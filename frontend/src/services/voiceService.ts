import { useLedgerStore } from '../store/useLedgerStore';
import type { VoiceServerResponse, LatencyRecord } from '../types';
import { getTranslation } from '../utils/i18n';

// Web Speech API interfaces for live transcription
interface IWindow extends Window {
  webkitSpeechRecognition?: any;
  SpeechRecognition?: any;
}

class VoiceService {
  private ws: WebSocket | null = null;
  private mediaRecorder: MediaRecorder | null = null;
  private audioChunks: Blob[] = [];
  private recognition: any = null;
  private liveTranscript: string = '';
  private isStarting: boolean = false;
  private shouldStopAfterStart: boolean = false;
  private t0: number = 0;
  private t1: number = 0;
  private t2: number = 0;
  private mimeType: string = 'audio/webm';
  private activeAudio: HTMLAudioElement | null = null;
  private recentSpokenTexts: string[] = [];
  private isEchoCooldown: boolean = false;
  private cooldownTimer: any = null;

  constructor() {
    this.initSpeechRecognition();
  }

  private initSpeechRecognition() {
    if (typeof window === 'undefined') return;
    const win = window as unknown as IWindow;
    const SpeechRec = win.SpeechRecognition || win.webkitSpeechRecognition;

    if (SpeechRec) {
      try {
        this.recognition = new SpeechRec();
        this.recognition.continuous = true;
        this.recognition.interimResults = true;
        this.recognition.maxAlternatives = 1;

        this.recognition.onresult = (event: any) => {
          if (this.isEchoCooldown || useLedgerStore.getState().voiceState === 'speaking') {
            return;
          }
          let interim = '';
          for (let i = event.resultIndex; i < event.results.length; ++i) {
            if (event.results[i].isFinal) {
              this.liveTranscript += event.results[i][0].transcript + ' ';
            } else {
              interim += event.results[i][0].transcript;
            }
          }
          const text = (this.liveTranscript + interim).trim();
          if (text) {
            const lower = text.toLowerCase();
            const isEcho = this.recentSpokenTexts.some(spoken => spoken.includes(lower) || (lower.length > 6 && spoken.length > 6 && lower.includes(spoken)));
            if (!isEcho) {
              useLedgerStore.getState().setHeardTranscript(text);
            }
          }
        };

        this.recognition.onerror = (e: any) => {
          console.warn('SpeechRecognition error:', e.error);
        };
      } catch (err) {
        console.warn('SpeechRecognition initialization error', err);
      }
    }
  }

  public connect() {
    if (this.ws && (this.ws.readyState === WebSocket.OPEN || this.ws.readyState === WebSocket.CONNECTING)) {
      return;
    }

    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const host = window.location.host;
    // Vite proxies /api with ws: true
    const wsUrl = `${protocol}//${host}/api/voice/ws`;

    try {
      this.ws = new WebSocket(wsUrl);

      this.ws.onopen = () => {
        useLedgerStore.getState().setOnline(true);
      };

      this.ws.onmessage = (event) => {
        try {
          const data: VoiceServerResponse = JSON.parse(event.data);
          this.handleServerMessage(data);
        } catch (e) {
          console.error('Error parsing WS message', e);
        }
      };

      this.ws.onclose = () => {
        setTimeout(() => this.connect(), 4000);
      };

      this.ws.onerror = (err) => {
        console.warn('Voice WebSocket error, will fallback to REST', err);
      };
    } catch (e) {
      console.warn('Failed to initialize WebSocket', e);
    }
  }

