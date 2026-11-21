import React, { useState, useEffect } from 'react';
import { GlassCard } from './GlassCard';
import { MonoLabel } from './MonoLabel';
import { Activity, ShieldCheck, Zap, Volume2, Sparkles, Check, CheckCircle2 } from 'lucide-react';

interface HeroVoiceVisualizer3DProps {
  onOpenLedger: () => void;
}

export const HeroVoiceVisualizer3D: React.FC<HeroVoiceVisualizer3DProps> = ({ onOpenLedger }) => {
  const [activeScenario, setActiveScenario] = useState(0);
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [tilt, setTilt] = useState({ x: 0, y: 0 });

  const scenarios = [
    {
      voice: 'Ramesh ka 340 udhaar',
      action: 'UDHAAR RECORDED',
      type: 'credit' as const,
      customer: 'Ramesh Kumar',
      amount: '+₹340',
      totalBalance: '₹750',
      tag: 'Code-Mixed Vernacular',
      confidence: '98.8%'
    },
    {
      voice: 'Suresh cleared his full debt',
      action: 'DEBT CLEARED',
      type: 'clear' as const,
      customer: 'Suresh General Store',
      amount: '₹0.00',
      totalBalance: 'ACCOUNT CLEAR',
      tag: 'Zero Debt Settlement',
      confidence: '99.4%'
    },
    {
      voice: 'Namaste bhaiya, kaise ho?',
      action: 'CONVERSATIONAL CHIT-CHAT',
      type: 'chitchat' as const,
      customer: 'Assistant Response',
      amount: 'Live AI',
      totalBalance: '100% Encrypted & Safe',
      tag: 'Natural Indic AI',
      confidence: '100%'
    }
  ];

  // Auto-cycle scenarios every 5.5 seconds unless user is interacting
  useEffect(() => {
    const timer = setInterval(() => {
      setActiveScenario((prev) => (prev + 1) % scenarios.length);
      setIsSpeaking(true);
      setTimeout(() => setIsSpeaking(false), 2400);
    }, 5500);
    return () => clearInterval(timer);
  }, [scenarios.length]);

  const handleCardMouseMove = (e: React.MouseEvent<HTMLDivElement>) => {
    const rect = e.currentTarget.getBoundingClientRect();
    const x = ((e.clientX - rect.left) / rect.width - 0.5) * 16;
    const y = ((e.clientY - rect.top) / rect.height - 0.5) * -16;
    setTilt({ x, y });
  };

  const handleCardMouseLeave = () => {
    setTilt({ x: 0, y: 0 });
  };

  const current = scenarios[activeScenario];

  return (
    <div
      onMouseMove={handleCardMouseMove}
      onMouseLeave={handleCardMouseLeave}
      className="relative w-full max-w-lg mx-auto"
      style={{
        perspective: '1200px'
      }}
    >
      {/* 3D Tilting Stage */}
      <div
        className="space-y-4 transition-transform duration-300 ease-out"
        style={{
          transform: `rotateX(${tilt.y}deg) rotateY(${tilt.x}deg) translateZ(0)`
        }}
      >
        {/* Floating 3D Holographic Orbit Badge */}
        <div className="flex items-center justify-between px-2">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full glass border border-emerald-500/30 bg-emerald-950/40 text-emerald-300 text-xs shadow-[0_0_15px_rgba(16,185,129,0.25)]">
            <span className="w-2 h-2 rounded-full bg-emerald-400 animate-ping" />
            <span className="font-mono text-[11px] tracking-wide">3D LIVE KHATA STREAM</span>
          </div>

          <div className="flex items-center gap-1.5 px-2.5 py-1 rounded-full glass border border-white/10 text-[10px] text-white/50 font-mono">
            <ShieldCheck className="w-3.5 h-3.5 text-cyan-400" />
            <span>DPDP ACT COMPLIANT</span>
          </div>
        </div>

        {/* Central 3D Interactive Card */}
        <GlassCard
          shimmer
          spotlight
          className="p-6 border-emerald-500/40 shadow-[0_25px_60px_rgba(0,0,0,0.85)] relative overflow-hidden backdrop-blur-xl bg-black/60 group"
        >
          {/* Subtle Ambient Radial Glow */}
          <div className="absolute -top-16 -right-16 w-44 h-44 bg-emerald-500/20 rounded-full blur-3xl pointer-events-none group-hover:bg-emerald-500/30 transition-all duration-700" />
          <div className="absolute -bottom-16 -left-16 w-44 h-44 bg-cyan-500/15 rounded-full blur-3xl pointer-events-none" />

          {/* Card Top: Intent Pill & Model Tag */}
          <div className="flex items-center justify-between mb-4">
            <MonoLabel variant={current.type === 'credit' ? 'rose' : 'emerald'} pulseDot>
              {current.action}
            </MonoLabel>

            <span className="text-[10px] font-mono px-2 py-0.5 rounded-full bg-white/5 border border-white/10 text-white/60">
              {current.tag}
            </span>
          </div>

          {/* Dynamic Voice Spoken Utterance Banner */}
          <div className="p-3 rounded-2xl bg-white/[0.04] border border-white/10 mb-4 flex items-center justify-between">
            <div className="flex items-center gap-2.5 min-w-0">
              <div className="w-7 h-7 rounded-full bg-emerald-500/20 border border-emerald-500/40 flex items-center justify-center text-emerald-400 shrink-0 shadow-[0_0_10px_rgba(16,185,129,0.3)]">
                <Volume2 className="w-3.5 h-3.5 animate-pulse" />
              </div>
              <span className="font-serif italic text-white/90 text-sm truncate">
                "{current.voice}"
              </span>
            </div>

            {/* Live Audio Visualizer Equalizer Bars */}
            <div className="flex items-center gap-0.5 h-5 pl-2 shrink-0">
              {[8, 18, 12, 22, 14, 20, 10, 16].map((h, i) => (
                <span
                  key={i}
                  style={{
                    height: isSpeaking ? `${Math.min(22, h * (1 + Math.sin(i * 1.5)))}px` : `${Math.max(4, h * 0.55)}px`,
                    transition: 'height 0.15s ease'
                  }}
                  className="w-1 bg-gradient-to-t from-emerald-500 to-cyan-300 rounded-full"
                />
              ))}
            </div>
          </div>

          {/* Main Transaction Numbers & Customer */}
          <div className="flex items-end justify-between pt-1 pb-2">
            <div>
              <span className="text-[10px] text-white/40 font-mono uppercase tracking-wider block">Customer</span>
              <h3 className="font-medium text-xl text-white tracking-tight">{current.customer}</h3>
              <span className="text-xs text-white/50 block mt-0.5 font-mono">
                Balance: <strong className="text-white/80">{current.totalBalance}</strong>
              </span>
            </div>

            <div className="text-right">
              <span className="text-[10px] text-white/40 font-mono uppercase tracking-wider block">Logged Amount</span>
              <div
                className={`font-serif text-4xl sm:text-5xl font-normal tracking-tight ${
                  current.type === 'credit'
                    ? 'text-rose-400 drop-shadow-[0_0_15px_rgba(244,63,94,0.35)]'
                    : 'text-emerald-400 drop-shadow-[0_0_15px_rgba(16,185,129,0.35)]'
                }`}
              >
                {current.amount}
              </div>
            </div>
          </div>

          {/* Bottom Telemetry Bar */}
          <div className="mt-4 pt-3 border-t border-white/10 flex items-center justify-between text-[11px] font-mono text-white/50">
            <span className="flex items-center gap-1.5 text-emerald-400">
              <CheckCircle2 className="w-3.5 h-3.5" /> Parsed in 5.2ms
            </span>
            <span>Confidence: {current.confidence}</span>
          </div>
        </GlassCard>

        {/* Interactive Scenario Switcher Buttons */}
        <div className="flex items-center gap-2 justify-center pt-1">
          {scenarios.map((sc, idx) => (
            <button
              key={sc.voice}
              onClick={() => {
                setActiveScenario(idx);
                setIsSpeaking(true);
                setTimeout(() => setIsSpeaking(false), 2000);
              }}
              className={`px-3 py-1.5 rounded-xl text-xs font-mono transition-all border flex items-center gap-1.5 ${
                activeScenario === idx
                  ? 'bg-emerald-500/20 text-emerald-300 border-emerald-500/50 shadow-[0_0_15px_rgba(16,185,129,0.25)]'
                  : 'bg-white/5 text-white/50 border-white/10 hover:border-white/20 hover:text-white'
              }`}
            >
              <span className={`w-1.5 h-1.5 rounded-full ${activeScenario === idx ? 'bg-emerald-400' : 'bg-white/30'}`} />
              <span>{idx === 0 ? 'Udhaar' : idx === 1 ? 'Debt Clear' : 'Chit-Chat'}</span>
            </button>
          ))}
        </div>

        {/* Two Mini 3D Companion Metric Cards */}
        <div className="grid grid-cols-2 gap-3 pt-1">
          {/* Card 1: 85dB Noise Filter */}
          <GlassCard className="p-3.5 border-white/10 flex items-center gap-3">
            <div className="w-9 h-9 rounded-xl bg-cyan-500/10 border border-cyan-500/30 flex items-center justify-center text-cyan-400 shrink-0">
              <Zap className="w-4 h-4 animate-pulse" />
            </div>
            <div className="min-w-0">
              <span className="text-[10px] text-white/40 font-mono uppercase block">Filter</span>
              <span className="text-xs text-white font-medium block truncate">85 dB Bazaar VAD</span>
            </div>
          </GlassCard>

          {/* Card 2: 4 Indian Languages */}
          <GlassCard className="p-3.5 border-white/10 flex items-center gap-3 cursor-pointer hover:border-emerald-500/40" onClick={onOpenLedger}>
            <div className="w-9 h-9 rounded-xl bg-emerald-500/10 border border-emerald-500/30 flex items-center justify-center text-emerald-400 shrink-0">
              <Sparkles className="w-4 h-4" />
            </div>
            <div className="min-w-0">
              <span className="text-[10px] text-white/40 font-mono uppercase block">Vernacular</span>
              <span className="text-xs text-white font-medium block truncate">4 Languages</span>
            </div>
          </GlassCard>
        </div>
      </div>
    </div>
  );
};
