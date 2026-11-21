import React from 'react';
import { MonoLabel } from './MonoLabel';
import { RotateCcw } from 'lucide-react';
import type { Entry } from '../types';
import { useLedgerStore } from '../store/useLedgerStore';
import { getTranslation } from '../utils/i18n';

interface EntryCardProps {
  entry: Entry;
  onUndo?: () => void;
  shimmer?: boolean;
}

export const EntryCard: React.FC<EntryCardProps> = ({
  entry,
  onUndo,
  shimmer = false
}) => {
  const { settings } = useLedgerStore();
  const isUdhaar = entry.type === 'credit';
  const amountColor = isUdhaar ? 'text-rose-400' : 'text-emerald-400';
  const sign = isUdhaar ? '+' : '-';
  const labelText = isUdhaar
    ? getTranslation('udhaar', settings.language)
    : getTranslation('jama', settings.language);

  return (
    <div className={`glass rounded-2xl p-4 flex items-center justify-between transition-all duration-200 hover:border-white/20 ${shimmer ? 'shimmer border-emerald-500/40' : ''}`}>
      <div className="flex flex-col gap-1 min-w-0">
        <div className="flex items-center gap-2">
          <span className="font-medium text-white/90 text-base truncate">
            {entry.customer_name}
          </span>
          <MonoLabel variant={isUdhaar ? 'rose' : 'emerald'}>
            {labelText}
          </MonoLabel>
        </div>

        {entry.heard_text && (
          <p className="text-xs text-white/40 truncate max-w-[200px]">
            "{entry.heard_text}"
          </p>
        )}

        <span className="text-[11px] text-white/30">
          {entry.transaction_date || 'Today'}
        </span>
      </div>

      <div className="flex items-center gap-3">
        <div className="text-right">
          {entry.old_amount !== undefined && (
            <span className="line-through text-white/40 text-sm mr-2 font-mono">
              ₹{entry.old_amount}
            </span>
          )}
          <span className={`font-serif text-2xl font-normal tracking-tight ${amountColor}`}>
            {sign}₹{entry.amount}
          </span>
        </div>

        {onUndo && (
          <button
            onClick={onUndo}
            title="Undo entry"
            className="p-2 rounded-xl text-white/40 hover:text-white hover:bg-white/10 transition-colors"
          >
            <RotateCcw className="w-4 h-4" />
          </button>
        )}
      </div>
    </div>
  );
};
