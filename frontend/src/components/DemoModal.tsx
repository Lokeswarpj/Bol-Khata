import React, { useState, useEffect } from 'react';
import { Sheet } from './Sheet';
import { MonoLabel } from './MonoLabel';
import { GlowPill } from './GlowPill';
import {
  Volume2,
  CheckCircle2,
  ArrowRight,
  ArrowLeft,
  Play,
  Pause,
  RotateCcw,
  Sparkles,
  Zap,
  ShieldCheck,
  Smartphone
} from 'lucide-react';

interface DemoModalProps {
  isOpen: boolean;
  onClose: () => void;
  onLaunchApp: () => void;
}

export const DemoModal: React.FC<DemoModalProps> = ({ isOpen, onClose, onLaunchApp }) => {
  const [currentStep, setCurrentStep] = useState(0);
  const [isPlaying, setIsPlaying] = useState(false);

  const steps = [
    {
      step: 1,
      tag: 'VOICE ENTRY',
      title: 'Speak the Sale Naturally',
      voice: 'Ramesh ka 340 udhaar',
      desc: 'Shopkeeper speaks code-mixed Hindi & numerals hands-free. The system processes noise-resilient audio and extracts intent, customer, and amount in sub-second time.',
      uiVisual: {
        badge: 'CONFIRMED ENTRY',
        badgeColor: 'text-rose-400',
        customer: 'Ramesh Kumar',
        amount: '+₹340',
        amountLabel: 'Udhaar Logged',
        meta: 'STT: 98.8% Confidence • Kannada/Telugu/Hindi ready'
      }
    },
    {
      step: 2,
      tag: '15S STRIKE-THROUGH',
      title: 'Instant Voice Correction',
      voice: 'Nahi, 430',
      desc: 'Made a mistake? Speak the correction within 15 seconds. BolKhata amends the previous transaction in-place without creating a duplicate record, rendering a visual strike-through.',
      uiVisual: {
        badge: 'CORRECTION APPLIED',
        badgeColor: 'text-amber-400',
        customer: 'Ramesh Kumar',
        strikeAmount: '₹340',
        amount: '₹430',
        amountLabel: 'Corrected Amount',
        meta: 'Strike-through applied • Balance adjusted to ₹680'
      }
    },
    {
      step: 3,
      tag: 'SMART DISAMBIGUATION',
      title: 'Location-Aware Disambiguation',
      voice: 'Ramesh',
      desc: 'Multiple customers named Ramesh? BolKhata asks a spoken prompt and renders visual selection chips with real shopkeeper landmarks ("Kirana Lane" vs "Milk Dairy").',
      uiVisual: {
        badge: 'DISAMBIGUATION REQUIRED',
        badgeColor: 'text-cyan-400',
        options: [
          { name: 'Ramesh Kumar', hint: 'Kirana Lane', dues: '₹750' },
          { name: 'Ramesh Patel', hint: 'Milk Dairy', dues: '₹200' }
        ],
        meta: 'Spoken hint: "Kaunse Ramesh? Kirana Lane wale ya Milk Dairy wale?"'
      }
    },
    {
      step: 4,
      tag: 'TEMPORAL NLU',
      title: 'Relative Date Parsing',
      voice: 'Ramesh ne 200 diya kal',
      desc: 'Resolves relative temporal dates like "kal" (yesterday), "parso" (day before), or "aaj subah" into verified calendar dates without manual calendar pickers.',
      uiVisual: {
        badge: 'PAYMENT RECORDED',
        badgeColor: 'text-emerald-400',
        customer: 'Ramesh Kumar',
        amount: '-₹200',
        amountLabel: 'Jama (Payment)',
        meta: 'Transaction Date resolved to yesterday'
      }
    },
    {
      step: 5,
      tag: 'SUB-2S QUERY & SETTLE',
      title: 'Voice Query & Debt Settlement',
      voice: 'Suresh cleared his full debt',
      desc: 'Ask customer balance verbally ("Ramesh ka total?") or clear debt in one sentence. BolKhata resets customer balance to zero and speaks back spoken confirmation.',
      uiVisual: {
        badge: 'FULL SETTLEMENT',
        badgeColor: 'text-emerald-400',
        customer: 'Suresh General Store',
        amount: '₹0.00',
        amountLabel: 'Balance Cleared',
        meta: 'Latency: 5.2ms • 100% Zero Debt Cleared'
      }
    }
  ];

  // Autoplay step sequencer
  useEffect(() => {
    let timer: any;
    if (isPlaying && isOpen) {
      timer = setInterval(() => {
        setCurrentStep((prev) => {
          if (prev >= steps.length - 1) {
            setIsPlaying(false);
            return prev;
          }
          return prev + 1;
        });
      }, 4200);
    }
    return () => clearInterval(timer);
  }, [isPlaying, isOpen, steps.length]);

  if (!isOpen) return null;

  const current = steps[currentStep];

  return (
    <Sheet
      isOpen={isOpen}
      onClose={onClose}
      title="5-Step Interactive Product Demonstration"
    >
      <div className="space-y-6 text-sm text-paper max-h-[80vh] overflow-y-auto pr-1">
        {/* Step Indicator Pills */}
        <div className="flex items-center justify-between gap-1 border-b border-white/10 pb-4">
          {steps.map((st, idx) => (
            <button
              key={st.step}
              onClick={() => {
                setCurrentStep(idx);
                setIsPlaying(false);
              }}
              className={`flex-1 py-1.5 px-2 rounded-xl text-xs font-mono transition-all text-center border ${
                currentStep === idx
                  ? 'bg-emerald-500/20 text-emerald-300 font-bold border-emerald-500/50 shadow-[0_0_15px_rgba(16,185,129,0.3)]'
                  : 'bg-white/5 text-white/40 border-white/5 hover:border-white/20'
              }`}
            >
              Step {st.step}
            </button>
          ))}
        </div>

        {/* Current Step Showcase Card */}
        <div className="glass rounded-3xl p-6 border border-emerald-500/30 shadow-[0_20px_50px_rgba(0,0,0,0.7)] relative overflow-hidden space-y-4">
          {/* Header Tag & Step */}
          <div className="flex items-center justify-between">
            <MonoLabel variant="emerald" pulseDot>
              {current.tag}
            </MonoLabel>
            <span className="text-xs text-white/40 font-mono">
              STEP {current.step} OF 5
            </span>
          </div>

          <div>
            <h3 className="font-serif text-2xl text-white font-normal">
              {current.title}
            </h3>
            <p className="text-xs text-white/60 leading-relaxed mt-1">
              {current.desc}
            </p>
          </div>

          {/* Simulated Speech Bubble */}
          <div className="p-4 rounded-2xl bg-white/[0.04] border border-white/10 flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 rounded-full bg-emerald-500/20 text-emerald-400 flex items-center justify-center shrink-0">
                <Volume2 className="w-4 h-4 animate-pulse" />
              </div>
              <div>
                <span className="text-[10px] text-white/40 font-mono uppercase block">Shopkeeper Spoke:</span>
                <span className="font-serif italic text-white text-base">"{current.voice}"</span>
              </div>
            </div>

            {/* Simulated Audio Spectrum Waves */}
            <div className="flex items-center gap-1 h-6">
              {[10, 22, 16, 26, 14, 20, 12, 18].map((h, i) => (
                <span
                  key={i}
                  style={{ height: `${h}px` }}
                  className="w-1 bg-gradient-to-t from-emerald-500 to-cyan-300 rounded-full animate-pulse"
                />
              ))}
            </div>
          </div>

          {/* Visual UI Simulation Container */}
          <div className="p-4 rounded-2xl bg-black/40 border border-white/10 space-y-3">
            <div className="flex items-center justify-between">
              <span className={`text-[11px] font-mono font-medium ${current.uiVisual.badgeColor}`}>
                ● {current.uiVisual.badge}
              </span>
              <span className="text-[10px] text-white/30 font-mono">BOLKHATA ENGINE</span>
            </div>

            {/* Disambiguation options visual */}
            {current.uiVisual.options ? (
              <div className="space-y-2 pt-1">
                {current.uiVisual.options.map((opt) => (
                  <div
                    key={opt.name}
                    className="p-3 rounded-xl bg-white/5 border border-white/10 flex items-center justify-between hover:border-emerald-500/40 transition-colors"
                  >
                    <div>
                      <div className="font-medium text-white text-sm">{opt.name}</div>
                      <div className="text-xs text-white/50">{opt.hint}</div>
                    </div>
                    <div className="text-right">
                      <div className="text-xs text-rose-400 font-serif">{opt.dues}</div>
                      <div className="text-[9px] text-white/30 font-mono">Dues</div>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              /* Transaction amount visual */
              <div className="flex items-center justify-between pt-1">
                <div>
                  <div className="text-base font-medium text-white">{current.uiVisual.customer}</div>
                  <div className="text-xs text-white/40">{current.uiVisual.amountLabel}</div>
                </div>

                <div className="text-right">
                  {current.uiVisual.strikeAmount && (
                    <span className="text-sm font-serif line-through text-white/40 mr-2">
                      {current.uiVisual.strikeAmount}
                    </span>
                  )}
                  <span className={`font-serif text-3xl font-normal ${current.uiVisual.badgeColor}`}>
                    {current.uiVisual.amount}
                  </span>
                </div>
              </div>
            )}

            <div className="text-[10px] text-white/40 font-mono border-t border-white/5 pt-2 flex items-center gap-1.5">
              <Sparkles className="w-3 h-3 text-emerald-400" />
              <span>{current.uiVisual.meta}</span>
            </div>
          </div>
        </div>

        {/* Step Navigation & Controls */}
        <div className="flex items-center justify-between gap-3 pt-2">
          <button
            onClick={() => {
              setCurrentStep((prev) => Math.max(0, prev - 1));
              setIsPlaying(false);
            }}
            disabled={currentStep === 0}
            className="px-4 py-2.5 rounded-xl glass border border-white/10 text-white/70 hover:text-white disabled:opacity-30 disabled:pointer-events-none flex items-center gap-1 text-xs font-mono"
          >
            <ArrowLeft className="w-3.5 h-3.5" /> Back
          </button>

          <button
            onClick={() => setIsPlaying(!isPlaying)}
            className={`px-4 py-2.5 rounded-xl border flex items-center gap-2 text-xs font-mono transition-all ${
              isPlaying
                ? 'bg-amber-500/20 text-amber-300 border-amber-500/40'
                : 'glass border-white/10 text-white hover:border-emerald-500/40'
            }`}
          >
            {isPlaying ? (
              <>
                <Pause className="w-3.5 h-3.5 fill-current" /> Pause Autoplay
              </>
            ) : (
              <>
                <Play className="w-3.5 h-3.5 fill-current" /> Autoplay (All 5)
              </>
            )}
          </button>

          {currentStep < steps.length - 1 ? (
            <button
              onClick={() => {
                setCurrentStep((prev) => prev + 1);
                setIsPlaying(false);
              }}
              className="px-4 py-2.5 rounded-xl bg-white text-ink hover:bg-emerald-400 transition-colors flex items-center gap-1 text-xs font-mono font-medium"
            >
              Next Step <ArrowRight className="w-3.5 h-3.5" />
            </button>
          ) : (
            <button
              onClick={() => {
                onClose();
                onLaunchApp();
              }}
              className="px-4 py-2.5 rounded-xl bg-emerald-500 hover:bg-emerald-400 text-ink font-bold transition-all shadow-[0_0_20px_rgba(16,185,129,0.4)] flex items-center gap-1.5 text-xs font-mono"
            >
              Launch Live App <ArrowRight className="w-3.5 h-3.5" />
            </button>
          )}
        </div>

        {/* Quick Launch CTA */}
        <div className="pt-2">
          <GlowPill
            variant="primary"
            onClick={() => {
              onClose();
              onLaunchApp();
            }}
            className="w-full text-xs h-11"
          >
            Open Live Voice Ledger App <ArrowRight className="w-4 h-4 ml-1" />
          </GlowPill>
        </div>
      </div>
    </Sheet>
  );
};
