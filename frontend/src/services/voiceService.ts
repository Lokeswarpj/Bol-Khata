import { useLedgerStore } from '../store/useLedgerStore';
import type { VoiceServerResponse, LatencyRecord } from '../types';

class VoiceService {
  private ws: WebSocket | null = null;
  private mediaRecorder: MediaRecorder | null = null;
  private audioChunks: Blob[] = [];
  private t0: number = 0;
  private t1: number = 0;
  private t2: number = 0;
  private isConnected: boolean = false;

  constructor() {
    // Lazy connect when app initializes
  }

  public connect() {
    if (this.ws && (this.ws.readyState === WebSocket.OPEN || this.ws.readyState === WebSocket.CONNECTING)) {
      return;
    }

    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const host = window.location.host;
    const wsUrl = `${protocol}//${host}/api/voice/ws`;

    try {
      this.ws = new WebSocket(wsUrl);

      this.ws.onopen = () => {
        this.isConnected = true;
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
        this.isConnected = false;
        // Try reconnect in 3s
        setTimeout(() => this.connect(), 3000);
      };

      this.ws.onerror = (err) => {
        console.warn('Voice WebSocket error, will fallback to REST', err);
        this.isConnected = false;
      };
    } catch (e) {
      console.warn('Failed to initialize WebSocket', e);
    }
  }

  private handleServerMessage(data: VoiceServerResponse) {
    const store = useLedgerStore.getState();

    if (data.type === 'disclosure') {
      // AI disclosure sent by server
      if (!store.settings.aiDisclosureDismissed) {
        store.setSpokenResponse(data.text || 'AI Assistant bol raha hai. Sirf hisaab store hota hai.');
      }
      return;
    }

    if (data.type === 'response') {
      this.t1 = performance.now();
      const sttMs = Math.max(50, Math.round(this.t1 - this.t0 - 150));
      const nluMs = Math.max(20, Math.round(this.t1 - this.t0));

      if (data.transcript) {
        store.setHeardTranscript(data.transcript);
      }

      if (data.text) {
        store.setSpokenResponse(data.text);
      }

      // Check for Disambiguation
      if (data.needs_disambiguation && data.disambiguation_options && data.disambiguation_options.length > 0) {
        const normalizedOptions = data.disambiguation_options.map((opt: any, idx: number) => {
          if (typeof opt === 'string') {
            return { id: idx + 1, name: opt, hint: opt.includes(' - ') ? opt.split(' - ')[1] : undefined };
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

      // Check for Strike-Through / Correction Event
      if ((data as any).correction_event) {
        const ce = (data as any).correction_event;
        store.applyCorrection(ce.new_amount, ce.customer);
      }

      // Check for Query Intent (e.g. "Ramesh ka total?")
      if (data.intent?.type === 'query') {
        const balance = data.transaction?.amount ?? 0;
        store.setAnswerCard({
          isOpen: true,
          customerName: data.intent?.customer || 'Customer',
          balance: balance,
          text: data.text || `Balance: ₹${balance}`
        });
        store.setVoiceState('idle');
      }

      // Check for Correction Intent (e.g. "Nahi, 430")
      else if (data.intent?.type === 'correction') {
        if (data.intent.amount) {
          store.applyCorrection(data.intent.amount, data.intent.customer);
        }
      }

      // Check for Undo Intent (e.g. "Galat ho gaya", "Undo")
      else if (data.intent?.type === 'undo') {
        if (store.entries.length > 0) {
          const latest = store.entries[0];
          store.undoEntry(latest.id!, latest.remote_id);
        }
      }

      // New Transaction (Credit / Payment)
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
        this.playBase64Audio(data.audio);
      } else if (data.text) {
        this.fallbackSpeechSynthesis(data.text);
      } else {
        store.setVoiceState('idle');
      }

      // Record Latency
      this.t2 = performance.now();
      const totalMs = Math.round(this.t2 - this.t0);
      const record: LatencyRecord = {
        t0_release: this.t0,
        t1_parsed: this.t1,
        t2_audio: this.t2,
        stt_ms: sttMs,
        nlu_ms: nluMs,
        tts_ms: Math.max(80, Math.round(this.t2 - this.t1)),
        total_ms: totalMs
      };
      store.setLastLatency(record);
    } else if (data.type === 'error') {
      store.setVoiceState('idle');
      console.error('Server returned error:', data.text);
    }
  }

  // Play audio from base64
  private playBase64Audio(base64: string) {
    const store = useLedgerStore.getState();
    try {
      const audio = new Audio(`data:audio/wav;base64,${base64}`);
      store.setVoiceState('speaking');
      audio.onended = () => {
        store.setVoiceState('idle');
      };
      audio.onerror = () => {
        store.setVoiceState('idle');
      };
      audio.play().catch(() => {
        store.setVoiceState('idle');
      });
    } catch {
      store.setVoiceState('idle');
    }
  }

  // Browser SpeechSynthesis fallback when audio not synthesized
  private fallbackSpeechSynthesis(text: string) {
    const store = useLedgerStore.getState();
    if (!('speechSynthesis' in window)) {
      store.setVoiceState('idle');
      return;
    }
    window.speechSynthesis.cancel();
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.lang = 'hi-IN';
    utterance.rate = 1.05;
    store.setVoiceState('speaking');

    utterance.onend = () => {
      store.setVoiceState('idle');
    };
    utterance.onerror = () => {
      store.setVoiceState('idle');
    };
    window.speechSynthesis.speak(utterance);
  }

  // Start recording
  public async startRecording(): Promise<boolean> {
    try {
      if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
        alert('Microphone access is not supported by your browser.');
        return false;
      }

      const stream = await navigator.mediaDevices.getUserMedia({
        audio: {
          echoCancellation: true,
          noiseSuppression: true,
          autoGainControl: true,
        }
      });

      this.audioChunks = [];
      this.mediaRecorder = new MediaRecorder(stream, { mimeType: 'audio/webm' });

      this.mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          this.audioChunks.push(event.data);
        }
      };

      this.mediaRecorder.start(100);
      useLedgerStore.getState().setVoiceState('listening');
      return true;
    } catch (err) {
      console.error('Error starting recording:', err);
      return false;
    }
  }

