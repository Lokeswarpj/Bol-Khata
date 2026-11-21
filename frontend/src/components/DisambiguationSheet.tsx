import React from 'react';
import { Sheet } from './Sheet';
import { MonoLabel } from './MonoLabel';
import { useLedgerStore } from '../store/useLedgerStore';
import { Users } from 'lucide-react';

export const DisambiguationSheet: React.FC = () => {
  const { disambiguation, setDisambiguation, setPendingConfirmation } = useLedgerStore();

  if (!disambiguation?.isOpen) return null;

  const handleSelect = (option: { id?: number; name: string; hint?: string; balance?: number }) => {
    // Set pending confirmation for the selected customer
    setPendingConfirmation({
      customer_id: option.id,
      customer_name: option.name,
      type: 'credit',
      amount: 340, // default / last amount
      transaction_date: new Date().toISOString().split('T')[0],
      heard_text: `Selected ${option.name}`,
      status: 'pending'
    });
    setDisambiguation(null);
  };

  return (
    <Sheet
      isOpen={disambiguation.isOpen}
      onClose={() => setDisambiguation(null)}
      title="Multiple Customers Found"
    >
      <div className="space-y-4">
        <MonoLabel pulseDot variant="emerald">
          SELECT CUSTOMER (OR SPEAK)
        </MonoLabel>

        <p className="text-sm text-white/60">
          We found multiple customers matching "{disambiguation.customerName}". Please choose:
        </p>

        <div className="space-y-2">
          {disambiguation.options.map((opt, idx) => (
            <button
              key={opt.id ?? idx}
              onClick={() => handleSelect(opt)}
              className="w-full text-left p-4 rounded-2xl glass border border-white/10 hover:border-emerald-500/50 hover:bg-white/[0.06] transition-all flex items-center justify-between group active:scale-[0.99]"
            >
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-full bg-white/5 flex items-center justify-center text-white/60 group-hover:text-emerald-400">
                  <Users className="w-5 h-5" />
                </div>
                <div>
                  <div className="font-medium text-white text-base">
                    {opt.name}
                  </div>
                  {opt.hint && (
                    <div className="text-xs text-white/40">
                      {opt.hint}
                    </div>
                  )}
                </div>
              </div>

              {opt.balance !== undefined && (
                <div className="text-right">
                  <div className="text-xs text-white/40">Balance</div>
                  <div className="font-serif text-paper">
                    ₹{opt.balance}
                  </div>
                </div>
              )}
            </button>
          ))}
        </div>
      </div>
    </Sheet>
  );
};
