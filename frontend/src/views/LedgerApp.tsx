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
import { BolKhataLogo } from '../components/BolKhataLogo';
import { VoiceKhataBackground3D } from '../components/VoiceKhataBackground3D';
import { CustomersView } from './CustomersView';
import { CustomerDetailView } from './CustomerDetailView';
import { Users, Settings, Wrench, Plus, ArrowUpRight, ArrowDownLeft, Wifi, WifiOff, Mic } from 'lucide-react';
import { api } from '../services/api';
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
    fetchInitialData,
    settings,
    updateSettings
  } = useLedgerStore();

  const [currentView, setCurrentView] = useState<'home' | 'customers' | 'customer_detail'>('home');
  const [selectedCust, setSelectedCust] = useState<Customer | null>(null);
  const [storeOwner, setStoreOwner] = useState<{ store_name: string; owner_name: string } | null>(null);

  useEffect(() => {
    fetchInitialData();
    voiceService.connect();
    api.getOwnerProfile().then(data => {
      if (data.registered && data.owner) {
        setStoreOwner({
          store_name: data.owner.store_name,
          owner_name: data.owner.owner_name,
        });
      }
    }).catch(console.warn);
  }, [fetchInitialData]);

  const handleMicPressStart = () => {
    voiceService.startRecording();
  };

  const handleMicPressEnd = () => {
    if (voiceState === 'listening') {
      voiceService.stopRecording();
    }
  };

  const handleMicToggle = () => {
    if (voiceState === 'listening') {
      voiceService.stopRecording();
    } else if (voiceState === 'idle') {
      voiceService.startRecording();
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
    <div className="min-h-screen bg-transparent text-paper flex flex-col justify-between selection:bg-emerald-500/20 pb-28 relative overflow-hidden">
      {/* 3D Voice & Khata Background */}
      <VoiceKhataBackground3D />
      {/* Top Bar - Frosted Glass */}
      <header className="sticky top-0 z-40 bg-black/20 backdrop-blur-xl border-b border-white/10 px-4 py-3 shadow-[0_8px_32px_rgba(0,0,0,0.2)]">
        <div className="max-w-md mx-auto flex items-center justify-between">
          {/* Logo Tile */}
          <div className="flex items-center gap-2.5 cursor-pointer group" onClick={onNavigateLanding}>
            <BolKhataLogo size="sm" />
            <div>
              <span className="font-serif tracking-tight text-lg text-white font-medium block leading-none">
                BolKhata
              </span>
              <MonoLabel variant="emerald" className="text-[9px] tracking-[0.25em]">
                {storeOwner ? `${storeOwner.store_name} · ${storeOwner.owner_name}` : 'VOICE LEDGER'}
              </MonoLabel>
            </div>
          </div>

          {/* Action Chips */}
          <div className="flex items-center gap-2">
            {/* Gnani Voice Badge */}
            <div className="hidden sm:flex items-center gap-1.5 px-2.5 py-1 rounded-full text-[10px] font-mono border bg-violet-500/10 border-violet-500/30 text-violet-300">
              <span className="w-1.5 h-1.5 rounded-full bg-violet-400 animate-ping"></span>
              <span>GNANI TIMBRE</span>
            </div>

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

      {/* Main Content Area */}
      <main className="max-w-md w-full mx-auto px-4 pt-4 flex-1 flex flex-col gap-5">
        {/* Real-time Voice Transcript Strip */}
        {heardTranscript && (
          <div className="glass px-4 py-2.5 rounded-2xl border border-white/10 flex items-center gap-2 animate-in fade-in slide-in-from-top-2">
            <span className="w-2 h-2 rounded-full bg-emerald-400 animate-ping" />
            <p className="text-xs text-paper/80 font-mono truncate">
              "{heardTranscript}"
            </p>
          </div>
        )}

        {/* Big Balance Hero Cards */}
        <div className="grid grid-cols-2 gap-3">
          {/* Credit (Udhaar) Card */}
          <div className="glass p-4 rounded-3xl border border-white/10 flex flex-col justify-between relative overflow-hidden group">
            <div className="absolute top-0 right-0 w-24 h-24 bg-rose-500/5 rounded-full blur-2xl group-hover:bg-rose-500/10 transition-colors" />
            <div className="flex items-center justify-between text-white/60 text-xs mb-3">
              <span className="font-mono uppercase tracking-wider text-[11px]">Today Udhaar</span>
              <div className="p-1 rounded-full bg-rose-500/10 text-rose-400">
                <ArrowUpRight className="w-3.5 h-3.5" />
              </div>
            </div>
            <div>
              <div className="text-2xl font-serif text-paper font-semibold tracking-tight">
                ₹{Math.round(todayCredit).toLocaleString('en-IN')}
              </div>
              <span className="text-[10px] text-white/40 font-mono mt-0.5 block">
                Grahak se lena hai
              </span>
            </div>
          </div>

          {/* Payment (Jama) Card */}
          <div className="glass p-4 rounded-3xl border border-white/10 flex flex-col justify-between relative overflow-hidden group">
            <div className="absolute top-0 right-0 w-24 h-24 bg-emerald-500/5 rounded-full blur-2xl group-hover:bg-emerald-500/10 transition-colors" />
            <div className="flex items-center justify-between text-white/60 text-xs mb-3">
              <span className="font-mono uppercase tracking-wider text-[11px]">Today Jama</span>
              <div className="p-1 rounded-full bg-emerald-500/10 text-emerald-400">
                <ArrowDownLeft className="w-3.5 h-3.5" />
              </div>
            </div>
            <div>
              <div className="text-2xl font-serif text-paper font-semibold tracking-tight">
                ₹{Math.round(todayPayment).toLocaleString('en-IN')}
              </div>
              <span className="text-[10px] text-white/40 font-mono mt-0.5 block">
                Cash aagaya hai
              </span>
            </div>
          </div>
        </div>

        {/* Action Bar (Manual Entry & Quick stats) */}
        <div className="flex items-center justify-between px-1">
          <div className="flex items-center gap-2">
            <MonoLabel variant="muted" className="text-[10px]">
              RECENT TRANSACTIONS
            </MonoLabel>
            <span className="text-xs text-white/40 font-mono">
              ({entries.length})
            </span>
          </div>

          <button
            onClick={() => setManualEntryOpen(true)}
            className="flex items-center gap-1.5 text-xs text-white/70 hover:text-white glass px-3 py-1.5 rounded-full border border-white/10 hover:border-white/20 transition-all font-mono"
          >
            <Plus className="w-3 h-3 text-emerald-400" />
            <span>MANUAL ENTRY</span>
          </button>
        </div>

        {/* Feed of Ledger Entries */}
        <div className="flex flex-col gap-2.5 pb-6">
          {entries.length > 0 ? (
            entries.slice(0, 15).map((entry) => (
              <EntryCard
                key={entry.id}
                entry={entry}
                onUndo={() => undoEntry(entry.id, entry.remote_id)}
              />
            ))
          ) : (
            <div className="glass rounded-3xl p-8 border border-white/10 text-center flex flex-col items-center justify-center my-6">
              <div className="w-12 h-12 rounded-2xl bg-white/5 flex items-center justify-center text-white/30 mb-3">
                <Mic className="w-6 h-6 text-white/40" />
              </div>
              <h4 className="font-serif text-base text-paper mb-1">
                Koi entry nahi mili
              </h4>
              <p className="text-xs text-white/50 max-w-xs font-sans leading-relaxed">
                Neeche Mic button ko daba kar boliye: <br />
                <span className="text-white/80 font-mono mt-1 block">"Ramesh ka 340 udhaar likh lo"</span>
              </p>
            </div>
          )}
        </div>
      </main>

      {/* Floating Push-to-Talk Mic Bar */}
      <div className="fixed bottom-4 inset-x-0 z-30 flex flex-col items-center pointer-events-none">
        <div className="pointer-events-auto flex items-center flex-col gap-2">
          {/* Hands-Free & 1-Click Multilingual Switcher */}
          <div className="flex items-center gap-1.5 flex-wrap justify-center">
            {/* Hands-Free Auto-Listening Toggle */}
            <button
              onClick={() => updateSettings({ handsFree: !settings.handsFree })}
              className={`px-2.5 py-0.5 rounded-full text-[10px] font-mono flex items-center gap-1 transition-all border ${
                settings.handsFree
                  ? 'bg-cyan-500/20 text-cyan-300 border-cyan-400/50 shadow-[0_0_12px_rgba(6,182,212,0.3)] animate-pulse'
                  : 'bg-black/50 text-white/50 border-white/10 hover:text-white'
              }`}
              title="Continuous Hands-Free Autonomous Listening"
            >
              <span className={`w-1.5 h-1.5 rounded-full ${settings.handsFree ? 'bg-cyan-400' : 'bg-white/30'}`} />
              <span>HANDS-FREE {settings.handsFree ? 'ON' : 'OFF'}</span>
            </button>

            {/* Language Selector */}
            <div className="flex items-center gap-0.5 p-0.5 rounded-full glass border border-white/10 bg-black/50 backdrop-blur-md shadow-lg">
              {[
                { id: 'auto', label: 'AUTO' },
                { id: 'hi-IN', label: 'हिन्दी' },
                { id: 'en-IN', label: 'ENG' },
                { id: 'kn-IN', label: 'ಕನ್ನಡ' },
                { id: 'te-IN', label: 'తెలుగు' }
              ].map((lang) => (
                <button
                  key={lang.id}
                  onClick={() => updateSettings({ language: lang.id })}
                  className={`px-2 py-0.5 rounded-full text-[10px] font-mono transition-all ${
                    settings.language === lang.id
                      ? 'bg-emerald-500/20 text-emerald-300 font-bold border border-emerald-500/40 shadow-[0_0_10px_rgba(16,185,129,0.3)]'
                      : 'text-white/50 hover:text-white border border-transparent'
                  }`}
                  title={`Language: ${lang.label}`}
                >
                  {lang.label}
                </button>
              ))}
            </div>
          </div>

          <MicButton
            state={voiceState}
            onPressStart={handleMicPressStart}
            onPressEnd={handleMicPressEnd}
            onClickToggle={handleMicToggle}
          />
          <span className="text-[10px] text-white/40 font-mono tracking-wider uppercase">
            {voiceState === 'listening' ? 'Recording... (release or tap)' : 'Hold or tap to speak'}
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
