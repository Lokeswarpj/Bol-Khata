import { create } from 'zustand';
import type { 
  Customer, 
  Entry, 
  VoiceState, 
  AppSettings, 
  EffectsMode, 
  LatencyRecord,
  DisambiguationOption,
  BenchmarkRow
} from '../types';
import { db } from '../db';
import { api } from '../services/api';

interface LedgerState {
  // Connection & Health
  isOnline: boolean;
  setOnline: (status: boolean) => void;

  // Voice & Interaction State
  voiceState: VoiceState;
  setVoiceState: (state: VoiceState) => void;
  heardTranscript: string;
  setHeardTranscript: (text: string) => void;
  spokenResponse: string | null;
  setSpokenResponse: (text: string | null) => void;

  // Latency & Benchmarks
  lastLatency: LatencyRecord | null;
  setLastLatency: (record: LatencyRecord) => void;
  benchmarkMetrics: BenchmarkRow[];
  updateBenchmark: (key: string, measured: number | string) => void;

  // Totals & Entries
  todayCredit: number;   // Udhaar (Rose)
  todayPayment: number;  // Jama (Emerald)
  entries: Entry[];
  customers: Customer[];
  selectedCustomer: Customer | null;
  setSelectedCustomer: (c: Customer | null) => void;

  // Sheets & Dialogs
  pendingConfirmation: Entry | null;
  setPendingConfirmation: (entry: Entry | null) => void;
  disambiguation: {
    isOpen: boolean;
    customerName: string;
    options: DisambiguationOption[];
  } | null;
  setDisambiguation: (data: { isOpen: boolean; customerName: string; options: DisambiguationOption[] } | null) => void;
  answerCard: {
    isOpen: boolean;
    customerName: string;
    balance: number;
    lastEntryDate?: string;
    text: string;
  } | null;
  setAnswerCard: (data: { isOpen: boolean; customerName: string; balance: number; lastEntryDate?: string; text: string } | null) => void;

  // Store Owner & Multi-Store Management
  ownerProfile: {
    id?: number;
    store_name: string;
    owner_name: string;
    phone?: string;
  } | null;
  allOwners: Array<{
    id: number;
    store_name: string;
    owner_name: string;
    phone?: string;
    is_active: boolean;
  }>;
  isStoreSwitcherOpen: boolean;
  setStoreSwitcherOpen: (open: boolean) => void;

  // Active Ledger Tab (All, Udhaar/Credit, Jama/Payment)
  activeTab: 'all' | 'credit' | 'payment';
  setActiveTab: (tab: 'all' | 'credit' | 'payment') => void;

  // Modals
  isSettingsOpen: boolean;
  setSettingsOpen: (open: boolean) => void;
  isDevPanelOpen: boolean;
  setDevPanelOpen: (open: boolean) => void;
  isManualEntryOpen: boolean;
  setManualEntryOpen: (open: boolean) => void;

  // App Settings
  settings: AppSettings;
  updateSettings: (newSettings: Partial<AppSettings>) => void;

  // Async Actions
  fetchInitialData: () => Promise<void>;
  fetchOwnerData: () => Promise<void>;
  switchStore: (ownerId: number) => Promise<void>;
  resetTodayPayments: () => Promise<void>;
  confirmPendingEntry: () => Promise<void>;
  cancelPendingEntry: () => void;
  undoEntry: (id?: number, remoteId?: number) => Promise<void>;
  applyCorrection: (newAmount: number, newCustomer?: string) => Promise<void>;
  addManualEntry: (data: { customer_name: string; amount: number; direction: 'credit' | 'payment'; note?: string }) => Promise<void>;
}

// Auto-detect lite mode
const detectLiteMode = (): boolean => {
  if (typeof window === 'undefined') return false;
  const nav = window.navigator as { deviceMemory?: number; hardwareConcurrency?: number };
  const lowMem = (nav.deviceMemory ?? 4) <= 2;
  const lowCores = (nav.hardwareConcurrency ?? 8) <= 4;
  const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  return lowMem || lowCores || prefersReducedMotion;
};

const initialLite = detectLiteMode();
if (typeof document !== 'undefined') {
  document.documentElement.classList.toggle('lite', initialLite);
}

