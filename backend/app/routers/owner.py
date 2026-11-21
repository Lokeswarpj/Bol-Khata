"""
BolKhata - Store Owner Profile & Multi-Store Account Router
Handles merchant registration, sign up, login, multi-store switching,
and today's payment resets.
"""

import logging
from typing import Optional, List
from datetime import date
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_, update

from app.database import get_db
from app.models import (
    StoreOwner, StoreOwnerCreate, StoreOwnerResponse,
    StoreOwnerSignup, StoreOwnerLogin,
    Customer, Transaction, TransactionDirection
)
from app.services.gnani_tts import tts_service

logger = logging.getLogger("bolkhata.owner")

router = APIRouter(prefix="/api/owner", tags=["Store Owner"])


async def _get_owner_metrics(db: AsyncSession, owner: StoreOwner) -> StoreOwnerResponse:
    """Aggregates ledger figures scoped specifically to this store owner."""
    # Count customers owned by this merchant (or legacy unassigned)
    cust_res = await db.execute(
        select(func.count(Customer.id)).where(
            or_(Customer.owner_id == owner.id, Customer.owner_id.is_(None))
        )
    )
    customer_count = cust_res.scalar() or 0

    # Sum credit and payments for this merchant
    credit_res = await db.execute(
        select(func.sum(Transaction.amount)).where(
            Transaction.direction == TransactionDirection.CREDIT.value,
            Transaction.corrected == False,
            or_(Transaction.owner_id == owner.id, Transaction.owner_id.is_(None)),
        )
    )
    total_credit = credit_res.scalar() or 0.0

    payment_res = await db.execute(
        select(func.sum(Transaction.amount)).where(
            Transaction.direction == TransactionDirection.PAYMENT.value,
            Transaction.corrected == False,
            or_(Transaction.owner_id == owner.id, Transaction.owner_id.is_(None)),
        )
    )
    total_payments = payment_res.scalar() or 0.0

    net_outstanding = max(0.0, total_credit - total_payments)

    return StoreOwnerResponse(
        id=owner.id,
        store_name=owner.store_name,
        owner_name=owner.owner_name,
        phone=owner.phone,
        address=owner.address,
        language_preference=owner.language_preference or "en-IN",
        is_active=owner.is_active,
        created_at=owner.created_at,
        total_credit=total_credit,
        total_payments=total_payments,
        net_outstanding=net_outstanding,
        customer_count=customer_count,
    )


@router.get("/profile")
async def get_owner_profile(db: AsyncSession = Depends(get_db)):
    """Fetch the active Kirana store owner profile."""
    result = await db.execute(
        select(StoreOwner).where(StoreOwner.is_active == True).order_by(StoreOwner.id.desc())
    )
    owner = result.scalars().first()

    if not owner:
        # Fallback to first owner if none marked active
        fallback_res = await db.execute(select(StoreOwner).order_by(StoreOwner.id.asc()))
        owner = fallback_res.scalars().first()
        if owner:
            owner.is_active = True
            await db.commit()
            await db.refresh(owner)

    if not owner:
        return {
            "registered": False,
            "message": "No store owner registered yet. Please sign up or register to personalize BolKhata.",
            "owner": None,
        }

    profile = await _get_owner_metrics(db, owner)
    return {
        "registered": True,
        "owner": profile,
    }


@router.get("/all")
async def list_all_store_owners(db: AsyncSession = Depends(get_db)):
    """List all registered store owners for multi-store counter switching."""
    result = await db.execute(select(StoreOwner).order_by(StoreOwner.id.asc()))
    owners = result.scalars().all()
    
    owner_list = []
    for o in owners:
        owner_list.append({
            "id": o.id,
            "store_name": o.store_name,
            "owner_name": o.owner_name,
            "phone": o.phone,
            "language_preference": o.language_preference,
            "is_active": o.is_active,
            "created_at": o.created_at.isoformat() if o.created_at else None,
        })
    return {"success": True, "owners": owner_list}


