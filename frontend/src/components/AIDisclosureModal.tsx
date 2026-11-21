import React, { useState, useEffect } from 'react';
import { ShieldCheck, Mic, Sparkles, X, Volume2, ArrowRight, Lock, CheckCircle2 } from 'lucide-react';
import { GlowPill } from './GlowPill';
import { MonoLabel } from './MonoLabel';
import { BolKhataLogo } from './BolKhataLogo';
import { useLedgerStore } from '../store/useLedgerStore';

export const AIDisclosureModal: React.FC = () => {
  const { settings, updateSettings } = useLedgerStore();
  const [waveHeights, setWaveHeights] = useState<number[]>([40, 70, 30, 85, 60, 95, 45, 65, 35, 80, 50, 90]);

  useEffect(() => {
    const interval = setInterval(() => {
      setWaveHeights(prev =>
        prev.map(() => Math.floor(Math.random() * 65) + 25)
      );
    }, 180);
    return () => clearInterval(interval);
  }, []);

  if (settings.aiDisclosureDismissed) return null;

  const handleDismiss = () => {
    updateSettings({ aiDisclosureDismissed: true });
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/45 backdrop-blur-md transition-all">
      {/* Ambient Radial Aura for Depth */}
      <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_center,rgba(16,185,129,0.18),rgba(6,182,212,0.08),transparent_70%)] pointer-events-none" />

      {/* Main Glass Modal Card */}
      <div className="relative w-full max-w-lg bg-[#080d12]/92 backdrop-blur-2xl rounded-3xl border border-white/20 shadow-[0_24px_80px_rgba(0,0,0,0.85),0_0_60px_rgba(16,185,129,0.18)] p-6 sm:p-8 animate-in fade-in zoom-in-95 duration-300 overflow-hidden">
        {/* Top Iridescent Glow Line */}
        <div className="absolute top-0 inset-x-0 h-px bg-gradient-to-r from-transparent via-emerald-400 to-transparent" />
        <div className="absolute -top-24 left-1/2 -translate-x-1/2 w-48 h-48 bg-emerald-500/20 rounded-full blur-3xl pointer-events-none" />

        {/* Modal Top Bar */}
        <div className="flex items-center justify-between mb-4 relative z-10">
          <div className="flex items-center gap-2">
            <BolKhataLogo size="sm" />
            <MonoLabel pulseDot variant="emerald" className="tracking-widest text-[10px]">
              VOICE AI • ONBOARDING
            </MonoLabel>
          </div>

          <div className="flex items-center gap-2">
            <span className="flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[10px] font-mono bg-emerald-500/10 border border-emerald-500/30 text-emerald-300">
              <ShieldCheck className="w-3.5 h-3.5 text-emerald-400" />
              DPDP 2023
            </span>
            <button
              onClick={handleDismiss}
              className="p-1.5 rounded-full text-white/50 hover:text-white hover:bg-white/10 transition-colors"
              title="Close"
            >
              <X className="w-4 h-4" />
            </button>
          </div>
        </div>

        {/* Typography Headline */}
        <div className="mb-5 relative z-10">
          <h2 className="font-serif text-2xl sm:text-3xl text-white font-normal tracking-tight leading-snug">
            Speak the sale. <br />
            The <span className="italic font-normal text-emerald-400">khata</span> writes itself.
          </h2>
          <p className="text-xs sm:text-sm text-white/70 mt-1.5 font-sans leading-relaxed">
            Hinglish Voice Assistant engineered for Kirana retail counters. Bina hath lagaye rozaana hisab-kitab.
          </p>
        </div>

        {/* Live Audio Visualizer Demonstration Card */}
        <div className="bg-white/[0.04] rounded-2xl p-3.5 border border-white/10 mb-5 relative overflow-hidden group">
          <div className="flex items-center justify-between mb-2">
            <span className="text-[10px] font-mono text-emerald-300/90 flex items-center gap-1.5 uppercase tracking-wider">
              <Volume2 className="w-3.5 h-3.5 text-emerald-400" />
              Live Vernacular Speech Recognition
            </span>
            <span className="text-[9px] font-mono text-white/40">Gnani.ai 16kHz</span>
          </div>

          {/* Equalizer Wave + Spoken Example */}
          <div className="flex items-center gap-3 bg-black/40 p-2.5 rounded-xl border border-white/5">
            {/* Waveform Bars */}
            <div className="flex items-center gap-1 h-6 shrink-0 px-1">
              {waveHeights.map((h, i) => (
                <div
                  key={i}
                  className="w-1 bg-gradient-to-t from-emerald-500 to-cyan-400 rounded-full transition-all duration-150"
                  style={{ height: `${h}%` }}
                />
              ))}
            </div>

            {/* Transcript text */}
            <div className="min-w-0 flex-1">
              <div className="text-xs text-white/95 italic font-sans font-medium truncate">
                "Ramesh ka 340 udhaar likho"
              </div>
              <div className="text-[10px] text-emerald-400 font-mono flex items-center gap-1 mt-0.5">
                <CheckCircle2 className="w-3 h-3 text-emerald-400" />
                Parsed: Ramesh Kumar • +₹340 Udhaar (Debt)
              </div>
            </div>
          </div>
        </div>

        {/* 3 Value Pillars */}
        <div className="space-y-2.5 text-xs text-white/75 mb-6 relative z-10">
          <div className="flex items-start gap-2.5 p-2 rounded-xl bg-white/[0.02] border border-white/5">
            <Mic className="w-4 h-4 text-cyan-400 shrink-0 mt-0.5" />
            <div>
              <span className="font-semibold text-white">4 Languages & Code-Mixed Hinglish: </span>
              Hindi, Hinglish, Kannada, and Telugu with 85dB noisy market voice isolation.
            </div>
          </div>

          <div className="flex items-start gap-2.5 p-2 rounded-xl bg-white/[0.02] border border-white/5">
            <Lock className="w-4 h-4 text-emerald-400 shrink-0 mt-0.5" />
            <div>
              <span className="font-semibold text-white">Privacy First (DPDP Compliant): </span>
              Audio is processed in temporary RAM and discarded immediately. No raw voice recordings are stored.
            </div>
          </div>

          <div className="flex items-start gap-2.5 p-2 rounded-xl bg-white/[0.02] border border-white/5">
            <Sparkles className="w-4 h-4 text-amber-400 shrink-0 mt-0.5" />
            <div>
              <span className="font-semibold text-white">Multi-Intent Ledger Intelligence: </span>
              Handles Udhaar, Jama, Full Debt Clearing (<em>"pura hisab clear"</em>), and store chit-chat in &lt;2s.
            </div>
          </div>
        </div>

        {/* Action Button */}
        <div className="space-y-2 relative z-10">
          <GlowPill
            variant="primary"
            className="w-full text-base font-semibold py-3.5 shadow-[0_0_24px_rgba(16,185,129,0.35)] flex items-center justify-center gap-2 hover:scale-[1.01] transition-transform"
            onClick={handleDismiss}
          >
            <span>Samajh Gaya • Open Ledger</span>
            <ArrowRight className="w-4 h-4" />
          </GlowPill>

          <p className="text-center text-[11px] text-white/40 font-mono">
            Press & hold Spacebar or Mic button to talk anytime
          </p>
        </div>
      </div>
    </div>
  );
};
