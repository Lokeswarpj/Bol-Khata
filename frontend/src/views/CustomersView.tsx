import React, { useState } from 'react';
import { useLedgerStore } from '../store/useLedgerStore';
import { MonoLabel } from '../components/MonoLabel';
import { Search, User, ArrowLeft, Plus } from 'lucide-react';
import type { Customer } from '../types';

interface CustomersViewProps {
  onBack: () => void;
  onSelectCustomer: (customer: Customer) => void;
}

export const CustomersView: React.FC<CustomersViewProps> = ({ onBack, onSelectCustomer }) => {
  const { customers, setManualEntryOpen } = useLedgerStore();
  const [search, setSearch] = useState('');

  const filtered = customers
    .filter((c) => c.name.toLowerCase().includes(search.toLowerCase()) || (c.nickname && c.nickname.toLowerCase().includes(search.toLowerCase())))
    .sort((a, b) => (b.balance || 0) - (a.balance || 0)); // Sorted by highest dues first

  return (
    <div className="min-h-screen bg-ink text-paper pb-24">
      {/* Top Bar - Frosted Glass */}
      <header className="sticky top-0 z-40 bg-black/20 backdrop-blur-xl border-b border-white/10 px-4 py-3 flex items-center justify-between shadow-[0_8px_32px_rgba(0,0,0,0.2)]">
        <div className="flex items-center gap-3">
          <button
            onClick={onBack}
            className="p-2 rounded-full hover:bg-white/10 text-white/70 hover:text-white transition-colors"
          >
            <ArrowLeft className="w-5 h-5" />
          </button>
          <h1 className="font-serif text-xl text-paper">Khata Customers</h1>
        </div>

        <button
          onClick={() => setManualEntryOpen(true)}
          className="p-2 rounded-full glass border border-white/20 text-white hover:border-emerald-500/50"
          title="Add Customer / Entry"
        >
          <Plus className="w-5 h-5" />
        </button>
      </header>

      {/* Main Content */}
      <main className="max-w-md mx-auto p-4 space-y-4">
        {/* Pill Search Field */}
        <div className="relative">
          <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-white/40" />
          <input
            type="text"
            placeholder="Search by name or nickname..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full pl-11 pr-4 py-3 bg-white/5 border border-white/10 rounded-full text-sm text-paper placeholder-white/30 focus:outline-none focus:border-emerald-500 transition-colors"
          />
        </div>

        <div className="flex items-center justify-between px-1">
          <MonoLabel variant="muted">
            {filtered.length} CUSTOMERS SORTED BY DUES
          </MonoLabel>
        </div>

        {/* Customer List */}
        <div className="space-y-2">
          {filtered.map((customer) => (
            <div
              key={customer.id}
              onClick={() => onSelectCustomer(customer)}
              className="p-4 rounded-2xl glass border border-white/5 hover:border-white/20 transition-all cursor-pointer flex items-center justify-between group active:scale-[0.99]"
            >
              <div className="flex items-center gap-3 min-w-0">
                <div className="w-10 h-10 rounded-full bg-white/5 border border-white/10 flex items-center justify-center text-white/60 group-hover:text-emerald-400 group-hover:border-emerald-500/30 transition-colors shrink-0">
                  <User className="w-5 h-5" />
                </div>
                <div className="min-w-0">
                  <div className="font-medium text-white text-base truncate">
                    {customer.name}
                  </div>
                  <div className="text-xs text-white/40 truncate">
                    {customer.phone || (customer.opted_in_reminders ? 'Opted in reminders' : 'No phone')}
                  </div>
                </div>
              </div>

              <div className="text-right shrink-0">
                <div className="text-[10px] text-white/40 uppercase font-mono">Dues</div>
                <div className={`font-serif text-xl font-normal ${(customer.balance || 0) > 0 ? 'text-rose-400' : 'text-emerald-400'}`}>
                  ₹{customer.balance || 0}
                </div>
              </div>
            </div>
          ))}

          {filtered.length === 0 && (
            <div className="text-center py-12 text-white/40 text-sm">
              No customers found. Tap + to add an entry or customer.
            </div>
          )}
        </div>
      </main>
    </div>
  );
};