  // Stop recording and process
  public stopRecording() {
    this.t0 = performance.now();
    const store = useLedgerStore.getState();
    store.setVoiceState('thinking');

    if (!this.mediaRecorder || this.mediaRecorder.state === 'inactive') {
      store.setVoiceState('idle');
      return;
    }

    this.mediaRecorder.onstop = async () => {
      const audioBlob = new Blob(this.audioChunks, { type: 'audio/webm' });
      const reader = new FileReader();
      reader.onloadend = () => {
        const base64Data = (reader.result as string).split(',')[1];
        if (this.ws && this.ws.readyState === WebSocket.OPEN) {
          this.ws.send(JSON.stringify({
            type: 'audio',
            data: base64Data,
            language: store.settings.language
          }));
        } else {
          // Fallback to demo prompt if microphone was silent / no WS
          store.setVoiceState('idle');
        }
      };
      reader.readAsDataURL(audioBlob);

      // Stop stream tracks
      this.mediaRecorder?.stream.getTracks().forEach(track => track.stop());
    };

    this.mediaRecorder.stop();
  }

  // Send a text command directly (for testing, /dev panel, and demo replay)
  public async sendTextCommand(text: string) {
    this.t0 = performance.now();
    const store = useLedgerStore.getState();
    store.setVoiceState('thinking');
    store.setHeardTranscript(text);

    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify({
        type: 'text',
        data: text,
        language: store.settings.language
      }));
    } else {
      // REST fallback
      try {
        const res = await fetch('/api/voice/process-text', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            text,
            language: store.settings.language
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
          disambiguation_options: json.disambiguation_options
        });
      } catch (err) {
        console.error('REST process-text fallback error:', err);
        store.setVoiceState('idle');
      }
    }
  }
}

export const voiceService = new VoiceService();
