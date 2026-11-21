import React, { useState } from 'react';
import { Sheet } from './Sheet';
import { GlowPill } from './GlowPill';
import { MonoLabel } from './MonoLabel';
import { useLedgerStore } from '../store/useLedgerStore';
import { Check, Edit3 } from 'lucide-react';

export const ConfirmationSheet: React.FC = () => {
  const { pendingConfirmation, confirmPendingEntry, cancelPendingEntry } = useLedgerStore();
  const [isEditing, setIsEditing] = useState(false);
  const [editedAmount, setEditedAmount] = useState(0);
  const [editedCustomer, setEditedCustomer] = useState('');

  if (!pendingConfirmation) return null;

  const isUdhaar = pendingConfirmation.type === 'credit';
  const amountColor = isUdhaar ? 'text-rose-400' : 'text-emerald-400';
  const labelText = isUdhaar ? 'UDHAAR (CREDIT)' : 'JAMA (PAYMENT)';

  const handleEditOpen = () => {
    setEditedAmount(pendingConfirmation.amount);
    setEditedCustomer(pendingConfirmation.customer_name);
    setIsEditing(true);
  };

  const handleEditSave = () => {
    useLedgerStore.getState().applyCorrection(editedAmount, editedCustomer);
    setIsEditing(false);
  };

  return (
    <Sheet isOpen={!!pendingConfirmation} onClose={cancelPendingEntry} title="Confirm Voice Entry">
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <MonoLabel variant={isUdhaar ? 'rose' : 'emerald'} pulseDot>
            {labelText}
          </MonoLabel>
          <span className="text-xs text-white/40">
            {pendingConfirmation.transaction_date || 'Today'}
          </span>
        </div>

        {isEditing ? (
          <div className="space-y-4">
            <div>
              <label className="text-xs text-white/50 block mb-1">Customer Name</label>
              <input
                type="text"
                value={editedCustomer}
                onChange={(e) => setEditedCustomer(e.target.value)}
                className="w-full bg-white/5 border border-white/20 rounded-2xl px-4 py-3 text-white focus:outline-none focus:border-emerald-500"
              />
            </div>
            <div>
              <label className="text-xs text-white/50 block mb-1">Amount (₹)</label>
              <input
                type="number"
                value={editedAmount}
                onChange={(e) => setEditedAmount(Number(e.target.value))}
                className="w-full bg-white/5 border border-white/20 rounded-2xl px-4 py-3 text-white focus:outline-none focus:border-emerald-500"
              />
            </div>
            <GlowPill variant="primary" className="w-full" onClick={handleEditSave}>
              Update Entry
            </GlowPill>
          </div>
        ) : (
          <>
            <div className="text-center py-2">
              <div className={`font-serif text-[56px] leading-tight font-normal tracking-tight ${amountColor}`}>
                ₹{pendingConfirmation.amount}
              </div>
              <h2 className="text-xl font-medium text-white/95 mt-1">
                {pendingConfirmation.customer_name}
              </h2>
            </div>

            {pendingConfirmation.heard_text && (
              <div className="bg-white/[0.03] p-3 rounded-2xl border border-white/10 text-center">
                <MonoLabel variant="muted" className="mb-1 block">
                  HEARD PHRASE
                </MonoLabel>
                <p className="text-sm text-white/70 italic">
                  "{pendingConfirmation.heard_text}"
                </p>
              </div>
            )}

            <div className="grid grid-cols-2 gap-3 pt-2">
              <GlowPill
                variant="ghost"
                onClick={handleEditOpen}
                className="flex items-center justify-center gap-2"
              >
                <Edit3 className="w-4 h-4" /> Edit
              </GlowPill>

              <GlowPill
                variant="primary"
                onClick={confirmPendingEntry}
                className="flex items-center justify-center gap-2"
              >
                <Check className="w-4 h-4" /> Confirm
              </GlowPill>
            </div>
          </>
        )}
      </div>
    </Sheet>
  );
};