  public handleServerMessage(data: VoiceServerResponse) {
    const store = useLedgerStore.getState();

    if (data.type === 'disclosure') {
      if (!store.settings.aiDisclosureDismissed) {
        store.setSpokenResponse(data.text || 'AI Assistant bol raha hai. Sirf hisaab store hota hai.');
      }
      return;
    }

    if (data.type === 'response') {
      this.t1 = performance.now();
      const sttMs = Math.max(40, Math.round(this.t1 - this.t0 - 120));
      const nluMs = Math.max(10, Math.round(this.t1 - this.t0));

      if (data.transcript) {
        store.setHeardTranscript(data.transcript);
      }

      if (data.text) {
        store.setSpokenResponse(data.text);
      }

      // 1. Disambiguation
      if (data.needs_disambiguation && data.disambiguation_options && data.disambiguation_options.length > 0) {
        const normalizedOptions = data.disambiguation_options.map((opt: any, idx: number) => {
          if (typeof opt === 'string') {
            return {
              id: idx + 1,
              name: opt,
              hint: opt.includes(' - ') ? opt.split(' - ')[1] : undefined
            };
          }
          return opt;
        });

        store.setDisambiguation({
          isOpen: true,
          customerName: data.intent?.customer || 'Customer',
          options: normalizedOptions
        });
        store.setVoiceState('idle');
        return;
      }

      // 2. Correction with strike-through
      if ((data as any).correction_event) {
        const ce = (data as any).correction_event;
        store.applyCorrection(ce.new_amount, ce.customer);
      } else if (data.intent?.type === 'correction' && data.intent.amount) {
        store.applyCorrection(data.intent.amount, data.intent.customer);
      }

      // 3. Query Intent ("Ramesh ka total?")
      else if (data.intent?.type === 'query') {
        const balance = data.transaction?.amount ?? 0;
        store.setAnswerCard({
          isOpen: true,
          customerName: data.intent?.customer || 'Customer',
          balance: balance,
          text: data.text || `Balance: ₹${balance}`
        });
        store.setVoiceState('idle');
      }

      // 4. Conversational Chitchat & Greetings ("Namaste bhaiya, kaise ho?")
      else if (data.intent?.type === 'chitchat' || (data.intent as any)?.intent === 'chitchat') {
        store.setSpokenResponse(data.text || 'Namaste! BolKhata aapki dukaan ka voice ledger hai.');
        store.setVoiceState('idle');
      }

      // 5. Full Debt Settlement / Clearing ("Ramesh cleared his debt")
      else if (data.intent?.type === 'clear_debt' || (data.intent as any)?.intent === 'clear_debt') {
        const customerName = data.transaction?.customer_name || data.intent?.customer || 'Customer';
        const clearedAmount = data.transaction?.amount || 0;
        store.setPendingConfirmation({
          customer_name: customerName,
          type: 'payment',
          amount: clearedAmount,
          transaction_date: data.transaction?.date || new Date().toISOString().split('T')[0],
          heard_text: data.transcript || store.heardTranscript,
          confidence: 0.99,
          status: 'pending'
        });
        store.fetchInitialData();
      }

      // 6. Undo Intent
      else if (data.intent?.type === 'undo') {
        if (store.entries.length > 0) {
          const latest = store.entries[0];
          store.undoEntry(latest.id!, latest.remote_id);
        }
      }

      // 7. New Transaction (Credit / Payment)
      else if (data.transaction || (data.intent && (data.intent.type === 'credit' || data.intent.type === 'payment'))) {
        const direction = (data.transaction?.direction as any) || data.intent?.type || 'credit';
        const amount = data.transaction?.amount || data.intent?.amount || 0;
        const customerName = data.transaction?.customer_name || data.intent?.customer || 'Unknown';

        store.setPendingConfirmation({
          customer_name: customerName,
          type: direction,
          amount: amount,
          transaction_date: data.transaction?.date || new Date().toISOString().split('T')[0],
          heard_text: data.transcript || store.heardTranscript,
          confidence: data.intent?.confidence || 0.95,
          status: 'pending'
        });
      }

      // Audio Playback
      if (data.audio) {
        this.playBase64Audio(data.audio, data.text);
      } else if (data.text) {
        this.fallbackSpeechSynthesis(data.text);
      } else {
        store.setVoiceState('idle');
      }

      // Latency telemetry
      this.t2 = performance.now();
      const totalMs = Math.round(this.t2 - this.t0);
      const record: LatencyRecord = {
        t0_release: this.t0,
        t1_parsed: this.t1,
        t2_audio: this.t2,
        stt_ms: sttMs,
        nlu_ms: nluMs,
        tts_ms: Math.max(50, Math.round(this.t2 - this.t1)),
        total_ms: totalMs
      };
      store.setLastLatency(record);
    } else if (data.type === 'error') {
      store.setVoiceState('idle');
      const errorMsg = data.text || getTranslation('voiceNotUnderstood', store.settings.language);
      store.setHeardTranscript(`⚠️ ${errorMsg}`);
    }
  }

