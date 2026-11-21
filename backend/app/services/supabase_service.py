"""
BolKhata - Supabase Cloud Database Integration Service
Connects to Supabase REST / PostgREST API with configured Anon Key.
Synchronizes Store Owners, Customers, and Ledger Transactions in real-time.
"""

import logging
from typing import Optional, Dict, Any, List
import httpx
from sqlalchemy.ext.asyncio import AsyncSession
from app.config import settings

logger = logging.getLogger("bolkhata.supabase")


class SupabaseService:
    """Async service to interact with Supabase database."""

    def __init__(self):
        self.url = settings.supabase_url.rstrip("/")
        self.anon_key = settings.supabase_anon_key
        self.headers = {
            "apikey": self.anon_key,
            "Authorization": f"Bearer {self.anon_key}",
            "Content-Type": "application/json",
            "Prefer": "resolution=merge-duplicates"
        }

    async def get_cloud_status(self) -> Dict[str, Any]:
        """Checks connectivity and table existence in Supabase project."""
        try:
            async with httpx.AsyncClient(timeout=4.0) as client:
                res = await client.get(f"{self.url}/auth/v1/health", headers={"apikey": self.anon_key})
                connected = (res.status_code == 200)

                tables = {}
                for tbl in ["store_owners", "customers", "transactions"]:
                    try:
                        t_res = await client.get(f"{self.url}/rest/v1/{tbl}?select=count", headers=self.headers)
                        tables[tbl] = (t_res.status_code == 200)
                    except Exception:
                        tables[tbl] = False

                tables_ready = all(tables.values())

                return {
                    "connected": connected,
                    "tables_ready": tables_ready,
                    "tables": tables,
                    "url": self.url,
                    "service": "Supabase Cloud Database",
                    "status": "online" if (connected and tables_ready) else ("tables_pending" if connected else "offline")
                }
        except Exception as e:
            logger.warning(f"Supabase health check notice: {e}")
            return {
                "connected": False,
                "tables_ready": False,
                "url": self.url,
                "service": "Supabase Cloud Database",
                "error": str(e)
            }

    async def sync_store_owner(self, owner_data: Dict[str, Any]) -> bool:
        """Upserts a store owner profile to Supabase."""
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                res = await client.post(
                    f"{self.url}/rest/v1/store_owners",
                    headers=self.headers,
                    json=owner_data
                )
                if res.status_code in (200, 201, 204):
                    logger.info(f"✅ Synced store owner '{owner_data.get('owner_name')}' to Supabase")
                    return True
        except Exception as e:
            logger.warning(f"Supabase sync notice for owner: {e}")
        return False

    async def sync_customer(self, customer_data: Dict[str, Any]) -> bool:
        """Upserts a customer record to Supabase."""
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                res = await client.post(
                    f"{self.url}/rest/v1/customers",
                    headers=self.headers,
                    json=customer_data
                )
                if res.status_code in (200, 201, 204):
                    logger.info(f"✅ Synced customer '{customer_data.get('name')}' to Supabase")
                    return True
        except Exception as e:
            logger.warning(f"Supabase sync notice for customer: {e}")
        return False

    async def sync_transaction(self, txn_data: Dict[str, Any]) -> bool:
        """Pushes a ledger transaction entry to Supabase."""
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                res = await client.post(
                    f"{self.url}/rest/v1/transactions",
                    headers=self.headers,
                    json=txn_data
                )
                if res.status_code in (200, 201, 204):
                    logger.info(f"✅ Synced transaction to Supabase (₹{txn_data.get('amount')})")
                    return True
        except Exception as e:
            logger.warning(f"Supabase sync notice for transaction: {e}")
        return False

    async def sync_all_database(self, db: AsyncSession) -> Dict[str, Any]:
        """Syncs all SQLite owners, customers, and transactions to Supabase."""
        from app.models import StoreOwner, Customer, Transaction
        from sqlalchemy import select

        owners = (await db.execute(select(StoreOwner))).scalars().all()
        customers = (await db.execute(select(Customer))).scalars().all()
        txns = (await db.execute(select(Transaction))).scalars().all()

        synced_counts = {"owners": 0, "customers": 0, "transactions": 0}

        async with httpx.AsyncClient(timeout=8.0) as client:
            for o in owners:
                payload = {
                    "id": o.id,
                    "store_name": o.store_name,
                    "owner_name": o.owner_name,
                    "phone": o.phone,
                    "pin": o.pin,
                    "language_preference": o.language_preference,
                    "is_active": o.is_active,
                }
                res = await client.post(f"{self.url}/rest/v1/store_owners", headers=self.headers, json=payload)
                if res.status_code in (200, 201, 204):
                    synced_counts["owners"] += 1

            for c in customers:
                payload = {
                    "id": c.id,
                    "owner_id": c.owner_id,
                    "name": c.name,
                    "phone": c.phone,
                    "nickname": c.nickname,
                    "opted_in_reminders": c.opted_in_reminders,
                }
                res = await client.post(f"{self.url}/rest/v1/customers", headers=self.headers, json=payload)
                if res.status_code in (200, 201, 204):
                    synced_counts["customers"] += 1

            for t in txns:
                payload = {
                    "id": t.id,
                    "owner_id": t.owner_id,
                    "customer_id": t.customer_id,
                    "amount": t.amount,
                    "direction": t.direction,
                    "transaction_date": str(t.transaction_date),
                    "note": t.note,
                    "raw_transcript": t.raw_transcript,
                    "corrected": t.corrected,
                }
                res = await client.post(f"{self.url}/rest/v1/transactions", headers=self.headers, json=payload)
                if res.status_code in (200, 201, 204):
                    synced_counts["transactions"] += 1

        return {"success": True, "synced": synced_counts}


supabase_service = SupabaseService()