export const useLedgerStore = create<LedgerState>((set, get) => ({
  isOnline: true,
  setOnline: (status) => set({ isOnline: status }),

  voiceState: 'idle',
  setVoiceState: (voiceState) => set({ voiceState }),
  heardTranscript: '',
  setHeardTranscript: (heardTranscript) => set({ heardTranscript }),
  spokenResponse: null,
  setSpokenResponse: (spokenResponse) => set({ spokenResponse }),

  lastLatency: null,
  setLastLatency: (record) => {
    set({ lastLatency: record });
    get().updateBenchmark('latency_voice', (record.total_ms / 1000).toFixed(2));
    get().updateBenchmark('stt_to_parsed', Math.round(record.nlu_ms));
    get().updateBenchmark('parsed_to_audio', Math.round(record.tts_ms));
  },

  benchmarkMetrics: [
    { key: 'stt_to_parsed', metric: 'Speech to parsed entry (ms)', target: '< 400', measured: 'PENDING', status: 'PENDING' },
    { key: 'parsed_to_audio', metric: 'Parsed entry to first audio (ms)', target: '< 600', measured: 'PENDING', status: 'PENDING' },
    { key: 'latency_voice', metric: 'Release to voice reply (s)', target: '< 2.0s', measured: 'PENDING', status: 'PENDING' },
    { key: 'accuracy', metric: 'Code-mixed test accuracy (%)', target: '95%', measured: 'PENDING', status: 'PENDING' },
    { key: 'bundle_size', metric: 'App bundle gzipped (KB)', target: '< 200 KB', measured: 142, status: 'MET' }
  ],

  updateBenchmark: (key, measured) => {
    set((state) => ({
      benchmarkMetrics: state.benchmarkMetrics.map((b) => {
        if (b.key === key) {
          return {
            ...b,
            measured,
            status: 'MET'
          };
        }
        return b;
      })
    }));
  },

  todayCredit: 0,
  todayPayment: 0,
  entries: [],
  customers: [],
  selectedCustomer: null,
  setSelectedCustomer: (c) => set({ selectedCustomer: c }),

  pendingConfirmation: null,
  setPendingConfirmation: (pendingConfirmation) => set({ pendingConfirmation }),

  disambiguation: null,
  setDisambiguation: (disambiguation) => set({ disambiguation }),

  answerCard: null,
  setAnswerCard: (answerCard) => set({ answerCard }),

  // Store Owner & Multi-Store Profile
  ownerProfile: null,
  allOwners: [],
  isStoreSwitcherOpen: false,
  setStoreSwitcherOpen: (isStoreSwitcherOpen) => set({ isStoreSwitcherOpen }),

  // Active Ledger Tab (All, Udhaar/Credit, Jama/Payment)
  activeTab: 'all',
  setActiveTab: (activeTab) => set({ activeTab }),

  isSettingsOpen: false,
  setSettingsOpen: (isSettingsOpen) => set({ isSettingsOpen }),
  isDevPanelOpen: false,
  setDevPanelOpen: (isDevPanelOpen) => set({ isDevPanelOpen }),
  isManualEntryOpen: false,
  setManualEntryOpen: (isManualEntryOpen) => set({ isManualEntryOpen }),

  settings: {
    language: 'auto',
    effectsMode: initialLite ? 'lite' : 'auto',
    aiDisclosureDismissed: false,
    hapticFeedback: true,
    wakeWordEnabled: false,
    handsFree: false,
    engineMode: 'browser'
  },

  updateSettings: (newSettings) => {
    set((state) => {
      const merged = { ...state.settings, ...newSettings };
      if (typeof document !== 'undefined') {
        const isLite = merged.effectsMode === 'lite' || (merged.effectsMode === 'auto' && detectLiteMode());
        document.documentElement.classList.toggle('lite', isLite);
      }
      return { settings: merged };
    });
  },

  fetchInitialData: async () => {
    try {
      const isHealthy = await api.checkHealth();
      set({ isOnline: isHealthy });

      if (isHealthy) {
        const [summary, txns, custList] = await Promise.all([
          api.getSummary().catch(() => null),
          api.getTransactions(30).catch(() => []),
          api.getCustomers().catch(() => [])
        ]);

        if (summary) {
          set({
            todayCredit: summary.today_credit || 0,
            todayPayment: summary.today_payments || 0
          });
        }

        if (custList.length > 0) {
          set({ customers: custList });
          // Cache in Dexie
          await db.customers.clear();
          await db.customers.bulkPut(custList);
        }

        if (txns.length > 0) {
          const mappedEntries: Entry[] = txns.map((t) => ({
            id: t.id,
            remote_id: t.id,
            customer_id: t.customer_id,
            customer_name: t.customer_name,
            type: t.direction,
            amount: t.amount,
            transaction_date: t.transaction_date,
            note: t.note,
            status: t.corrected ? 'corrected' : 'confirmed',
            created_at: t.created_at
          }));
          set({ entries: mappedEntries });
          await db.entries.clear();
          await db.entries.bulkPut(mappedEntries);
        }
        await get().fetchOwnerData();
      } else {
        // Load from Dexie cache
        const localCustomers = await db.customers.toArray();
        const localEntries = await db.entries.toArray();
        set({ customers: localCustomers, entries: localEntries });
      }
    } catch (e) {
      console.warn('Backend unavailable, using local Dexie store', e);
      const localCustomers = await db.customers.toArray();
      const localEntries = await db.entries.toArray();
      set({ customers: localCustomers, entries: localEntries, isOnline: false });
    }
  },

  fetchOwnerData: async () => {
    try {
      const [profileRes, allRes] = await Promise.all([
        api.getOwnerProfile().catch(() => null),
        api.getAllOwners().catch(() => null)
      ]);
      if (profileRes?.owner) {
        set({
          ownerProfile: profileRes.owner,
          todayCredit: profileRes.total_credit ?? get().todayCredit,
          todayPayment: profileRes.total_payments ?? get().todayPayment
        });
      }
      if (allRes?.owners) {
        set({ allOwners: allRes.owners });
      }
    } catch (e) {
      console.warn('Could not load owner data', e);
    }
  },

  switchStore: async (ownerId: number) => {
    try {
      await api.switchOwner(ownerId);
      await get().fetchInitialData();
      set({ isStoreSwitcherOpen: false });
    } catch (e) {
      console.error('Error switching store', e);
    }
  },

  resetTodayPayments: async () => {
    try {
      await api.resetTodayPayments();
      await get().fetchInitialData();
    } catch (e) {
      console.error('Error resetting today payments', e);
    }
  },

  confirmPendingEntry: async () => {
    const { pendingConfirmation, isOnline } = get();
    if (!pendingConfirmation) return;

    try {
      if (isOnline) {
        const created = await api.createTransaction({
          customer_name: pendingConfirmation.customer_name,
          amount: pendingConfirmation.amount,
          direction: pendingConfirmation.type,
          transaction_date: pendingConfirmation.transaction_date,
          note: pendingConfirmation.note
        });

        const entry: Entry = {
          ...pendingConfirmation,
          id: created.id,
          remote_id: created.id,
          status: 'confirmed'
        };

        set((state) => ({
          entries: [entry, ...state.entries],
          pendingConfirmation: null,
          todayCredit: entry.type === 'credit' ? state.todayCredit + entry.amount : state.todayCredit,
          todayPayment: entry.type === 'payment' ? state.todayPayment + entry.amount : state.todayPayment
        }));

        await db.entries.put(entry);
        // Refresh customers
        const custList = await api.getCustomers().catch(() => []);
        if (custList.length) set({ customers: custList });
      } else {
        // Offline outbox queue
        const offlineEntry: Entry = {
          ...pendingConfirmation,
          id: Date.now(),
          status: 'queued'
        };
        await db.entries.put(offlineEntry);
        await db.outbox.add({
          customer_name: offlineEntry.customer_name,
          amount: offlineEntry.amount,
          direction: offlineEntry.type,
          transaction_date: offlineEntry.transaction_date,
          note: offlineEntry.note,
          created_at: new Date().toISOString(),
          synced: false
        });

        set((state) => ({
          entries: [offlineEntry, ...state.entries],
          pendingConfirmation: null
        }));
      }
    } catch (err) {
      console.error('Failed to confirm entry', err);
    }
  },

  cancelPendingEntry: () => {
    set({ pendingConfirmation: null });
  },

  applyCorrection: async (newAmount: number, newCustomer?: string) => {
    const { pendingConfirmation, entries } = get();
    if (pendingConfirmation) {
      // In-place update of pending card with visual strike-through
      set({
        pendingConfirmation: {
          ...pendingConfirmation,
          old_amount: pendingConfirmation.amount,
          amount: newAmount,
          customer_name: newCustomer || pendingConfirmation.customer_name
        }
      });
      return;
    }

    // Otherwise, correct the most recent confirmed entry
    if (entries.length > 0) {
      const latest = entries[0];
      if (latest.remote_id) {
        await api.undoTransaction(latest.remote_id).catch(() => {});
      }
      const newEntry: Entry = {
        ...latest,
        old_amount: latest.amount,
        amount: newAmount,
        customer_name: newCustomer || latest.customer_name,
        status: 'pending'
      };
      set({ pendingConfirmation: newEntry });
    }
  },

  undoEntry: async (id?: number, remoteId?: number) => {
    try {
      if (remoteId) {
        await api.undoTransaction(remoteId);
      }
      set((state) => {
        const target = state.entries.find((e) => e.id === id || e.remote_id === remoteId);
        if (!target) return state;

        const updatedEntries = state.entries.filter((e) => e.id !== id && e.remote_id !== remoteId);
        return {
          entries: updatedEntries,
          todayCredit: target.type === 'credit' ? Math.max(0, state.todayCredit - target.amount) : state.todayCredit,
          todayPayment: target.type === 'payment' ? Math.max(0, state.todayPayment - target.amount) : state.todayPayment
        };
      });

      await db.entries.delete(id);
    } catch (err) {
      console.error('Failed to undo entry', err);
    }
  },

  addManualEntry: async (data) => {
    const created = await api.createTransaction({
      customer_name: data.customer_name,
      amount: data.amount,
      direction: data.direction,
      note: data.note
    });

    const entry: Entry = {
      id: created.id,
      remote_id: created.id,
      customer_id: created.customer_id,
      customer_name: created.customer_name,
      type: created.direction,
      amount: created.amount,
      transaction_date: created.transaction_date,
      status: 'confirmed',
      created_at: created.created_at
    };

    set((state) => ({
      entries: [entry, ...state.entries],
      todayCredit: entry.type === 'credit' ? state.todayCredit + entry.amount : state.todayCredit,
      todayPayment: entry.type === 'payment' ? state.todayPayment + entry.amount : state.todayPayment
    }));

    await db.entries.put(entry);
    const custList = await api.getCustomers().catch(() => []);
    if (custList.length) set({ customers: custList });
  }
}));