  private playBase64Audio(base64: string, spokenText?: string) {
    const store = useLedgerStore.getState();
    if (this.activeAudio) {
      try { this.activeAudio.pause(); } catch {}
      this.activeAudio = null;
    }
    if ('speechSynthesis' in window) window.speechSynthesis.cancel();
    if (spokenText) {
      this.recentSpokenTexts.push(spokenText.toLowerCase().trim());
      if (this.recentSpokenTexts.length > 15) this.recentSpokenTexts.shift();
    }
    try {
      this.activeAudio = new Audio(`data:audio/wav;base64,${base64}`);
      store.setVoiceState('speaking');
      this.isEchoCooldown = true;
      if (this.cooldownTimer) clearTimeout(this.cooldownTimer);
      if (this.recognition) {
        try { this.recognition.abort(); } catch {}
      }

      const handleEnded = () => {
        this.activeAudio = null;
        store.setVoiceState('idle');
        this.cooldownTimer = setTimeout(() => {
          this.isEchoCooldown = false;
          if (store.settings.handsFree) {
            this.startRecording();
          }
        }, 1100);
      };
      this.activeAudio.onended = handleEnded;
      this.activeAudio.onerror = handleEnded;
      this.activeAudio.play().catch(handleEnded);
    } catch {
      store.setVoiceState('idle');
      this.isEchoCooldown = false;
    }
  }

  private fallbackSpeechSynthesis(text: string) {
    const store = useLedgerStore.getState();
    if (!('speechSynthesis' in window)) {
      store.setVoiceState('idle');
      return;
    }
    window.speechSynthesis.cancel();
    this.recentSpokenTexts.push(text.toLowerCase().trim());
    if (this.recentSpokenTexts.length > 15) this.recentSpokenTexts.shift();
    const utterance = new SpeechSynthesisUtterance(text);
    const lang = store.settings.language === 'auto' ? 'hi-IN' : (store.settings.language || 'hi-IN');
    utterance.lang = lang;
    utterance.rate = 1.05;
    store.setVoiceState('speaking');
    this.isEchoCooldown = true;
    if (this.cooldownTimer) clearTimeout(this.cooldownTimer);
    if (this.recognition) {
      try { this.recognition.abort(); } catch {}
    }

    const handleEnded = () => {
      store.setVoiceState('idle');
      this.cooldownTimer = setTimeout(() => {
        this.isEchoCooldown = false;
        if (store.settings.handsFree) {
          this.startRecording();
        }
      }, 1100);
    };

    utterance.onend = handleEnded;
    utterance.onerror = handleEnded;
    window.speechSynthesis.speak(utterance);
  }

