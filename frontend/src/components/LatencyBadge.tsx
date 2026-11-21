import React from 'react';
import { useLedgerStore } from '../store/useLedgerStore';
import { Zap } from 'lucide-react';

export const LatencyBadge: React.FC = () => {
  const { lastLatency, setDevPanelOpen } = useLedgerStore();

  if (!lastLatency) return null;

  return (
    <button
      onClick={() => setDevPanelOpen(true)}
      title="View latency breakdown in Dev Panel"
      className="fixed bottom-6 right-6 z-30 glass px-3 py-1.5 rounded-full border border-white/10 hover:border-emerald-500/50 flex items-center gap-1.5 text-[11px] font-mono text-emerald-400 transition-all active:scale-95 shadow-lg"
    >
      <Zap className="w-3.5 h-3.5 fill-current" />
      <span>{(lastLatency.total_ms / 1000).toFixed(2)}s</span>
    </button>
  );
};
