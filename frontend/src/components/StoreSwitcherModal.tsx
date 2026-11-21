import React, { useEffect } from 'react';
import { Sheet } from './Sheet';
import { MonoLabel } from './MonoLabel';
import { Store, Check, RefreshCw, UserCheck, Shield } from 'lucide-react';
import { useLedgerStore } from '../store/useLedgerStore';

export const StoreSwitcherModal: React.FC = () => {
  const {
    isStoreSwitcherOpen,
    setStoreSwitcherOpen,
    ownerProfile,
    allOwners,
    switchStore,
    resetTodayPayments,
    fetchOwnerData
  } = useLedgerStore();

  useEffect(() => {
    if (isStoreSwitcherOpen) {
      fetchOwnerData();
    }
  }, [isStoreSwitcherOpen, fetchOwnerData]);

  if (!isStoreSwitcherOpen) return null;

  return (
    <Sheet
      isOpen={isStoreSwitcherOpen}
      onClose={() => setStoreSwitcherOpen(false)}
      title="Store Merchant & Account Switcher"
    >
      <div className="space-y-5 text-sm text-paper">
        {/* Active Store Badge */}
        <div className="p-4 rounded-2xl bg-emerald-500/10 border border-emerald-500/30 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-emerald-500/20 flex items-center justify-center text-emerald-400">
              <Store className="w-5 h-5" />
            </div>
            <div>
              <div className="font-semibold text-white text-base">
                {ownerProfile?.store_name || 'Sri Balaji Kirana'}
              </div>
              <div className="text-xs text-white/60 flex items-center gap-1.5 mt-0.5">
                <UserCheck className="w-3.5 h-3.5 text-emerald-400" />
                <span>Owner: <strong>{ownerProfile?.owner_name || 'Niranjan'}</strong></span>
                {ownerProfile?.phone && <span>• {ownerProfile.phone}</span>}
              </div>
            </div>
          </div>
          <MonoLabel variant="emerald" pulseDot>
            ACTIVE STORE
          </MonoLabel>
        </div>

        {/* Switch Available Stores */}
        <div>
          <label className="text-xs text-white/50 block mb-2 font-mono uppercase tracking-wider">
            Available Kirana Stores ({allOwners.length || 3})
          </label>
          <div className="space-y-2">
            {(allOwners.length > 0
              ? allOwners
              : [
                  { id: 1, store_name: 'Sri Balaji Kirana', owner_name: 'Niranjan', phone: '9876543210', is_active: true },
                  { id: 2, store_name: 'Gupta Provision Store', owner_name: 'Ramesh Gupta', phone: '9876543220', is_active: false },
                  { id: 3, store_name: 'Royal Super Market', owner_name: 'Suresh Kumar', phone: '9876543230', is_active: false }
                ]
            ).map((s) => (
              <button
                key={s.id}
                onClick={() => switchStore(s.id)}
                className={`w-full text-left p-3.5 rounded-2xl border transition-all flex items-center justify-between group active:scale-[0.99] ${
                  s.is_active || (ownerProfile?.id === s.id)
                    ? 'border-emerald-500 bg-emerald-500/10 text-white'
                    : 'border-white/10 bg-white/[0.03] text-white/70 hover:border-white/25 hover:bg-white/[0.06]'
                }`}
              >
                <div className="flex items-center gap-3">
                  <div className={`w-9 h-9 rounded-xl flex items-center justify-center ${
                    s.is_active || (ownerProfile?.id === s.id)
                      ? 'bg-emerald-500/20 text-emerald-300'
                      : 'bg-white/5 text-white/50'
                  }`}>
                    <Store className="w-4 h-4" />
                  </div>
                  <div>
                    <div className="font-medium text-white text-sm">
                      {s.store_name}
                    </div>
                    <div className="text-[11px] text-white/50">
                      Owner: {s.owner_name} {s.phone ? `· ${s.phone}` : ''}
                    </div>
                  </div>
                </div>

                {s.is_active || (ownerProfile?.id === s.id) ? (
                  <span className="flex items-center gap-1 text-xs text-emerald-400 font-mono font-medium">
                    <Check className="w-4 h-4" /> Selected
                  </span>
                ) : (
                  <span className="text-xs text-white/40 group-hover:text-white font-mono transition-colors">
                    Switch Store →
                  </span>
                )}
              </button>
            ))}
          </div>
        </div>

        {/* Daily Cash Drawer Settlement / Reset */}
        <div className="p-4 rounded-2xl bg-white/[0.02] border border-white/10 space-y-2">
          <div className="flex items-center justify-between">
            <div>
              <span className="text-xs font-semibold text-white block">Daily Cash Drawer Reset</span>
              <span className="text-[11px] text-white/50 block">Reset today's collected payment cash balance to ₹0 at close.</span>
            </div>
            <button
              onClick={async () => {
                if (window.confirm("Aaj ka collected cash drawer reset karna chahte hain? (Customer udhaar records safe rahenge)")) {
                  await resetTodayPayments();
                }
              }}
              className="px-3 py-1.5 rounded-xl text-xs font-mono bg-rose-500/20 text-rose-300 border border-rose-500/30 hover:bg-rose-500/30 transition flex items-center gap-1.5"
            >
              <RefreshCw className="w-3.5 h-3.5" />
              Reset Cash
            </button>
          </div>
        </div>

        {/* Security & Multi-Store Notice */}
        <div className="flex items-start gap-2 text-xs text-white/40">
          <Shield className="w-4 h-4 text-emerald-400 shrink-0 mt-0.5" />
          <span>Each store ledger is isolated with customer data encrypted and scoped to the active merchant.</span>
        </div>
      </div>
    </Sheet>
  );
};
