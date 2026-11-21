import React, { useEffect, useState } from 'react';
import { ArrowLeft, Bell, BellOff, Share2, Plus, Calendar } from 'lucide-react';
import { MonoLabel } from '../components/MonoLabel';
import { GlowPill } from '../components/GlowPill';
import { api } from '../services/api';
import { useLedgerStore } from '../store/useLedgerStore';
import type { Customer } from '../types';

interface CustomerDetailViewProps {
  customer: Customer;
  onBack: () => void;
}

export const CustomerDetailView: React.FC<CustomerDetailViewProps> = ({ customer, onBack }) => {
  const { setManualEntryOpen } = useLedgerStore();
  const [duesData, setDuesData] = useState<{
    balance: number;
    transactions: Array<{
      id: number;
      amount: number;
      direction: string;
      date: string;
      note?: string;
    }>;
  } | null>(null);

  const [optedIn, setOptedIn] = useState(customer.opted_in_reminders);
  const [reminderPreview, setReminderPreview] = useState<string | null>(null);
  const [loadingConsent, setLoadingConsent] = useState(false);

  useEffect(() => {
    // Fetch detailed dues & history
    api.getCustomerDues(customer.id)
      .then((data) => {
        setDuesData({
          balance: data.balance,
          transactions: data.transactions
        });
      })
      .catch((err) => console.error('Failed to load dues', err));
  }, [customer.id]);

  const handleToggleConsent = async () => {
    setLoadingConsent(true);
    try {
      const newStatus = !optedIn;
      await api.updateConsent(customer.id, newStatus);
      setOptedIn(newStatus);
      if (newStatus) {
        const rem = await api.getReminder(customer.id).catch(() => null);
        if (rem) setReminderPreview(rem.reminder_message);
      } else {
        setReminderPreview(null);
      }
    } catch (err) {
      console.error('Failed to update consent', err);
    } finally {
      setLoadingConsent(false);
    }
  };

  const balance = duesData ? duesData.balance : customer.balance;

  return (
    <div className="min-h-screen bg-ink text-paper pb-20">
      {/* Header - Frosted Glass */}
      <header className="sticky top-0 z-40 bg-black/20 backdrop-blur-xl border-b border-white/10 px-4 py-3 flex items-center justify-between shadow-[0_8px_32px_rgba(0,0,0,0.2)]">
        <button
          onClick={onBack}
          className="p-2 rounded-full hover:bg-white/10 text-white/70 hover:text-white transition-colors"
        >
          <ArrowLeft className="w-5 h-5" />
        </button>
        <h1 className="font-serif text-lg text-paper">{customer.name}</h1>
        <div className="w-8" />
      </header>

      {/* Main Container */}
      <main className="max-w-md mx-auto p-4 space-y-6">
        {/* Balance Card */}
        <div className="glass rounded-3xl p-6 text-center border border-white/10">
          <MonoLabel variant={balance > 0 ? 'rose' : 'emerald'} pulseDot>
            {balance > 0 ? 'TOTAL OUTSTANDING DUES' : 'ACCOUNT CLEAR'}
          </MonoLabel>

          <div className={`font-serif text-[56px] leading-tight font-normal tracking-tight mt-2 ${balance > 0 ? 'text-rose-400' : 'text-emerald-400'}`}>
            ₹{balance}
          </div>

          <div className="flex items-center justify-center gap-3 mt-4">
            <GlowPill
              variant="primary"
              onClick={() => setManualEntryOpen(true)}
              className="text-xs h-10 px-4"
            >
              <Plus className="w-4 h-4 mr-1" /> Add Entry
            </GlowPill>
          </div>
        </div>

        {/* DPDP Polite Reminder Section */}
        <div className="glass rounded-2xl p-4 border border-white/10 space-y-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              {optedIn ? (
                <Bell className="w-4 h-4 text-emerald-400" />
              ) : (
                <BellOff className="w-4 h-4 text-white/40" />
              )}
              <span className="font-medium text-sm text-white/90">
                Polite Payment Reminder
              </span>
            </div>

            <button
              onClick={handleToggleConsent}
              disabled={loadingConsent}
              className={`text-xs px-3 py-1 rounded-full border transition-all ${
                optedIn
                  ? 'border-emerald-500/50 bg-emerald-500/20 text-emerald-300'
                  : 'border-white/20 bg-white/5 text-white/50'
              }`}
            >
              {optedIn ? 'Opted In' : 'Opt In'}
            </button>
          </div>

          <p className="text-xs text-white/50">
            {optedIn
              ? 'Customer has given DPDP consent to receive respectful, polite payment reminders.'
              : 'Opt-in required before sending gentle reminders under DPDP compliance.'}
          </p>

          {optedIn && reminderPreview && (
            <div className="bg-white/[0.03] p-3 rounded-xl border border-white/10 text-xs text-white/80 font-mono">
              <span className="text-white/40 block text-[10px] mb-1">PREVIEW MESSAGE:</span>
              "{reminderPreview}"
            </div>
          )}
        </div>

        {/* Timeline of Entries */}
        <div className="space-y-3">
          <MonoLabel variant="muted">
            TRANSACTION HISTORY
          </MonoLabel>

          {duesData?.transactions && duesData.transactions.length > 0 ? (
            <div className="space-y-2">
              {duesData.transactions.map((txn) => {
                const isCredit = txn.direction === 'credit';
                return (
                  <div
                    key={txn.id}
                    className="p-3 rounded-2xl glass border border-white/5 flex items-center justify-between"
                  >
                    <div>
                      <div className="flex items-center gap-2">
                        <MonoLabel variant={isCredit ? 'rose' : 'emerald'}>
                          {isCredit ? 'UDHAAR' : 'JAMA'}
                        </MonoLabel>
                        <span className="text-xs text-white/40 flex items-center gap-1">
                          <Calendar className="w-3 h-3" /> {txn.date}
                        </span>
                      </div>
                      {txn.note && (
                        <p className="text-xs text-white/60 mt-0.5">{txn.note}</p>
                      )}
                    </div>

                    <div className={`font-serif text-lg ${isCredit ? 'text-rose-400' : 'text-emerald-400'}`}>
                      {isCredit ? '+' : '-'}₹{txn.amount}
                    </div>
                  </div>
                );
              })}
            </div>
          ) : (
            <p className="text-center py-6 text-xs text-white/30">
              No transactions recorded yet for this customer.
            </p>
          )}
        </div>
      </main>
    </div>
  );
};