  public async startRecording(): Promise<boolean> {
    const store = useLedgerStore.getState();
    this.liveTranscript = '';
    this.audioChunks = [];
    this.isStarting = true;
    this.shouldStopAfterStart = false;

    // Provide instant feedback in UI
    store.setVoiceState('listening');
    store.setHeardTranscript(getTranslation('listeningFeedback', store.settings.language));

    // 1. Start live speech recognition if supported
    if (this.recognition) {
      try {
        const lang = store.settings.language || 'hi-IN';
        this.recognition.lang = lang;
        this.recognition.start();
      } catch {
        // Recognition might already be running
      }
    }

    // 2. Start hardware MediaRecorder
    try {
      if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
        store.setHeardTranscript('⚠️ Mic not supported on insecure HTTP. Please use localhost or HTTPS.');
        store.setVoiceState('idle');
        this.isStarting = false;
        return false;
      }

      const stream = await navigator.mediaDevices.getUserMedia({
        audio: {
          echoCancellation: true,
          noiseSuppression: true,
          autoGainControl: true,
        }
      });

      this.isStarting = false;

      // Detect MIME support
      if (typeof MediaRecorder !== 'undefined') {
        if (MediaRecorder.isTypeSupported('audio/webm;codecs=opus')) {
          this.mimeType = 'audio/webm;codecs=opus';
        } else if (MediaRecorder.isTypeSupported('audio/webm')) {
          this.mimeType = 'audio/webm';
        } else if (MediaRecorder.isTypeSupported('audio/mp4')) {
          this.mimeType = 'audio/mp4';
        } else {
          this.mimeType = '';
        }

        const options = this.mimeType ? { mimeType: this.mimeType } : undefined;
        this.mediaRecorder = new MediaRecorder(stream, options);

        this.mediaRecorder.ondataavailable = (event) => {
          if (event.data.size > 0) {
            this.audioChunks.push(event.data);
          }
        };

        this.mediaRecorder.start(100);

        // If user already released the button before getUserMedia resolved:
        if (this.shouldStopAfterStart) {
          this.stopRecording();
        }
      }
      return true;
    } catch (err: any) {
      console.error('Error starting recording:', err);
      this.isStarting = false;
      store.setVoiceState('idle');
      if (err.name === 'NotAllowedError' || err.name === 'PermissionDeniedError') {
        store.setHeardTranscript('⚠️ Microphone permission blocked. Click the lock icon in the browser URL bar to allow.');
      } else {
        store.setHeardTranscript(`⚠️ Mic error: ${err.message || 'Please check mic connection'}`);
      }
      return false;
    }
  }

  public stopRecording() {
    this.t0 = performance.now();
    const store = useLedgerStore.getState();

    // If startRecording is still requesting permission, flag to stop once opened
    if (this.isStarting) {
      this.shouldStopAfterStart = true;
      return;
    }

    store.setVoiceState('thinking');

    // Stop speech recognition
    if (this.recognition) {
      try {
        this.recognition.stop();
      } catch {
        // ignore
      }
    }

    // Check if we captured a transcript from live speech recognition
    const capturedText = (this.liveTranscript || store.heardTranscript || '').replace('Suniye, bol rahe hain...', '').trim();

    if (!this.mediaRecorder || this.mediaRecorder.state === 'inactive') {
      if (capturedText) {
        this.sendTextCommand(capturedText);
      } else {
        store.setVoiceState('idle');
      }
      return;
    }

    this.mediaRecorder.onstop = async () => {
      // If we have live transcript text, process it directly for sub-second speed!
      if (capturedText && capturedText.length > 2) {
        this.sendTextCommand(capturedText);
      } else {
        // Fall back to sending raw audio to Gnani STT
        const blobType = this.mimeType || 'audio/webm';
        const audioBlob = new Blob(this.audioChunks, { type: blobType });
        const reader = new FileReader();

        reader.onloadend = async () => {
          const base64Data = (reader.result as string).split(',')[1];
          if (!base64Data) {
            store.setVoiceState('idle');
            return;
          }

          if (this.ws && this.ws.readyState === WebSocket.OPEN) {
            this.ws.send(JSON.stringify({
              type: 'audio',
              data: base64Data,
              content_type: blobType.split(';')[0],
              language: store.settings.language === 'auto' ? undefined : store.settings.language
            }));
          } else {
            // REST upload fallback
            try {
              const formData = new FormData();
              formData.append('audio', audioBlob, 'speech.webm');
              if (store.settings.language && store.settings.language !== 'auto') {
                formData.append('language', store.settings.language);
              }

              const res = await fetch('/api/voice/process', {
                method: 'POST',
                body: formData
              });
              const json = await res.json();
              this.handleServerMessage({
                type: 'response',
                text: json.message,
                audio: json.audio_base64,
                transcript: json.message,
                intent: json.intent ? {
                  type: json.intent.intent,
                  customer: json.intent.customer_name,
                  amount: json.intent.amount,
                  direction: json.intent.direction,
                  confidence: json.intent.confidence
                } : undefined,
                transaction: json.transaction ? {
                  id: json.transaction.id,
                  customer_name: json.transaction.customer_name,
                  amount: json.transaction.amount,
                  direction: json.transaction.direction,
                  date: json.transaction.transaction_date
                } : undefined,
                needs_disambiguation: json.needs_disambiguation,
                disambiguation_options: json.disambiguation_options,
                correction_event: json.correction_event
              } as any);
            } catch (err) {
              console.error('Audio upload error:', err);
              store.setVoiceState('idle');
            }
          }
        };
        reader.readAsDataURL(audioBlob);
      }

      // Stop stream tracks to turn off mic indicator
      this.mediaRecorder?.stream.getTracks().forEach((track) => track.stop());
    };

    this.mediaRecorder.stop();
  }

  public async sendTextCommand(text: string) {
    this.t0 = performance.now();
    const store = useLedgerStore.getState();
    store.setVoiceState('thinking');
    store.setHeardTranscript(text);

    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify({
        type: 'text',
        data: text,
        language: store.settings.language === 'auto' ? undefined : store.settings.language
      }));
    } else {
      // REST fallback
      try {
        const res = await fetch('/api/voice/process-text', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            text,
            language: store.settings.language === 'auto' ? undefined : store.settings.language
          })
        });
        const json = await res.json();
        this.handleServerMessage({
          type: 'response',
          text: json.message,
          audio: json.audio_base64,
          transcript: text,
          intent: json.intent ? {
            type: json.intent.intent,
            customer: json.intent.customer_name,
            amount: json.intent.amount,
            direction: json.intent.direction,
            confidence: json.intent.confidence
          } : undefined,
          transaction: json.transaction ? {
            id: json.transaction.id,
            customer_name: json.transaction.customer_name,
            amount: json.transaction.amount,
            direction: json.transaction.direction,
            date: json.transaction.transaction_date
          } : undefined,
          needs_disambiguation: json.needs_disambiguation,
          disambiguation_options: json.disambiguation_options,
          correction_event: json.correction_event
        } as any);
      } catch (err) {
        console.error('REST process-text fallback error:', err);
        store.setVoiceState('idle');
      }
    }
  }
}

export const voiceService = new VoiceService();
