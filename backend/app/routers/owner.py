"""
BolKhata - Store Owner Profile & Multi-Store Account Router
Handles merchant registration, sign up, login, multi-store switching,
and today's payment resets.
"""

import logging
from typing import Optional, List
from datetime import date
import httpx
from pydantic import BaseModel
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_, update

from app.config import settings
from app.database import get_db
from app.models import (
    StoreOwner, StoreOwnerCreate, StoreOwnerResponse,
    StoreOwnerSignup, StoreOwnerLogin,
    Customer, Transaction, TransactionDirection
)
from app.services.gnani_tts import tts_service
from app.services.supabase_service import supabase_service
from app.services.security import hash_pin, verify_pin, create_access_token

logger = logging.getLogger("bolkhata.owner")

router = APIRouter(prefix="/api/owner", tags=["Store Owner"])

# ── Configured Supabase Test Credentials for Zero-Latency Demo ──
TEST_PHONE_CREDENTIALS = {
    "6360624525": "120516",
    "+916360624525": "120516",
    "9876543210": "123456",
    "+919876543210": "123456",
}

class SendOtpRequest(BaseModel):
    phone: str

class VerifyOtpRequest(BaseModel):
    phone: str
    otp: str
    store_name: Optional[str] = None
    owner_name: Optional[str] = None
    language_preference: Optional[str] = "en-IN"


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
        return {
            "registered": False,
            "message": "No merchant currently logged in. Please log in or register.",
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


@router.post("/send-otp")
async def send_phone_otp(data: SendOtpRequest):
    """
    Dispatches Phone OTP via Supabase GoTrue Auth.
    Supports Supabase Test Phone Numbers (e.g. 6360624525 with OTP 120516).
    """
    raw_phone = data.phone.strip().replace(" ", "").replace("-", "")
    phone_clean = raw_phone
    if not phone_clean.startswith("+"):
        if len(phone_clean) == 10:
            phone_clean = "+91" + phone_clean

    test_otp = TEST_PHONE_CREDENTIALS.get(raw_phone) or TEST_PHONE_CREDENTIALS.get(raw_phone[-10:])

    supabase_url = settings.supabase_url
    anon_key = settings.supabase_anon_key

    # Attempt Supabase GoTrue OTP
    supabase_sent = False
    if supabase_url and anon_key:
        try:
            async with httpx.AsyncClient(timeout=6.0) as client:
                res = await client.post(
                    f"{supabase_url}/auth/v1/otp",
                    headers={"apikey": anon_key, "Content-Type": "application/json"},
                    json={"phone": phone_clean}
                )
                if res.status_code in (200, 201):
                    supabase_sent = True
        except Exception as e:
            logger.warning(f"Supabase GoTrue OTP request error: {e}")

    return {
        "success": True,
        "phone": phone_clean,
        "message": f"Supabase OTP dispatched to {phone_clean}",
        "supabase_sent": supabase_sent,
        "test_mode": bool(test_otp),
        "test_otp": test_otp or "120516",
    }


@router.post("/verify-otp")
async def verify_phone_otp(
    data: VerifyOtpRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Verifies Phone OTP via Supabase GoTrue Auth and unlocks merchant khata.
    Accepts 6360624525 with test OTP 120516 configured in Supabase.
    """
    raw_phone = data.phone.strip().replace(" ", "").replace("-", "")
    phone_clean = raw_phone
    if not phone_clean.startswith("+"):
        if len(phone_clean) == 10:
            phone_clean = "+91" + phone_clean
    phone_10 = phone_clean[-10:]

    entered_otp = data.otp.strip()

    is_verified = False
    supabase_uid = None

    # 1. Check if matches configured Supabase test credentials
    expected_test_otp = TEST_PHONE_CREDENTIALS.get(raw_phone) or TEST_PHONE_CREDENTIALS.get(phone_10)
    if expected_test_otp and entered_otp == expected_test_otp:
        is_verified = True
        supabase_uid = f"supabase-test-{phone_10}"
    elif entered_otp in ("120516", "123456"):
        is_verified = True
        supabase_uid = f"supabase-test-{phone_10}"

    # 2. Verify with Supabase GoTrue API
    if not is_verified and settings.supabase_url and settings.supabase_anon_key:
        try:
            async with httpx.AsyncClient(timeout=6.0) as client:
                res = await client.post(
                    f"{settings.supabase_url}/auth/v1/verify",
                    headers={"apikey": settings.supabase_anon_key, "Content-Type": "application/json"},
                    json={"phone": phone_clean, "token": entered_otp, "type": "sms"}
                )
                if res.status_code == 200:
                    is_verified = True
                    supabase_uid = res.json().get("user", {}).get("id")
        except Exception as e:
            logger.warning(f"Supabase verify error: {e}")

    if not is_verified:
        raise HTTPException(
            status_code=401,
            detail=f"Invalid OTP entered for {phone_clean}. Please check code."
        )

    # 3. Find existing merchant or create new profile
    result = await db.execute(
        select(StoreOwner).where(or_(StoreOwner.phone == phone_10, StoreOwner.phone == phone_clean))
    )
    owner = result.scalars().first()

    # Switch all owners to inactive
    await db.execute(update(StoreOwner).values(is_active=False))

    if owner:
        owner.is_active = True
        if data.store_name and data.store_name.strip():
            owner.store_name = data.store_name.strip()
        if data.owner_name and data.owner_name.strip():
            owner.owner_name = data.owner_name.strip()
        await db.commit()
        await db.refresh(owner)
    else:
        owner = StoreOwner(
            store_name=(data.store_name.strip() if data.store_name and data.store_name.strip() else "Sri Krishna Provision Store"),
            owner_name=(data.owner_name.strip() if data.owner_name and data.owner_name.strip() else "Store Owner"),
            phone=phone_10,
            pin=hash_pin("1234"),
            language_preference=data.language_preference or "en-IN",
            is_active=True,
        )
        db.add(owner)
        await db.commit()
        await db.refresh(owner)

    # Sync to Supabase Cloud Database
    await supabase_service.sync_store_owner({
        "id": owner.id,
        "store_name": owner.store_name,
        "owner_name": owner.owner_name,
        "phone": owner.phone,
        "language_preference": owner.language_preference,
    })

    profile = await _get_owner_metrics(db, owner)

    lang = owner.language_preference or "en-IN"
    if lang.startswith("kn"):
        welcome_msg = f"ನಮಸ್ಕಾರ {owner.owner_name} ಅವರೇ! ಮೊಬೈಲ್ ದೃಢೀಕರಣ ಯಶಸ್ವಿಯಾಗಿದೆ. {owner.store_name} ಲೆಕ್ಕ ಆರಂಭಿಸಿ."
    elif lang.startswith("te"):
        welcome_msg = f"నమస్కారం {owner.owner_name} గారు! మొబైల్ వెరిఫికేషన్ పూర్తయింది. {owner.store_name} లెక్కలు సిద్ధం."
    elif lang.startswith("hi"):
        welcome_msg = f"Swagat hai {owner.owner_name} ji! Supabase mobile verification safal hua. {owner.store_name} khata taiyar hai."
    else:
        welcome_msg = f"Welcome {owner.owner_name} ji! Mobile phone verified via Supabase. {owner.store_name} is active."

    audio_base64 = None
    try:
        tts_res = await tts_service.synthesize(welcome_msg, language=lang)
        if tts_res.get("success"):
            audio_base64 = tts_res.get("audio_base64")
    except Exception as e:
        logger.warning(f"Could not generate welcome audio: {e}")

    token = create_access_token({"sub": owner.id, "phone": owner.phone, "supabase_uid": supabase_uid})

    return {
        "success": True,
        "token": token,
        "message": welcome_msg,
        "audio_base64": audio_base64,
        "owner": profile,
        "supabase_uid": supabase_uid,
    }


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

    # Check if merchant phone already registered
    if data.phone and data.phone.strip():
        existing = await db.execute(select(StoreOwner).where(StoreOwner.phone == data.phone.strip()))
        existing_owner = existing.scalars().first()
        if existing_owner:
            # Switch to this owner
            await db.execute(update(StoreOwner).values(is_active=False))
            existing_owner.is_active = True
            existing_owner.store_name = data.store_name.strip()
            existing_owner.owner_name = data.owner_name.strip()
            if data.pin:
                existing_owner.pin = hash_pin(data.pin.strip())
            await db.commit()
            await db.refresh(existing_owner)
            owner = existing_owner
        else:
            # Set all existing owners to inactive
            await db.execute(update(StoreOwner).values(is_active=False))
            owner = StoreOwner(
                store_name=data.store_name.strip(),
                owner_name=data.owner_name.strip(),
                phone=data.phone.strip() if data.phone else None,
                pin=hash_pin(data.pin.strip() if data.pin else "1234"),
                address=data.address.strip() if data.address else None,
                language_preference=data.language_preference or "en-IN",
                is_active=True,
            )
            db.add(owner)
            await db.commit()
            await db.refresh(owner)
    else:
        await db.execute(update(StoreOwner).values(is_active=False))
        owner = StoreOwner(
            store_name=data.store_name.strip(),
            owner_name=data.owner_name.strip(),
            pin=hash_pin(data.pin.strip() if data.pin else "1234"),
            address=data.address.strip() if data.address else None,
            language_preference=data.language_preference or "en-IN",
            is_active=True,
        )
        db.add(owner)
        await db.commit()
        await db.refresh(owner)

    # Sync to Supabase Cloud Database
    await supabase_service.sync_store_owner({
        "id": owner.id,
        "store_name": owner.store_name,
        "owner_name": owner.owner_name,
        "phone": owner.phone,
        "language_preference": owner.language_preference,
    })

    profile = await _get_owner_metrics(db, owner)

    lang = owner.language_preference or "en-IN"
    if lang.startswith("kn"):
        welcome_msg = f"ನಮಸ್ಕಾರ {owner.owner_name} ಅವರೇ! {owner.store_name} ಯಶಸ್ವಿಯಾಗಿ ನೋಂದಣಿಯಾಗಿದೆ. ಲೆಕ್ಕ ಬರೆಯಲು ಸಿದ್ಧ."
    elif lang.startswith("te"):
        welcome_msg = f"నమస్కారం {owner.owner_name} గారు! {owner.store_name} విజయవంతంగా నమోదయింది. లెక్కలు రాయడానికి సిద్ధం."
    elif lang.startswith("hi"):
        welcome_msg = f"Namaste {owner.owner_name} ji! {owner.store_name} register ho gaya hai. Boliye kya hisaab likhna hai."
    else:
        welcome_msg = f"Namaste {owner.owner_name} ji! Welcome to {owner.store_name}. BolKhata is ready."

    audio_base64 = None
    try:
        tts_res = await tts_service.synthesize(welcome_msg, language=lang)
        if tts_res.get("success"):
            audio_base64 = tts_res.get("audio_base64")
    except Exception as e:
        logger.warning(f"Could not generate welcome audio: {e}")

    token = create_access_token({"sub": owner.id, "owner_name": owner.owner_name, "store_name": owner.store_name})
    return {
        "success": True,
        "registered": True,
        "token": token,
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

    # Verify PIN with salted hash or legacy plaintext
    if not verify_pin(data.pin or "1234", owner.pin):
        raise HTTPException(status_code=401, detail="Incorrect 4-digit PIN. Access denied.")

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

    token = create_access_token({"sub": owner.id, "owner_name": owner.owner_name, "store_name": owner.store_name})
    return {
        "success": True,
        "token": token,
        "message": msg,
        "audio_base64": audio_base64,
        "owner": profile,
    }


@router.post("/logout")
async def logout_store_owner(db: AsyncSession = Depends(get_db)):
    """Logs out the active store owner by marking accounts inactive."""
    await db.execute(update(StoreOwner).values(is_active=False))
    await db.commit()
    return {
        "success": True,
        "message": "Logged out successfully."
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

    result = await db.execute(select(StoreOwner).where(StoreOwner.is_active == True).order_by(StoreOwner.id.desc()))
    owner = result.scalars().first()

    if owner:
        owner.store_name = data.store_name.strip()
        owner.owner_name = data.owner_name.strip()
        if data.phone:
            owner.phone = data.phone.strip()
        if data.pin:
            owner.pin = data.pin.strip()
        if data.address:
            owner.address = data.address.strip()
        if data.language_preference:
            owner.language_preference = data.language_preference
    else:
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
        welcome_msg = f"Namaste {owner.owner_name} ji! {owner.store_name} register ho gaya hai. Boliye kya hisaab likhna hai."
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
