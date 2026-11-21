import type { Customer, Entry, TransactionDirection } from '../types';

const API_BASE = '/api';

export interface LedgerSummaryResponse {
  total_credit: number;
  total_payments: number;
  net_outstanding: number;
  customer_count: number;
  today_credit: number;
  today_payments: number;
}

export interface TransactionResponse {
  id: number;
  customer_id: number;
  customer_name: string;
  amount: number;
  direction: TransactionDirection;
  transaction_date: string;
  note?: string;
  corrected: boolean;
  created_at?: string;
}

export const api = {
  // Ledger
  async getSummary(): Promise<LedgerSummaryResponse> {
    const res = await fetch(`${API_BASE}/ledger/summary`);
    if (!res.ok) throw new Error('Failed to fetch ledger summary');
    return res.json();
  },

  async getTransactions(limit = 50): Promise<TransactionResponse[]> {
    const res = await fetch(`${API_BASE}/ledger/transactions?limit=${limit}`);
    if (!res.ok) throw new Error('Failed to fetch transactions');
    return res.json();
  },

  async createTransaction(data: {
    customer_name: string;
    amount: number;
    direction: TransactionDirection;
    transaction_date?: string;
    note?: string;
  }): Promise<TransactionResponse> {
    const res = await fetch(`${API_BASE}/ledger/transaction`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });
    if (!res.ok) throw new Error('Failed to create transaction');
    return res.json();
  },

  async undoTransaction(txnId: number): Promise<{ message: string; id: number }> {
    const res = await fetch(`${API_BASE}/ledger/transaction/${txnId}`, {
      method: 'DELETE',
    });
    if (!res.ok) throw new Error('Failed to undo transaction');
    return res.json();
  },

  // Customers
  async getCustomers(search?: string): Promise<Customer[]> {
    const url = search 
      ? `${API_BASE}/customers/?search=${encodeURIComponent(search)}`
      : `${API_BASE}/customers/`;
    const res = await fetch(url);
    if (!res.ok) throw new Error('Failed to fetch customers');
    return res.json();
  },

  async getCustomerDues(customerId: number): Promise<{
    customer: { id: number; name: string };
    balance: number;
    transactions: Array<{
      id: number;
      amount: number;
      direction: TransactionDirection;
      date: string;
      note?: string;
      created_at?: string;
    }>;
  }> {
    const res = await fetch(`${API_BASE}/customers/${customerId}/dues`);
    if (!res.ok) throw new Error('Failed to fetch customer dues');
    return res.json();
  },

  async updateConsent(customerId: number, optIn: boolean): Promise<{ success: boolean; message: string }> {
    const res = await fetch(`${API_BASE}/compliance/consent/${customerId}?opt_in=${optIn}`, {
      method: 'POST',
    });
    if (!res.ok) throw new Error('Failed to update consent');
    return res.json();
  },

  async getReminder(customerId: number, language = 'hi-IN'): Promise<{
    status: string;
    customer_name: string;
    balance: number;
    reminder_message: string;
    compliance_note: string;
  }> {
    const res = await fetch(`${API_BASE}/compliance/reminder/${customerId}?language=${encodeURIComponent(language)}`);
    if (!res.ok) throw new Error('Failed to fetch reminder');
    return res.json();
  },

  // Store Owner Profile & Multi-Store Management
  async getOwnerProfile(): Promise<{
    registered: boolean;
    owner?: {
      id: number;
      store_name: string;
      owner_name: string;
      phone?: string;
      language_preference: string;
    };
    total_credit: number;
    total_payments: number;
    net_outstanding: number;
    customer_count: number;
  }> {
    const res = await fetch(`${API_BASE}/owner/profile`);
    if (!res.ok) throw new Error('Failed to fetch store owner profile');
    return res.json();
  },

  async getAllOwners() {
    const res = await fetch(`${API_BASE}/owner/all`);
    if (!res.ok) throw new Error('Failed to fetch all store owners');
    return res.json();
  },

  async signupOwner(data: {
    store_name: string;
    owner_name: string;
    phone: string;
    pin?: string;
    language_preference?: string;
  }) {
    const res = await fetch(`${API_BASE}/owner/signup`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });
    if (!res.ok) throw new Error('Failed to sign up store owner');
    return res.json();
  },

  async loginOwner(data: { phone: string; pin?: string }) {
    const res = await fetch(`${API_BASE}/owner/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });
    if (!res.ok) throw new Error('Failed to log in store owner');
    return res.json();
  },

  async switchOwner(ownerId: number) {
    const res = await fetch(`${API_BASE}/owner/switch/${ownerId}`, {
      method: 'POST',
    });
    if (!res.ok) throw new Error('Failed to switch store owner');
    return res.json();
  },

  async resetTodayPayments() {
    const res = await fetch(`${API_BASE}/owner/reset-today-payments`, {
      method: 'POST',
    });
    if (!res.ok) throw new Error('Failed to reset today payments');
    return res.json();
  },

  async registerOwner(data: {
    store_name: string;
    owner_name: string;
    phone?: string;
    language_preference?: string;
  }) {
    const res = await fetch(`${API_BASE}/owner/register`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });
    if (!res.ok) throw new Error('Failed to register store owner');
    return res.json();
  },
  // Voice Process REST Fallback
  async processTextVoice(text: string, language = 'hi-IN') {
    const res = await fetch(`${API_BASE}/voice/process-text`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text, language }),
    });
    if (!res.ok) throw new Error('Voice command processing failed');
    return res.json();
  },

  // Health
  async checkHealth() {
    try {
      const res = await fetch('/health');
      return res.ok;
    } catch {
      return false;
    }
  }
};