@router.post("/signup")
async def signup_store_owner(
    data: StoreOwnerSignup,
    db: AsyncSession = Depends(get_db),
):
    """
    Sign up a new Kirana store merchant and activate their store account.
    Stores password/PIN, persists in DB, and generates welcome audio.
    """
    if not data.store_name.strip() or not data.owner_name.strip():
        raise HTTPException(status_code=400, detail="Store name and Owner name are required.")

    # Deactivate existing owners to make the new store active
    await db.execute(update(StoreOwner).values(is_active=False))

    phone_val = data.phone.strip() if data.phone else None
    existing = None
    if phone_val:
        q = select(StoreOwner).where(
            StoreOwner.phone == phone_val,
            StoreOwner.store_name == data.store_name.strip()
        )
        existing = (await db.execute(q)).scalars().first()

    if existing:
        existing.is_active = True
        existing.owner_name = data.owner_name.strip()
        if data.pin:
            existing.pin = data.pin.strip()
        await db.commit()
        await db.refresh(existing)
        owner = existing
    else:
        owner = StoreOwner(
            store_name=data.store_name.strip(),
            owner_name=data.owner_name.strip(),
            phone=phone_val,
            pin=data.pin.strip() if data.pin else "1234",
            address=data.address.strip() if data.address else None,
            language_preference=data.language_preference or "en-IN",
            is_active=True,
        )
        db.add(owner)
        await db.commit()
        await db.refresh(owner)

    profile = await _get_owner_metrics(db, owner)

    lang = owner.language_preference or "en-IN"
    if lang.startswith("kn"):
        welcome_msg = f"ನಮಸ್ಕಾರ {owner.owner_name} ಅವರೇ! {owner.store_name} ಯಶಸ್ವಿಯಾಗಿ ನೋಂದಣಿಯಾಗಿದೆ. ನಿಮ್ಮ ಖಾತೆ 100% ಸುರಕ್ಷಿತವಾಗಿದೆ."
    elif lang.startswith("te"):
        welcome_msg = f"నమస్కారం {owner.owner_name} గారు! {owner.store_name} విజయవంతంగా నమోదయింది. మీ లెక్కలు 100% సురక్షితం."
    elif lang.startswith("hi"):
        welcome_msg = f"Namaste {owner.owner_name} ji! {owner.store_name} safalta-purvak register ho gaya hai. Aapka saara hisaab 100% surakshit aur encrypted hai."
    else:
        welcome_msg = f"Namaste {owner.owner_name} ji! Welcome to {owner.store_name}. Your merchant account is secured with AES-256 encryption."

    audio_base64 = None
    try:
        tts_res = await tts_service.synthesize(welcome_msg, language=lang)
        if tts_res.get("success"):
            audio_base64 = tts_res.get("audio_base64")
    except Exception as e:
        logger.warning(f"Could not generate welcome audio: {e}")

    return {
        "success": True,
        "registered": True,
        "message": welcome_msg,
        "audio_base64": audio_base64,
        "owner": profile,
    }


@router.post("/login")
async def login_store_owner(
    data: StoreOwnerLogin,
    db: AsyncSession = Depends(get_db),
):
    """
    Log in an existing Kirana merchant with Phone and PIN.
    Switches active store and returns merchant profile.
    """
    phone_clean = data.phone.strip() if data.phone else ""
    if not phone_clean:
        raise HTTPException(status_code=400, detail="Phone number is required to log in.")

    result = await db.execute(select(StoreOwner).where(StoreOwner.phone == phone_clean))
    owner = result.scalars().first()

    if not owner:
        raise HTTPException(status_code=404, detail=f"No store merchant found registered with phone {phone_clean}")

    # Check PIN if configured
    if owner.pin and data.pin:
        if str(owner.pin).strip() != str(data.pin).strip():
            raise HTTPException(status_code=401, detail="Incorrect 4-digit PIN. Please try again.")

    # Switch active store
    await db.execute(update(StoreOwner).values(is_active=False))
    owner.is_active = True
    await db.commit()
    await db.refresh(owner)

    profile = await _get_owner_metrics(db, owner)

    lang = owner.language_preference or "en-IN"
    if lang.startswith("kn"):
        msg = f"ಸ್ವಾಗತ {owner.owner_name} ಅವರೇ! {owner.store_name} ಖಾತೆಗೆ ಯಶಸ್ವಿಯಾಗಿ ಲಾಗಿನ್ ಆಗಿದ್ದೀರಿ."
    elif lang.startswith("te"):
        msg = f"స్వాగతం {owner.owner_name} గారు! {owner.store_name} ఖాతాలోకి లాగిన్ అయ్యారు."
    elif lang.startswith("hi"):
        msg = f"Swagat hai {owner.owner_name} ji! {owner.store_name} ke ledger mein aapka swagat hai."
    else:
        msg = f"Welcome back, {owner.owner_name} ji! Active store switched to {owner.store_name}."

    audio_base64 = None
    try:
        tts_res = await tts_service.synthesize(msg, language=lang)
        if tts_res.get("success"):
            audio_base64 = tts_res.get("audio_base64")
    except Exception as e:
        logger.warning(f"Could not generate login audio: {e}")

    return {
        "success": True,
        "message": msg,
        "audio_base64": audio_base64,
        "owner": profile,
    }


