import React, { useEffect, useState, useRef } from 'react';
import { MonoLabel } from '../components/MonoLabel';
import { GlowPill } from '../components/GlowPill';
import { GlassCard } from '../components/GlassCard';
import { LinkUnderline } from '../components/LinkUnderline';
import { Reveal } from '../components/Reveal';
import { CountUp } from '../components/CountUp';
import { BolKhataLogo } from '../components/BolKhataLogo';
import { VoiceKhataBackground3D } from '../components/VoiceKhataBackground3D';
import { HeroVoiceVisualizer3D } from '../components/HeroVoiceVisualizer3D';
import { DemoModal } from '../components/DemoModal';
import { useLedgerStore } from '../store/useLedgerStore';
import {
  Terminal,
  Volume2,
  Cpu,
  Layers,
  Sparkles,
  ShieldCheck,
  Smartphone,
  CheckCircle2,
  ArrowRight,
  TrendingUp,
  Activity,
  Play
} from 'lucide-react';

interface LandingPageProps {
  onOpenLedger: () => void;
  onOpenDemo: () => void;
}

export const LandingPage: React.FC<LandingPageProps> = ({ onOpenLedger, onOpenDemo }) => {
  const [scrolled, setScrolled] = useState(false);
  const [isDemoModalOpen, setIsDemoModalOpen] = useState(false);
  const { benchmarkMetrics } = useLedgerStore();
  const heroRef = useRef<HTMLDivElement>(null);
  const [mousePos, setMousePos] = useState({ x: 0, y: 0 });

  useEffect(() => {
    const handleScroll = () => {
      setScrolled(window.scrollY > 30);
    };
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  const handleMouseMove = (e: React.MouseEvent) => {
    if (window.matchMedia('(hover:hover) and (pointer:fine)').matches) {
      const { clientX, clientY } = e;
      const x = (clientX / window.innerWidth - 0.5) * 20;
      const y = (clientY / window.innerHeight - 0.5) * 20;
      setMousePos({ x, y });
    }
  };

  const featureCards = [
    {
      icon: Cpu,
      title: 'Code-Mixed Numerals',
      description: 'Accurately parses mixed Hindi, English & fractions like "dedh sau", "chaalis", and "three-forty" even under intense 85dB bazaar noise.'
    },
    {
      icon: Layers,
      title: 'Smart In-Place Corrections',
      description: 'Saying "nahi, 430" dynamically replaces previous erroneous entries in place without leaving duplicate ledger entries.'
    },
    {
      icon: Volume2,
      title: 'Spoken Disambiguation',
      description: 'When multiple customers share a common name like "Ramesh", BolKhata prompts with visual options and spoken location hints.'
    },
    {
      icon: Sparkles,
      title: 'Fast Spoken Answers',
      description: 'Instant answers to financial queries ("Aaj kitna udhaar gaya?", "Ramesh ka total?") synthesized and spoken in under 2 seconds.'
    },
    {
      icon: ShieldCheck,
      title: 'Responsible AI & DPDP',
      description: 'DPDP compliant. Voice audio is purged immediately post-parse; only ledger records persist with opt-in polite reminders.'
    },
    {
      icon: Smartphone,
      title: 'Built for 2 GB Phones',
      description: 'Adaptive dual-tier design automatically enables Lite mode for sub-₹8,000 Android phones, eliminating GPU blur & lag.'
    }
  ];

  return (
    <div className="min-h-screen bg-transparent text-paper selection:bg-emerald-500/20 selection:text-emerald-400 relative overflow-x-hidden">
      {/* 3D Voice AI & Khata Perspective Hologram Background */}
      <VoiceKhataBackground3D />

      {/* Fixed Frosted Glass Navbar */}
      <nav
        className={`fixed top-0 inset-x-0 z-50 transition-all duration-300 ${
          scrolled
            ? 'bg-black/20 backdrop-blur-xl border-b border-white/10 py-3.5 shadow-[0_8px_32px_rgba(0,0,0,0.25)]'
            : 'bg-transparent py-5'
        }`}
      >
        <div className="max-w-6xl mx-auto px-6 flex items-center justify-between">
          {/* Left: BolKhata Emblem Logo */}
          <div
            className="flex items-center gap-3 cursor-pointer group"
            onClick={() => window.scrollTo({ top: 0, behavior: 'smooth' })}
          >
            <BolKhataLogo size="md" />
            <div>
              <span className="font-serif text-xl tracking-tight font-medium text-white block leading-none">
                BolKhata
              </span>
              <MonoLabel variant="emerald" className="text-[9px]">
                PS2 / VOICE KHATA
              </MonoLabel>
            </div>
          </div>

          {/* Center Links with emerald underline */}
          <div className="hidden md:flex items-center gap-8 text-sm">
            <LinkUnderline href="#features">Features</LinkUnderline>
            <LinkUnderline href="#benchmarks">Benchmarks</LinkUnderline>
            <LinkUnderline href="#how-it-works">How It Works</LinkUnderline>
          </div>

          {/* Right CTA */}
          <div>
            <GlowPill
              variant="pulse"
              onClick={onOpenLedger}
              className="text-xs sm:text-sm h-11 px-5"
            >
              Open Ledger
            </GlowPill>
          </div>
        </div>
      </nav>

      {/* Hero Section (100vh split) */}
      <section
        ref={heroRef}
        onMouseMove={handleMouseMove}
        className="min-h-screen flex items-center pt-24 pb-12 px-6 max-w-6xl mx-auto relative"
      >
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-12 items-center w-full">
          {/* Hero Left */}
          <div className="lg:col-span-7 space-y-6">
            <Reveal delayMs={0}>
              <div className="inline-flex items-center gap-2 glass px-3.5 py-1.5 rounded-full border border-white/10">
                <MonoLabel pulseDot variant="emerald">
                  PS2 / VOICE KHATA / LIVE
                </MonoLabel>
              </div>
            </Reveal>

            <Reveal delayMs={80}>
              <h1 className="font-serif text-[clamp(44px,7vw,92px)] leading-[0.92] tracking-tighter text-white font-normal">
                Speak the sale. <br />
                The <span className="italic text-emerald-400">khata</span> writes itself.
              </h1>
            </Reveal>

            <Reveal delayMs={160}>
              <p className="text-base sm:text-lg text-white/60 font-sans max-w-xl leading-relaxed font-light">
                A hands-free, code-mixed voice ledger engineered for Indian Kirana store owners.
                Processes noisy vernacular numbers, corrects mistakes on the fly, and balances books in under 2 seconds.
              </p>
            </Reveal>

            <Reveal delayMs={240}>
              <div className="flex flex-wrap items-center gap-4 pt-2">
                <GlowPill variant="primary" onClick={onOpenLedger} className="gap-2">
                  Try the Live Ledger <ArrowRight className="w-4 h-4 text-emerald-600" />
                </GlowPill>

                <GlowPill variant="ghost" onClick={() => setIsDemoModalOpen(true)} className="gap-2">
                  <Play className="w-4 h-4 fill-current ml-0.5" /> See the 5-step demo
                </GlowPill>
              </div>
            </Reveal>

            <Reveal delayMs={320}>
              <div className="flex items-center gap-6 pt-4 text-xs text-white/40 font-mono">
                <span>⚡ SUB-2S LATENCY</span>
                <span>🔒 DPDP ACT COMPLIANT</span>
                <span>📱 2GB PHONE READY</span>
              </div>
            </Reveal>
          </div>

          {/* Hero Right - 3D Interactive Voice AI & Holographic Khata Showcase */}
          <div className="lg:col-span-5 relative">
            <HeroVoiceVisualizer3D onOpenLedger={onOpenLedger} />
          </div>
        </div>
      </section>

      {/* 3-Column Feature Grid */}
      <section id="features" className="py-24 px-6 max-w-6xl mx-auto border-t border-white/5">
        <div className="text-center max-w-2xl mx-auto mb-16 space-y-3">
          <MonoLabel variant="emerald" pulseDot>
            ENGINEERED CAPABILITIES
          </MonoLabel>
          <h2 className="font-serif text-4xl sm:text-5xl tracking-tight text-white font-normal">
            Precision voice intelligence for retail counters.
          </h2>
          <p className="text-white/60 text-sm font-light">
            Designed specifically for shop environments where background noise is loud, dialects are fluid, and transactions happen fast.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {featureCards.map((feat, index) => {
            const Icon = feat.icon;
            return (
              <Reveal key={feat.title} delayMs={index * 60}>
                <GlassCard
                  spotlight
                  shimmer
                  className="p-8 sm:p-10 rounded-3xl h-full flex flex-col justify-between group hover:border-white/20 transition-all duration-300"
                >
                  <div className="space-y-4">
                    <div className="w-12 h-12 rounded-2xl bg-white/5 border border-white/10 flex items-center justify-center text-white/80 group-hover:rotate-12 group-hover:bg-emerald-500 group-hover:text-ink transition-all duration-500">
                      <Icon className="w-6 h-6" />
                    </div>
                    <h3 className="font-serif text-2xl text-white font-normal">
                      {feat.title}
                    </h3>
                    <p className="text-sm text-white/55 font-light leading-relaxed">
                      {feat.description}
                    </p>
                  </div>

                  <div className="pt-6 border-t border-white/5 mt-6 flex items-center justify-between text-xs font-mono text-white/40 group-hover:text-emerald-400 transition-colors">
                    <span>CAPABILITY 0{index + 1}</span>
                    <ArrowRight className="w-3.5 h-3.5 transform group-hover:translate-x-1 transition-transform" />
                  </div>
                </GlassCard>
              </Reveal>
            );
          })}
        </div>
      </section>

      {/* 5-Step Interactive Walkthrough Section */}
      <section id="how-it-works" className="py-24 px-6 max-w-6xl mx-auto border-t border-white/5 relative">
        <div className="text-center max-w-2xl mx-auto mb-16 space-y-3">
          <MonoLabel variant="emerald" pulseDot>
            STEP-BY-STEP WORKFLOW
          </MonoLabel>
          <h2 className="font-serif text-4xl sm:text-5xl tracking-tight text-white font-normal">
            How BolKhata Works
          </h2>
          <p className="text-white/60 text-sm font-light">
            Designed for busy retail counters: 5 natural conversational steps from initial utterance to zero paper.
          </p>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4">
          {[
            {
              step: '01',
              title: 'Speak the Sale',
              phrase: '"Ramesh ka 340 udhaar"',
              desc: 'Code-mixed Indic speech is parsed in real time, identifying customer and amount.',
              badge: 'VOICE STT'
            },
            {
              step: '02',
              title: 'Spoken Feedback',
              phrase: '"Theek hai, 340 udhaar likha"',
              desc: 'Speaks immediate confirmation back so the shopkeeper never needs to look down.',
              badge: 'AUDIO CONFIRM'
            },
            {
              step: '03',
              title: '15s Correction',
              phrase: '"Nahi, 430"',
              desc: 'Mistakes amended in-place with animated strike-through without duplicate records.',
              badge: 'STRIKE-THROUGH'
            },
            {
              step: '04',
              title: 'Disambiguation',
              phrase: '"Kirana Lane wale"',
              desc: 'Location-aware prompts clarify identical names instantly.',
              badge: 'SMART RESOLVE'
            },
            {
              step: '05',
              title: 'Query & Settle',
              phrase: '"Suresh debt clear"',
              desc: 'Sub-2s balance retrieval and single-sentence zero debt settlement.',
              badge: 'SETTLED'
            }
          ].map((item) => (
            <GlassCard key={item.step} className="p-5 border-white/10 flex flex-col justify-between hover:border-emerald-500/40 transition-all group">
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <span className="font-mono text-emerald-400 font-bold text-sm">{item.step}</span>
                  <span className="text-[9px] font-mono px-2 py-0.5 rounded-full bg-white/5 text-white/50 border border-white/10">{item.badge}</span>
                </div>
                <h4 className="font-serif text-lg text-white font-normal group-hover:text-emerald-300 transition-colors">{item.title}</h4>
                <div className="p-2 rounded-xl bg-white/[0.03] border border-white/5 text-xs text-white/80 font-serif italic">
                  {item.phrase}
                </div>
                <p className="text-xs text-white/50 leading-relaxed font-light">{item.desc}</p>
              </div>
            </GlassCard>
          ))}
        </div>

        <div className="text-center mt-10">
          <GlowPill variant="primary" onClick={() => setIsDemoModalOpen(true)} className="gap-2">
            <Play className="w-4 h-4 fill-current ml-0.5" /> Launch Interactive 5-Step Demo Viewer
          </GlowPill>
        </div>
      </section>

      {/* Benchmark Table (Honesty Rule Adherent) */}
      <section id="benchmarks" className="py-24 px-6 max-w-5xl mx-auto border-t border-white/5">
        <div className="space-y-4 mb-12">
          <MonoLabel variant="emerald" pulseDot>
            VERIFIED TELEMETRY
          </MonoLabel>
          <h2 className="font-serif text-3xl sm:text-4xl text-white font-normal">
            Performance Benchmarks
          </h2>
          <p className="text-white/55 text-sm font-light max-w-xl">
            Honesty guarantee: Metrics display real recorded data produced by the developer telemetry harness. Until tested, values remain pending.
          </p>
        </div>

        <div className="glass rounded-3xl border border-white/10 overflow-hidden">
          {/* Table Header */}
          <div className="grid grid-cols-12 px-6 py-4 border-b border-white/10 bg-white/[0.02] text-[10px] font-mono uppercase tracking-[0.2em] text-white/50">
            <div className="col-span-5">Metric</div>
            <div className="col-span-2 text-emerald-400">Target</div>
            <div className="col-span-3">Measured</div>
            <div className="col-span-2 text-right">Status</div>
          </div>

          {/* Table Rows */}
          <div className="divide-y divide-white/[0.05]">
            {benchmarkMetrics.map((row) => (
              <div
                key={row.key}
                className="grid grid-cols-12 px-6 py-4 items-center text-sm font-sans hover:bg-white/[0.02] transition-colors"
              >
                <div className="col-span-5 font-medium text-white/80">
                  {row.metric}
                </div>
                <div className="col-span-2 font-mono text-xs text-emerald-400 font-semibold">
                  {row.target}
                </div>
                <div className="col-span-3 font-mono text-xs text-white/70">
                  {typeof row.measured === 'number' ? (
                    <CountUp end={row.measured} />
                  ) : (
                    row.measured
                  )}
                </div>
                <div className="col-span-2 flex justify-end">
                  {row.status === 'MET' ? (
                    <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-emerald-500/10 border border-emerald-500/30 text-[10px] font-mono text-emerald-300">
                      <CheckCircle2 className="w-3 h-3 text-emerald-400" /> MET
                    </span>
                  ) : (
                    <span className="text-[11px] font-mono text-white/30">
                      PENDING
                    </span>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Centered Massive CTA Section */}
      <section className="py-28 px-6 text-center max-w-4xl mx-auto border-t border-white/5 relative">
        <Reveal delayMs={0}>
          <h2 className="font-serif text-5xl sm:text-7xl font-normal tracking-tight text-white mb-6">
            Ready to voice-enable <br />
            <span className="gradient-text font-serif italic">your retail counter?</span>
          </h2>
        </Reveal>

        <Reveal delayMs={100}>
          <p className="text-white/60 text-base max-w-lg mx-auto mb-8 font-light">
            Zero paper friction. Instant spoken confirmation. Works in low connectivity.
          </p>
        </Reveal>

        <Reveal delayMs={180}>
          <GlowPill
            variant="pulse"
            onClick={onOpenLedger}
            className="text-base px-8 h-14 font-medium"
          >
            Launch BolKhata App <ArrowRight className="w-5 h-5 ml-2" />
          </GlowPill>
        </Reveal>
      </section>

      {/* Footer */}
      <footer className="border-t border-white/5 py-8 px-6 text-center text-xs text-white/40 font-mono">
        BOLKHATA • TEAM DRONA • SJCIT • PS2 VOICE KHATA
      </footer>

      {/* 5-Step Interactive Walkthrough Modal */}
      <DemoModal
        isOpen={isDemoModalOpen}
        onClose={() => setIsDemoModalOpen(false)}
        onLaunchApp={onOpenLedger}
      />
    </div>
  );
};
