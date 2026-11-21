import React from 'react';
import { Sheet } from './Sheet';
import { MonoLabel } from './MonoLabel';
import { GlowPill } from './GlowPill';
import { useLedgerStore } from '../store/useLedgerStore';
import { CheckCircle2 } from 'lucide-react';

export const AnswerCard: React.FC = () => {
  const { answerCard, setAnswerCard } = useLedgerStore();

  if (!answerCard?.isOpen) return null;

  return (
    <Sheet
      isOpen={answerCard.isOpen}
      onClose={() => setAnswerCard(null)}
      title="Voice Query Answer"
    >
      <div className="space-y-6 text-center py-2">
        <MonoLabel variant="emerald" pulseDot>
          FINANCIAL QUERY RESOLVED
        </MonoLabel>

        <div>
          <h4 className="text-lg text-white/80 font-medium">
            {answerCard.customerName}
          </h4>
          <div className="font-serif text-[64px] font-normal tracking-tight text-white mt-1">
            ₹{answerCard.balance}
          </div>
          <span className="text-xs text-white/40">Total Outstanding Balance</span>
        </div>

        {answerCard.text && (
          <p className="text-sm text-white/70 bg-white/[0.03] p-3 rounded-2xl border border-white/10">
            "{answerCard.text}"
          </p>
        )}

        <GlowPill
          variant="primary"
          className="w-full flex items-center justify-center gap-2"
          onClick={() => setAnswerCard(null)}
        >
          <CheckCircle2 className="w-5 h-5 text-emerald-500" /> Done
        </GlowPill>
      </div>
    </Sheet>
  );
};