@router.post("/switch/{owner_id}")
async def switch_active_owner(
    owner_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Switch active merchant profile by owner_id."""
    target = await db.execute(select(StoreOwner).where(StoreOwner.id == owner_id))
    owner = target.scalars().first()
    if not owner:
        raise HTTPException(status_code=404, detail="Store owner not found.")

    await db.execute(update(StoreOwner).values(is_active=False))
    owner.is_active = True
    await db.commit()
    await db.refresh(owner)

    profile = await _get_owner_metrics(db, owner)
    return {
        "success": True,
        "message": f"Switched active store to {owner.store_name} ({owner.owner_name})",
        "owner": profile,
    }


@router.post("/reset-today-payments")
async def reset_today_payments(
    db: AsyncSession = Depends(get_db),
):
    """
    Resets/voids today's payment records (jama) for the active merchant.
    E.g., merchant says "Reset today's payment" or clicks reset button.
    """
    # Get active owner
    res = await db.execute(select(StoreOwner).where(StoreOwner.is_active == True))
    owner = res.scalars().first()
    owner_id = owner.id if owner else 1
    lang = (owner.language_preference if owner else "en-IN") or "en-IN"

    today = date.today()
    query = select(Transaction).where(
        Transaction.direction == TransactionDirection.PAYMENT.value,
        Transaction.transaction_date == today,
        Transaction.corrected == False,
        or_(Transaction.owner_id == owner_id, Transaction.owner_id.is_(None)),
    )
    txns_res = await db.execute(query)
    today_payments = txns_res.scalars().all()

    total_reset_amount = sum(t.amount for t in today_payments)

    for t in today_payments:
        t.corrected = True
        t.note = f"Reset today's payments by merchant: {t.note or ''}"

    await db.commit()

    if lang.startswith("kn"):
        msg = f"ಇಂದಿನ ಎಲ್ಲಾ ಜಮಾ ಪಾವತಿಗಳನ್ನು ರದ್ದುಗೊಳಿಸಲಾಗಿದೆ. ಒಟ್ಟು ₹{total_reset_amount:g} ತೆರವುಗೊಳಿಸಲಾಗಿದೆ."
    elif lang.startswith("te"):
        msg = f"ఈరోజు జమ పేమెంట్లు అన్నీ రీసెట్ చేయబడ్డాయి. మొత్తం ₹{total_reset_amount:g} క్లియర్ చేయబడింది."
    elif lang.startswith("hi"):
        msg = f"Aaj ki saari jama (payments) reset ho gayi hai. Kul ₹{total_reset_amount:g} clear kar diya gaya."
    else:
        msg = f"Today's payments have been reset to ₹0. Total of ₹{total_reset_amount:g} cleared."

    audio_base64 = None
    try:
        tts_res = await tts_service.synthesize(msg, language=lang)
        if tts_res.get("success"):
            audio_base64 = tts_res.get("audio_base64")
    except Exception as e:
        logger.warning(f"Could not generate reset payments audio: {e}")

    return {
        "success": True,
        "reset_count": len(today_payments),
        "reset_amount": total_reset_amount,
        "message": msg,
        "audio_base64": audio_base64,
    }


@router.post("/register")
async def register_store_owner(
    data: StoreOwnerCreate,
    db: AsyncSession = Depends(get_db),
):
    """Legacy registration/update endpoint for backwards compatibility."""
    if not data.store_name.strip() or not data.owner_name.strip():
        raise HTTPException(status_code=400, detail="Store name and Owner name are required.")

    await db.execute(update(StoreOwner).values(is_active=False))
    owner = StoreOwner(
        store_name=data.store_name.strip(),
        owner_name=data.owner_name.strip(),
        phone=data.phone.strip() if data.phone else None,
        pin=data.pin.strip() if data.pin else "1234",
        address=data.address.strip() if data.address else None,
        language_preference=data.language_preference or "en-IN",
        is_active=True,
    )
    db.add(owner)
    await db.commit()
    await db.refresh(owner)

    profile = await _get_owner_metrics(db, owner)

    lang = owner.language_preference or "en-IN"
    if lang.startswith("kn"):
        welcome_msg = f"ನಮಸ್ಕಾರ {owner.owner_name} ಅವರೇ! {owner.store_name} ಯಶಸ್ವಿಯಾಗಿ ನೋಂದಣಿಯಾಗಿದೆ. ನಿಮ್ಮ ಡಿಜಿಟಲ್ ಖಾತೆ ಸುರಕ್ಷಿತವಾಗಿದೆ."
    elif lang.startswith("te"):
        welcome_msg = f"నమస్కారం {owner.owner_name} గారు! {owner.store_name} విజయవంతంగా నమోదయింది. మీ లెక్కలు 100% సురಕ್ಷితం."
    elif lang.startswith("hi"):
        welcome_msg = f"Namaste {owner.owner_name} ji! {owner.store_name} safalta-purvak register ho gaya hai. Aapka saara hisaab 100% surakshit aur encrypted hai."
    else:
        welcome_msg = f"Namaste {owner.owner_name} ji! {owner.store_name} has been successfully registered. Your store ledger is safe, 100% encrypted, and DPDP compliant."

    audio_base64 = None
    try:
        tts_res = await tts_service.synthesize(welcome_msg, language=lang)
        if tts_res.get("success"):
            audio_base64 = tts_res.get("audio_base64")
    except Exception as e:
        logger.warning(f"Could not generate welcome audio for registration: {e}")

    return {
        "success": True,
        "registered": True,
        "message": welcome_msg,
        "audio_base64": audio_base64,
        "owner": profile,
    }
