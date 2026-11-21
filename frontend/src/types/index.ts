export type TransactionDirection = 'credit' | 'payment';

export interface Customer {
  id: number;
  name: string;
  phone?: string;
  nickname?: string;
  area_hint?: string;
  aliases?: string[];
  opted_in_reminders: boolean;
  balance: number;
  created_at?: string;
}

export interface Entry {
  id?: number;
  remote_id?: number;
  customer_id?: number;
  customer_name: string;
  type: TransactionDirection; // credit = udhaar (rose), payment = jama (emerald)
  amount: number;
  old_amount?: number; // for 15s visual strike-through when corrected
  transaction_date: string;
  items?: string;
  note?: string;
  heard_text?: string;
  confidence?: number;
  status: 'confirmed' | 'pending' | 'corrected' | 'queued';
  created_at?: string;
}

export interface OutboxEntry {
  id?: number;
  customer_name: string;
  amount: number;
  direction: TransactionDirection;
  transaction_date: string;
  note?: string;
  created_at: string;
  synced: boolean;
}

export type VoiceState = 'idle' | 'listening' | 'thinking' | 'speaking';

export interface VoiceIntent {
  type: 'credit' | 'payment' | 'query' | 'correction' | 'undo' | 'unknown';
  customer?: string;
  amount?: number;
  direction?: 'credit' | 'payment';
  confidence: number;
}

export interface DisambiguationOption {
  id?: number;
  name: string;
  hint?: string;
  balance?: number;
}

export interface VoiceServerResponse {
  type: 'response' | 'error' | 'disclosure';
  text?: string;
  audio?: string; // base64
  success?: boolean;
  transcript?: string;
  needs_disambiguation?: boolean;
  disambiguation_options?: DisambiguationOption[];
  intent?: VoiceIntent;
  transaction?: {
    id: number;
    customer_name: string;
    amount: number;
    direction: string;
    date: string;
  };
}

export interface LatencyRecord {
  t0_release: number;
  t1_parsed: number;
  t2_audio: number;
  stt_ms: number;
  nlu_ms: number;
  tts_ms: number;
  total_ms: number;
}

export interface BenchmarkRow {
  metric: string;
  target: string;
  measured: string | number;
  status: 'PENDING' | 'MET' | 'IN_PROGRESS';
  key: string;
}

export type EffectsMode = 'auto' | 'full' | 'lite';

export interface AppSettings {
  language: string;
  effectsMode: EffectsMode;
  aiDisclosureDismissed: boolean;
  hapticFeedback: boolean;
  wakeWordEnabled: boolean; // Disabled with ROADMAP label
}
