import Dexie, { type EntityTable } from 'dexie';
import type { Customer, Entry, OutboxEntry } from '../types';

export class BolKhataDatabase extends Dexie {
  customers!: EntityTable<Customer, 'id'>;
  entries!: EntityTable<Entry, 'id'>;
  outbox!: EntityTable<OutboxEntry, 'id'>;

  constructor() {
    super('BolKhataDB');
    this.version(1).stores({
      customers: '++id, name, balance, opted_in_reminders',
      entries: '++id, remote_id, customer_id, customer_name, type, transaction_date, status, created_at',
      outbox: '++id, customer_name, created_at, synced'
    });
  }
}

export const db = new BolKhataDatabase();
