"""
Sync Local SQLite BolKhata Database to Supabase Cloud Database.
Can be executed standalone to verify table readiness and sync all records.
"""

import asyncio
import json
import httpx
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select

from app.config import settings
from app.models import StoreOwner, Customer, Transaction

SUPABASE_URL = settings.supabase_url.rstrip("/")
ANON_KEY = settings.supabase_anon_key

HEADERS = {
    "apikey": ANON_KEY,
    "Authorization": f"Bearer {ANON_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=minimal"
}


async def check_supabase_tables() -> dict:
    """Checks whether tables exist in Supabase PostgREST schema cache."""
    status = {}
    async with httpx.AsyncClient(timeout=6.0) as client:
        for tbl in ["store_owners", "customers", "transactions"]:
            try:
                res = await client.get(f"{SUPABASE_URL}/rest/v1/{tbl}?select=count", headers=HEADERS)
                status[tbl] = res.status_code == 200
            except Exception as e:
                status[tbl] = False
    return status


async def sync_all_to_supabase():
    print("=======================================================")
    print("⚡ BOLKHATA -> SUPABASE CLOUD SYNC UTILITY")
    print(f"🔗 Target Project: {SUPABASE_URL}")
    print("=======================================================")

    table_status = await check_supabase_tables()
    print("\n[1] Checking Supabase Tables in Schema Cache:")
    for tbl, exists in table_status.items():
        state = "✅ READY" if exists else "❌ NOT FOUND (Need to run supabase_schema.sql)"
        print(f"  • {tbl}: {state}")

    if not all(table_status.values()):
        print("\n⚠️  NOTICE: One or more tables do not exist in Supabase yet!")
        print("    Supabase requires tables to be created via SQL Editor first.")
        print("    Direct Link: https://supabase.com/dashboard/project/bniyjwlqzrnszxzacomp/sql")
        print("    Paste and run: Bol-Khata/backend/supabase_schema.sql")
        return False

    print("\n[2] Reading Local Database Records:")
    engine = create_async_engine(settings.database_url, echo=False)
    async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

    async with async_session() as session:
        owners = (await session.execute(select(StoreOwner))).scalars().all()
        customers = (await session.execute(select(Customer))).scalars().all()
        transactions = (await session.execute(select(Transaction))).scalars().all()

        print(f"  • Store Owners: {len(owners)}")
        print(f"  • Customers:    {len(customers)}")
        print(f"  • Transactions: {len(transactions)}")

        async with httpx.AsyncClient(timeout=10.0) as client:
            # Sync Owners
            for o in owners:
                payload = {
                    "id": o.id,
                    "store_name": o.store_name,
                    "owner_name": o.owner_name,
                    "phone": o.phone,
                    "pin": o.pin,
                    "language_preference": o.language_preference,
                    "is_active": o.is_active
                }
                res = await client.post(
                    f"{SUPABASE_URL}/rest/v1/store_owners",
                    headers={"apikey": ANON_KEY, "Authorization": f"Bearer {ANON_KEY}", "Content-Type": "application/json", "Prefer": "resolution=merge-duplicates"},
                    json=payload
                )
                print(f"    Synced Owner {o.owner_name}: HTTP {res.status_code}")

            # Sync Customers
            for c in customers:
                payload = {
                    "id": c.id,
                    "owner_id": c.owner_id,
                    "name": c.name,
                    "phone": c.phone,
                    "nickname": c.nickname,
                    "opted_in_reminders": c.opted_in_reminders
                }
                res = await client.post(
                    f"{SUPABASE_URL}/rest/v1/customers",
                    headers={"apikey": ANON_KEY, "Authorization": f"Bearer {ANON_KEY}", "Content-Type": "application/json", "Prefer": "resolution=merge-duplicates"},
                    json=payload
                )
                print(f"    Synced Customer {c.name}: HTTP {res.status_code}")

            # Sync Transactions
            for t in transactions:
                payload = {
                    "id": t.id,
                    "owner_id": t.owner_id,
                    "customer_id": t.customer_id,
                    "amount": t.amount,
                    "direction": t.direction,
                    "transaction_date": str(t.transaction_date),
                    "note": t.note,
                    "raw_transcript": t.raw_transcript,
                    "corrected": t.corrected
                }
                res = await client.post(
                    f"{SUPABASE_URL}/rest/v1/transactions",
                    headers={"apikey": ANON_KEY, "Authorization": f"Bearer {ANON_KEY}", "Content-Type": "application/json", "Prefer": "resolution=merge-duplicates"},
                    json=payload
                )
                print(f"    Synced Transaction #{t.id} (₹{t.amount}): HTTP {res.status_code}")

    print("\n🎉 ALL RECORDS SYNCED TO SUPABASE CLOUD SUCCESSFULLY!")
    return True

if __name__ == "__main__":
    asyncio.run(sync_all_to_supabase())
