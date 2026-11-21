"""
BolKhata - DPDP Act Compliance & Data Privacy Router
Digital Personal Data Protection (DPDP) Act Compliance:
1. Consent & Opt-in management for reminders
2. Encrypted data export for portability
3. Right to be forgotten (customer data purge)
4. Temporary demo transcript purge after judging
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import Customer, Transaction
from app.services.ledger_engine import LedgerEngine
from app.services.reminder_service import reminder_service
from app.utils.encryption import encrypt_text

router = APIRouter(prefix="/api/compliance", tags=["Compliance & DPDP"])


@router.post("/consent/{customer_id}")
async def update_customer_consent(
    customer_id: int,
    opt_in: bool = Query(..., description="Opt-in consent for polite payment reminders"),
    db: AsyncSession = Depends(get_db),
):
    """
    Record or revoke customer consent for ledger reminders (DPDP Act).
    """
    result = await db.execute(select(Customer).where(Customer.id == customer_id))
    customer = result.scalars().first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    customer.opted_in_reminders = opt_in
    await db.commit()
    await db.refresh(customer)

    status_str = "opted in" if opt_in else "opted out"
    return {
        "success": True,
        "customer_id": customer.id,
        "customer_name": customer.name,
        "opted_in_reminders": customer.opted_in_reminders,
        "message": f"Customer consent updated: {customer.name} is now {status_str}.",
    }


@router.get("/reminder/{customer_id}")
async def get_customer_reminder(
    customer_id: int,
    language: str = Query("hi-IN"),
    db: AsyncSession = Depends(get_db),
):
    """
    Generate a polite reminder with Responsible AI checks.
    Fails if customer is not opted in or balance <= 0.
    """
    result = await db.execute(select(Customer).where(Customer.id == customer_id))
    customer = result.scalars().first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    ledger = LedgerEngine(db)
    balance = await ledger.get_customer_balance(customer.id)

    reminder_data = reminder_service.generate_polite_reminder(
        customer=customer,
        balance=balance,
        language=language,
    )
    return reminder_data


@router.get("/export/{customer_id}")
async def export_customer_data(
    customer_id: int,
    db: AsyncSession = Depends(get_db),
):
    """
    DPDP Right to Data Portability:
    Export customer profile and transactions in an encrypted payload.
    """
    result = await db.execute(select(Customer).where(Customer.id == customer_id))
    customer = result.scalars().first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    ledger = LedgerEngine(db)
    balance = await ledger.get_customer_balance(customer.id)
    txns = await ledger.get_customer_transactions(customer.id)

    raw_payload = {
        "customer": {
            "id": customer.id,
            "name": customer.name,
            "phone": customer.phone,
            "opted_in": customer.opted_in_reminders,
            "balance": balance,
        },
        "transactions": [
            {
                "id": t.id,
                "amount": t.amount,
                "direction": t.direction,
                "date": str(t.transaction_date),
                "note": t.note,
            }
            for t in txns
        ],
    }

    import json
    encrypted_blob = encrypt_text(json.dumps(raw_payload))

    return {
        "customer_id": customer.id,
        "dpdp_compliant": True,
        "format": "AES-256 encrypted payload",
        "encrypted_data": encrypted_blob,
        "unencrypted_preview": {
            "name": customer.name,
            "transaction_count": len(txns),
            "balance": balance,
        },
    }


@router.delete("/purge-demo-transcripts")
async def purge_demo_transcripts(
    db: AsyncSession = Depends(get_db),
):
    """
    DPDP Act Requirement for Hackathons:
    'transcripts are encrypted at rest and deleted after judging.'
    Purges all stored STT raw transcripts while preserving final ledger balances.
    """
    txns = await db.execute(select(Transaction))
    for t in txns.scalars():
        t.raw_transcript = None
    await db.commit()

    return {
        "success": True,
        "message": "All demo audio/text transcripts successfully wiped in accordance with DPDP rules.",
    }
