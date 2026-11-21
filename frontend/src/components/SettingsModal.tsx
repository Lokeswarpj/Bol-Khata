import React from 'react';
import { Sheet } from './Sheet';
import { MonoLabel } from './MonoLabel';
import { GlowPill } from './GlowPill';
import { useLedgerStore } from '../store/useLedgerStore';
import { Sliders, Sparkles, Volume2, Shield, Download } from 'lucide-react';
import type { EffectsMode } from '../types';

export const SettingsModal: React.FC = () => {
  const { isSettingsOpen, setSettingsOpen, settings, updateSettings } = useLedgerStore();

  if (!isSettingsOpen) return null;

  return (
    <Sheet isOpen={isSettingsOpen} onClose={() => setSettingsOpen(false)} title="Ledger Settings">
      <div className="space-y-6 text-sm text-paper">
        {/* Language Selection */}
        <div>
          <label className="text-xs text-white/50 block mb-2 font-mono uppercase tracking-wider">
            Voice & UI Language
          </label>
          <div className="grid grid-cols-2 sm:grid-cols-5 gap-2">
            {[
              { id: 'auto', label: 'Auto (Detect)' },
              { id: 'hi-IN', label: 'Hindi (हिंदी)' },
              { id: 'en-IN', label: 'English (Indian)' },
              { id: 'kn-IN', label: 'Kannada (ಕನ್ನಡ)' },
              { id: 'te-IN', label: 'Telugu (తెలుగు)' },
            ].map((lang) => (
              <button
                key={lang.id}
                onClick={() => updateSettings({ language: lang.id })}
                className={`p-3 rounded-2xl text-xs font-medium border text-center transition-all ${
                  settings.language === lang.id
                    ? 'border-emerald-500 bg-emerald-500/10 text-emerald-300'
                    : 'border-white/10 bg-white/5 text-white/60 hover:border-white/20'
                }`}
              >
                {lang.label}
              </button>
            ))}
          </div>
        </div>

        {/* Visual Effects Tier */}
        <div>
          <div className="flex items-center justify-between mb-2">
            <label className="text-xs text-white/50 block font-mono uppercase tracking-wider">
              Visual Effects Mode
            </label>
            <Sparkles className="w-4 h-4 text-emerald-400" />
          </div>
          <div className="grid grid-cols-3 gap-2">
            {[
              { id: 'auto', label: 'Auto (Phone)' },
              { id: 'full', label: 'Full Effects' },
              { id: 'lite', label: 'Lite (2GB)' },
            ].map((mode) => (
              <button
                key={mode.id}
                onClick={() => updateSettings({ effectsMode: mode.id as EffectsMode })}
                className={`p-3 rounded-2xl text-xs font-medium border text-center transition-all ${
                  settings.effectsMode === mode.id
                    ? 'border-emerald-500 bg-emerald-500/10 text-emerald-300'
                    : 'border-white/10 bg-white/5 text-white/60 hover:border-white/20'
                }`}
              >
                {mode.label}
              </button>
            ))}
          </div>
          <p className="text-[11px] text-white/40 mt-1.5">
            Lite mode turns off heavy blurs, shimmer borders, and morphing blobs to save battery on budget devices.
          </p>
        </div>

        {/* Wake Word Feature (Roadmap) */}
        <div className="p-4 rounded-2xl glass border border-white/10 opacity-70">
          <div className="flex items-center justify-between mb-1">
            <span className="font-medium text-white/80 flex items-center gap-2">
              <Volume2 className="w-4 h-4 text-white/40" /> Hands-free Wake Phrase
            </span>
            <span className="text-[9px] px-2 py-0.5 rounded-full bg-white/10 border border-white/20 font-mono text-white/60">
              ROADMAP
            </span>
          </div>
          <p className="text-xs text-white/40">
            "Hey Khata" continuous wake word detection is planned for future low-power DSP models.
          </p>
        </div>

        {/* Privacy & DPDP Notice */}
        <div className="p-4 rounded-2xl glass border border-white/10">
          <div className="flex items-center gap-2 mb-1 text-emerald-400">
            <Shield className="w-4 h-4" />
            <span className="text-xs font-semibold uppercase tracking-wider">DPDP Act Compliance</span>
          </div>
          <p className="text-xs text-white/50 leading-relaxed">
            Data is encrypted at rest using AES-256. Reminders are opt-in only. Voice audio is purged immediately after transaction synthesis.
          </p>
        </div>

        <GlowPill
          variant="primary"
          className="w-full"
          onClick={() => setSettingsOpen(false)}
        >
          Close Settings
        </GlowPill>
      </div>
    </Sheet>
  );
};
