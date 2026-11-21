import React, { useEffect, useState } from 'react';
import { useLedgerStore } from '../store/useLedgerStore';
import { voiceService } from '../services/voiceService';
import { MonoLabel } from '../components/MonoLabel';
import { EntryCard } from '../components/EntryCard';
import { MicButton } from '../components/MicButton';
import { LatencyBadge } from '../components/LatencyBadge';
import { AIDisclosureModal } from '../components/AIDisclosureModal';
import { ConfirmationSheet } from '../components/ConfirmationSheet';
import { DisambiguationSheet } from '../components/DisambiguationSheet';
import { AnswerCard } from '../components/AnswerCard';
import { SettingsModal } from '../components/SettingsModal';
import { ManualEntryModal } from '../components/ManualEntryModal';
import { DevPanel } from '../components/DevPanel';
import { CustomersView } from './CustomersView';
import { CustomerDetailView } from './CustomerDetailView';
import { Users, Settings, Wrench, Plus, ArrowUpRight, ArrowDownLeft, Wifi, WifiOff } from 'lucide-react';
import type { Customer } from '../types';

export const LedgerApp: React.FC<{ onNavigateLanding: () => void }> = ({ onNavigateLanding }) => {
  const {
    isOnline,
    voiceState,
    heardTranscript,
    todayCredit,
    todayPayment,
    entries,
    setSettingsOpen,
    setDevPanelOpen,
    setManualEntryOpen,
    undoEntry,
    fetchInitialData
  } = useLedgerStore();

  const [currentView, setCurrentView] = useState<'home' | 'customers' | 'customer_detail'>('home');
  const [selectedCust, setSelectedCust] = useState<Customer | null>(null);

  useEffect(() => {
    fetchInitialData();
    voiceService.connect();
  }, [fetchInitialData]);

  const handleMicPressStart = () => {
    voiceService.startRecording();
  };

  const handleMicPressEnd = () => {
    if (voiceState === 'listening') {
      voiceService.stopRecording();
    }
  };

  const handleSelectCustomer = (c: Customer) => {
    setSelectedCust(c);
    setCurrentView('customer_detail');
  };

  if (currentView === 'customers') {
    return (
      <CustomersView
        onBack={() => setCurrentView('home')}
        onSelectCustomer={handleSelectCustomer}
      />
    );
  }

  if (currentView === 'customer_detail' && selectedCust) {
    return (
      <CustomerDetailView
        customer={selectedCust}
        onBack={() => setCurrentView('customers')}
      />
    );
  }

  return (
    <div className="min-h-screen bg-ink text-paper flex flex-col justify-between selection:bg-emerald-500/20 pb-28 relative overflow-hidden">
      {/* Top Bar */}
      <header className="sticky top-0 z-40 bg-ink/80 backdrop-blur-md border-b border-white/10 px-4 py-3">
        <div className="max-w-md mx-auto flex items-center justify-between">
          {/* Logo Tile */}
          <div className="flex items-center gap-2.5 cursor-pointer" onClick={onNavigateLanding}>
            <div className="w-8 h-8 rounded-xl bg-white text-ink flex items-center justify-center font-bold text-sm shadow-[0_0_15px_rgba(255,255,255,0.2)]">
              B
            </div>
            <div>
              <span className="font-serif tracking-tight text-lg text-white font-medium block leading-none">
                BolKhata
              </span>
              <MonoLabel variant="emerald" className="text-[9px] tracking-[0.25em]">
                VOICE LEDGER
              </MonoLabel>
            </div>
          </div>

          {/* Action Chips */}
          <div className="flex items-center gap-2">
            {/* Connectivity chip */}
            <div className={`flex items-center gap-1 px-2.5 py-1 rounded-full text-[10px] font-mono border ${
              isOnline
                ? 'bg-emerald-500/10 border-emerald-500/30 text-emerald-400'
                : 'bg-rose-500/10 border-rose-500/30 text-rose-400'
            }`}>
              {isOnline ? <Wifi className="w-3 h-3" /> : <WifiOff className="w-3 h-3" />}
              <span>{isOnline ? 'LIVE' : 'OFFLINE'}</span>
            </div>

            {/* Customers button */}
            <button
              onClick={() => setCurrentView('customers')}
              className="p-2 rounded-xl text-white/70 hover:text-white glass border border-white/10 hover:border-white/20 transition-colors"
              title="Customers Directory"
            >
              <Users className="w-4 h-4" />
            </button>

            {/* Dev Panel button */}
            <button
              onClick={() => setDevPanelOpen(true)}
              className="p-2 rounded-xl text-white/70 hover:text-white glass border border-white/10 hover:border-white/20 transition-colors"
              title="Dev & Demo Panel"
            >
              <Wrench className="w-4 h-4" />
            </button>

            {/* Settings button */}
            <button
              onClick={() => setSettingsOpen(true)}
              className="p-2 rounded-xl text-white/70 hover:text-white glass border border-white/10 hover:border-white/20 transition-colors"
              title="Settings"
            >
              <Settings className="w-4 h-4" />
            </button>
          </div>
        </div>
      </header>

      {/* Main App Container */}
      <main className="max-w-md mx-auto w-full px-4 pt-4 space-y-4 flex-1">
        {/* Today's Totals Grid */}
        <div className="grid grid-cols-2 gap-3">
          {/* Udhaar Given (Rose) */}
          <div className="glass rounded-3xl p-4 border border-white/10 relative overflow-hidden group">
            <div className="flex items-center justify-between text-rose-400/80 mb-1">
              <span className="text-[10px] font-mono uppercase tracking-wider flex items-center gap-1">
                <ArrowUpRight className="w-3 h-3" /> Aaj Ka Udhaar
              </span>
            </div>
            <div className="font-serif text-3xl sm:text-4xl font-normal tracking-tight text-rose-400">
              ₹{todayCredit.toLocaleString('en-IN')}
            </div>
            <span className="text-[10px] text-white/40 block mt-1">Given to customers</span>
          </div>

          {/* Jama Received (Emerald) */}
          <div className="glass rounded-3xl p-4 border border-white/10 relative overflow-hidden group">
            <div className="flex items-center justify-between text-emerald-400/80 mb-1">
              <span className="text-[10px] font-mono uppercase tracking-wider flex items-center gap-1">
                <ArrowDownLeft className="w-3 h-3" /> Aaj Ka Jama
              </span>
            </div>
            <div className="font-serif text-3xl sm:text-4xl font-normal tracking-tight text-emerald-400">
              ₹{todayPayment.toLocaleString('en-IN')}
            </div>
            <span className="text-[10px] text-white/40 block mt-1">Collected payment</span>
          </div>
        </div>

        {/* Live Transcript / Heard Pill */}
        <div className="glass rounded-2xl p-3 border border-white/10 flex items-center justify-between min-h-[52px]">
          <div className="flex items-center gap-2.5 min-w-0 pr-2">
            <MonoLabel variant="emerald" pulseDot={voiceState === 'listening'}>
              {voiceState === 'listening'
                ? 'LISTENING'
                : voiceState === 'thinking'
                ? 'THINKING'
                : voiceState === 'speaking'
                ? 'SPEAKING'
                : 'HEARD'}
            </MonoLabel>

            <span className="text-xs text-white/80 truncate italic">
              {heardTranscript ? `"${heardTranscript}"` : 'Hold mic below to speak entry...'}
            </span>
          </div>

          <button
            onClick={() => setManualEntryOpen(true)}
            className="p-1.5 rounded-xl glass border border-white/10 hover:border-emerald-500/50 text-white/60 hover:text-white shrink-0"
            title="Manual entry"
          >
            <Plus className="w-4 h-4" />
          </button>
        </div>

        {/* Recent Entries Header */}
        <div className="flex items-center justify-between pt-1">
          <MonoLabel variant="muted">
            RECENT LEDGER ENTRIES ({entries.length})
          </MonoLabel>
          <span className="text-[11px] text-white/40">Latest on top</span>
        </div>

        {/* Recent Entries List */}
        <div className="space-y-2">
          {entries.slice(0, 15).map((entry, idx) => (
            <EntryCard
              key={entry.id || idx}
              entry={entry}
              onUndo={() => undoEntry(entry.id!, entry.remote_id)}
            />
          ))}

          {entries.length === 0 && (
            <div className="text-center py-12 glass rounded-3xl border border-white/5 space-y-2">
              <p className="font-serif text-lg text-white/70">Khata is clean for today</p>
              <p className="text-xs text-white/40 max-w-xs mx-auto">
                Press and hold the white button below and say e.g. <span className="text-white/80">"Ramesh ka 340 udhaar"</span>
              </p>
            </div>
          )}
        </div>
      </main>

      {/* Floating Push-to-Talk Mic Bar */}
      <div className="fixed bottom-4 inset-x-0 z-30 flex flex-col items-center pointer-events-none">
        <div className="pointer-events-auto flex items-center flex-col gap-2">
          <MicButton
            state={voiceState}
            onPressStart={handleMicPressStart}
            onPressEnd={handleMicPressEnd}
          />
          <span className="text-[10px] text-white/40 font-mono tracking-wider uppercase">
            {voiceState === 'listening' ? 'Release when done' : 'Hold to speak'}
          </span>
        </div>
      </div>

      {/* Latency Badge in Corner */}
      <LatencyBadge />

      {/* Modals and Sheets */}
      <AIDisclosureModal />
      <ConfirmationSheet />
      <DisambiguationSheet />
      <AnswerCard />
      <SettingsModal />
      <ManualEntryModal />
      <DevPanel />
    </div>
  );
};
