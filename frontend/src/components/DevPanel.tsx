import React from 'react';
import { Sheet } from './Sheet';
import { MonoLabel } from './MonoLabel';
import { GlowPill } from './GlowPill';
import { useLedgerStore } from '../store/useLedgerStore';
import { voiceService } from '../services/voiceService';
import { Play, Activity, Clock, CheckCircle2 } from 'lucide-react';

export const DevPanel: React.FC = () => {
  const { isDevPanelOpen, setDevPanelOpen, lastLatency, benchmarkMetrics } = useLedgerStore();

  if (!isDevPanelOpen) return null;

  // The 5 official demonstration test clips from the spec
  const demoSteps = [
    {
      step: 1,
      title: 'Initial Entry',
      phrase: 'Ramesh ka 340 udhaar',
      desc: 'Parses code-mixed Hindi digits & sets credit'
    },
    {
      step: 2,
      title: 'In-Place Correction',
      phrase: 'Nahi, 430',
      desc: 'Dynamically updates preceding entry without duplicate'
    },
    {
      step: 3,
      title: 'Disambiguation',
      phrase: 'Ramesh',
      desc: 'Ambiguous name triggers spoken clarification sheet'
    },
    {
      step: 4,
      title: 'Relative Date Payment',
      phrase: 'Ramesh ne 200 diya kal',
      desc: 'Parses payment & resolves "kal" to yesterday'
    },
    {
      step: 5,
      title: 'Sub-2s Query Answer',
      phrase: 'Ramesh ka total?',
      desc: 'Rapid voice balance lookup with audio answer'
    },
    {
      step: 6,
      title: 'Kannada Regional Voice',
      phrase: 'ರಮೇಶ್ ಗೆ 340 ಸಾಲ',
      desc: 'Native Kannada credit ledger entry'
    },
    {
      step: 7,
      title: 'Telugu Regional Voice',
      phrase: 'రమేష్ కి 340 అప్పు',
      desc: 'Native Telugu credit ledger entry'
    }
  ];

  const handleRunClip = (phrase: string) => {
    voiceService.sendTextCommand(phrase);
    setDevPanelOpen(false);
  };

  return (
    <Sheet
      isOpen={isDevPanelOpen}
      onClose={() => setDevPanelOpen(false)}
      title="Developer & Demo Control Panel"
    >
      <div className="space-y-6 text-sm text-paper max-h-[75vh] overflow-y-auto pr-1">
        {/* Latency Telemetry */}
        <div className="glass rounded-2xl p-4 border border-white/10">
          <div className="flex items-center justify-between mb-3">
            <MonoLabel variant="emerald" pulseDot>
              REAL-TIME LATENCY (TELEMETRY)
            </MonoLabel>
            <Clock className="w-4 h-4 text-emerald-400" />
          </div>

          {lastLatency ? (
            <div className="grid grid-cols-4 gap-2 text-center">
              <div className="bg-white/5 p-2 rounded-xl">
                <div className="text-[10px] text-white/40">STT</div>
                <div className="font-mono text-emerald-400 font-bold">{lastLatency.stt_ms}ms</div>
              </div>
              <div className="bg-white/5 p-2 rounded-xl">
                <div className="text-[10px] text-white/40">NLU/DB</div>
                <div className="font-mono text-emerald-400 font-bold">{lastLatency.nlu_ms}ms</div>
              </div>
              <div className="bg-white/5 p-2 rounded-xl">
                <div className="text-[10px] text-white/40">TTS</div>
                <div className="font-mono text-emerald-400 font-bold">{lastLatency.tts_ms}ms</div>
              </div>
              <div className="bg-emerald-500/10 border border-emerald-500/30 p-2 rounded-xl">
                <div className="text-[10px] text-emerald-300">Total</div>
                <div className="font-mono text-emerald-300 font-bold">{(lastLatency.total_ms / 1000).toFixed(2)}s</div>
              </div>
            </div>
          ) : (
            <p className="text-xs text-white/40 italic">
              Speak or run a demo step below to record live pipeline latency.
            </p>
          )}
        </div>

        {/* 5-Step Demo Utterance Replay */}
        <div>
          <MonoLabel variant="muted" className="mb-2 block">
            5-STEP HACKATHON DEMO REPLAY
          </MonoLabel>

          <div className="space-y-2">
            {demoSteps.map((demo) => (
              <button
                key={demo.step}
                onClick={() => handleRunClip(demo.phrase)}
                className="w-full text-left p-3 rounded-2xl glass border border-white/10 hover:border-emerald-500/40 hover:bg-white/[0.05] transition-all flex items-center justify-between group"
              >
                <div>
                  <div className="flex items-center gap-2">
                    <span className="w-5 h-5 rounded-full bg-white/10 text-[10px] flex items-center justify-center font-mono">
                      {demo.step}
                    </span>
                    <span className="font-medium text-white text-sm">
                      "{demo.phrase}"
                    </span>
                  </div>
                  <p className="text-[11px] text-white/40 pl-7 mt-0.5">
                    {demo.desc}
                  </p>
                </div>

                <div className="w-8 h-8 rounded-full bg-white/5 flex items-center justify-center text-white/40 group-hover:bg-emerald-500 group-hover:text-ink transition-colors">
                  <Play className="w-3.5 h-3.5 fill-current ml-0.5" />
                </div>
              </button>
            ))}
          </div>
        </div>

        {/* Current Benchmark Table Status */}
        <div className="glass rounded-2xl p-4 border border-white/10">
          <MonoLabel variant="emerald" className="mb-2 block">
            BENCHMARK TABLE SYNC
          </MonoLabel>
          <div className="space-y-1.5 text-xs">
            {benchmarkMetrics.map((b) => (
              <div key={b.key} className="flex items-center justify-between py-1 border-b border-white/5">
                <span className="text-white/60">{b.metric}</span>
                <span className={`font-mono font-medium ${b.status === 'MET' ? 'text-emerald-400' : 'text-white/30'}`}>
                  {b.measured}
                </span>
              </div>
            ))}
          </div>
        </div>

        <GlowPill
          variant="ghost"
          className="w-full"
          onClick={() => setDevPanelOpen(false)}
        >
          Close Panel
        </GlowPill>
      </div>
    </Sheet>
  );
};
