import React, { useState } from 'react';
import { Sheet } from './Sheet';
import { GlowPill } from './GlowPill';
import { MonoLabel } from './MonoLabel';
import { useLedgerStore } from '../store/useLedgerStore';
import type { TransactionDirection } from '../types';

export const ManualEntryModal: React.FC = () => {
  const { isManualEntryOpen, setManualEntryOpen, addManualEntry } = useLedgerStore();
  const [customer, setCustomer] = useState('');
  const [amount, setAmount] = useState('');
  const [direction, setDirection] = useState<TransactionDirection>('credit');
  const [note, setNote] = useState('');
  const [loading, setLoading] = useState(false);

  if (!isManualEntryOpen) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!customer.trim() || !amount) return;

    setLoading(true);
    try {
      await addManualEntry({
        customer_name: customer.trim(),
        amount: Number(amount),
        direction,
        note: note.trim() || undefined
      });
      setCustomer('');
      setAmount('');
      setNote('');
      setManualEntryOpen(false);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Sheet
      isOpen={isManualEntryOpen}
      onClose={() => setManualEntryOpen(false)}
      title="Manual Khata Entry"
    >
      <form onSubmit={handleSubmit} className="space-y-4">
        {/* Udhaar / Jama Selector */}
        <div className="grid grid-cols-2 gap-2">
          <button
            type="button"
            onClick={() => setDirection('credit')}
            className={`py-3 rounded-2xl font-medium text-sm transition-all border ${
              direction === 'credit'
                ? 'bg-rose-500/20 border-rose-500/50 text-rose-300'
                : 'glass border-white/10 text-white/60'
            }`}
          >
            Udhaar (+ Dues)
          </button>
          <button
            type="button"
            onClick={() => setDirection('payment')}
            className={`py-3 rounded-2xl font-medium text-sm transition-all border ${
              direction === 'payment'
                ? 'bg-emerald-500/20 border-emerald-500/50 text-emerald-300'
                : 'glass border-white/10 text-white/60'
            }`}
          >
            Jama (- Received)
          </button>
        </div>

        <div>
          <label className="text-xs text-white/50 block mb-1">Customer Name</label>
          <input
            type="text"
            required
            placeholder="e.g. Ramesh Kumar"
            value={customer}
            onChange={(e) => setCustomer(e.target.value)}
            className="w-full bg-white/5 border border-white/20 rounded-2xl px-4 py-3 text-white placeholder-white/20 focus:outline-none focus:border-emerald-500"
          />
        </div>

        <div>
          <label className="text-xs text-white/50 block mb-1">Amount (₹)</label>
          <input
            type="number"
            required
            placeholder="340"
            value={amount}
            onChange={(e) => setAmount(e.target.value)}
            className="w-full bg-white/5 border border-white/20 rounded-2xl px-4 py-3 text-white placeholder-white/20 focus:outline-none focus:border-emerald-500 font-serif text-lg"
          />
        </div>

        <div>
          <label className="text-xs text-white/50 block mb-1">Optional Note / Items</label>
          <input
            type="text"
            placeholder="e.g. Atta, Tel, Sugar"
            value={note}
            onChange={(e) => setNote(e.target.value)}
            className="w-full bg-white/5 border border-white/20 rounded-2xl px-4 py-3 text-white placeholder-white/20 focus:outline-none focus:border-emerald-500 text-sm"
          />
        </div>

        <GlowPill
          variant="primary"
          type="submit"
          className="w-full mt-4"
          disabled={loading || !customer || !amount}
        >
          {loading ? 'Saving Entry...' : 'Save to Ledger'}
        </GlowPill>
      </form>
    </Sheet>
  );
};
