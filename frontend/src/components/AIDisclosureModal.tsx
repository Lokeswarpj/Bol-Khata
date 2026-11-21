import React from 'react';
import { ShieldCheck, Info } from 'lucide-react';
import { GlowPill } from './GlowPill';
import { MonoLabel } from './MonoLabel';
import { useLedgerStore } from '../store/useLedgerStore';

export const AIDisclosureModal: React.FC = () => {
  const { settings, updateSettings } = useLedgerStore();

  if (settings.aiDisclosureDismissed) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-md">
      <div className="glass rounded-3xl p-6 sm:p-8 max-w-md w-full border border-white/20 shadow-2xl animate-in fade-in zoom-in-95 duration-300">
        <div className="flex items-center justify-between mb-4">
          <MonoLabel pulseDot variant="emerald">
            AI ASSISTANT DISCLOSURE
          </MonoLabel>
          <ShieldCheck className="w-5 h-5 text-emerald-400" />
        </div>

        <h3 className="font-serif text-2xl text-paper mb-3">
          Voice AI for your Kirana Khata
        </h3>

        <div className="space-y-3 text-sm text-white/70 mb-6 font-sans leading-relaxed">
          <p className="bg-white/[0.03] p-3 rounded-2xl border border-white/10 text-white/90">
            🎙️ <strong>Hinglish Notice:</strong> Yeh ek AI Voice Assistant hai jo aapki bolchal se khata likhta hai.
          </p>
          <div className="flex items-start gap-2 text-xs text-white/60">
            <Info className="w-4 h-4 text-emerald-400 shrink-0 mt-0.5" />
            <span>
              <strong>Privacy first:</strong> Audio is processed in real-time and never stored permanently. Only the parsed ledger entry is kept under DPDP guidelines.
            </span>
          </div>
        </div>

        <GlowPill
          variant="primary"
          className="w-full text-base font-medium"
          onClick={() => updateSettings({ aiDisclosureDismissed: true })}
        >
          Samajh Gaya (Continue)
        </GlowPill>
      </div>
    </div>
  );
};
