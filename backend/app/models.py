"""
BolKhata Database Models & Pydantic Schemas
Defines SQLAlchemy ORM models and API request/response schemas.
"""

from datetime import datetime, date
from typing import Optional, List, Literal
from enum import Enum

from sqlalchemy import (
    Column, Integer, String, Float, DateTime, Date,
    Boolean, Text, ForeignKey, Index
)
from sqlalchemy.orm import relationship, DeclarativeBase
from pydantic import BaseModel, Field


# ═══════════════════════════════════════════════════════════════
# SQLAlchemy ORM Models
# ═══════════════════════════════════════════════════════════════

class Base(DeclarativeBase):
    """Base class for all ORM models."""
    pass


class Customer(Base):
    """Customer (the person who takes udhaar)."""
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, autoincrement=True)
    owner_id = Column(Integer, ForeignKey("store_owners.id"), nullable=True, default=1, index=True)
    name = Column(String(100), nullable=False, index=True)
    phone = Column(String(15), nullable=True)
    nickname = Column(String(50), nullable=True)  # For disambiguation
    opted_in_reminders = Column(Boolean, default=False)  # Responsible AI: opt-in only
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    transactions = relationship("Transaction", back_populates="customer", lazy="selectin")

    __table_args__ = (
        Index("idx_customer_name_lower", "name"),
    )


class StoreOwner(Base):
    """Store Owner profile (the Kirana merchant)."""
    __tablename__ = "store_owners"

    id = Column(Integer, primary_key=True, autoincrement=True)
    store_name = Column(String(150), nullable=False)
    owner_name = Column(String(100), nullable=False)
    phone = Column(String(20), nullable=True, unique=True)
    pin = Column(String(50), default="1234")
    address = Column(String(200), nullable=True)
    language_preference = Column(String(20), default="en-IN")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Transaction(Base):
    """A single ledger entry (credit/udhaar or payment/jama)."""
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    owner_id = Column(Integer, ForeignKey("store_owners.id"), nullable=True, default=1, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False, index=True)
    amount = Column(Float, nullable=False)
    direction = Column(String(10), nullable=False)  # "credit" (udhaar) or "payment" (jama)
    transaction_date = Column(Date, default=date.today)
    note = Column(Text, nullable=True)  # Original spoken text
    raw_transcript = Column(Text, nullable=True)  # Full STT transcript
    corrected = Column(Boolean, default=False)  # Was this entry corrected?
    correction_of = Column(Integer, ForeignKey("transactions.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    customer = relationship("Customer", back_populates="transactions")


class SyncOutbox(Base):
    """Local SQLite outbox table for resilient, zero-loss offline-first cloud syncing."""
    __tablename__ = "sync_outbox"

    id = Column(Integer, primary_key=True, autoincrement=True)
    entity_type = Column(String(50), nullable=False)  # 'store_owner', 'customer', 'transaction'
    entity_id = Column(Integer, nullable=False)
    payload = Column(Text, nullable=False)  # JSON serialized data
    status = Column(String(20), default="pending")  # 'pending', 'synced', 'failed'
    attempts = Column(Integer, default=0)
    last_error = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


# ═══════════════════════════════════════════════════════════════
# Pydantic Schemas (API Request/Response)
# ═══════════════════════════════════════════════════════════════

class TransactionDirection(str, Enum):
    CREDIT = "credit"    # udhaar - customer owes
    PAYMENT = "payment"  # jama - customer paid


class IntentType(str, Enum):
    ADD_CREDIT = "add_credit"       # "Ramesh ka 340 udhaar"
    ADD_PAYMENT = "add_payment"     # "Ramesh ne 200 diya"
    CLEAR_DEBT = "clear_debt"       # "Ramesh cleared his debt" / "hisaab clear kar diya"
    RESET_TODAYS_PAYMENTS = "reset_todays_payments" # "Reset today's payments" / "Aaj ki jama reset karo"
    STOP_LISTENING = "stop_listening" # "Stop" / "Ruko" / "Bas"
    WAKE_UP = "wake_up"             # "BolKhata" / "Hey BolKhata"
    QUERY_BALANCE = "query_balance" # "Ramesh ka total?"
    QUERY_TODAY = "query_today"     # "Aaj kitna udhaar gaya?"
    QUERY_TOP_DEBTOR = "query_top_debtor" # "Sabse zyada udhaar kiska hai?" / "Who owes the most?"
    QUERY_CUSTOMERS_COUNT = "query_customers_count" # "Total customers kitne hain?"
    QUERY_COLLECTIONS_TODAY = "query_collections_today" # "Aaj kitna collection hua?"
    TRIGGER_REMINDER = "trigger_reminder" # "Ramesh ko reminder bhejo"
    CORRECTION = "correction"       # "nahi, 430"
    LIST_DUES = "list_dues"         # "Sabka hisaab bata"
    REGISTER_OWNER = "register_owner" # "Mera naam Niranjan hai, dukaan Sri Balaji Kirana"
    QUERY_OWNER = "query_owner"     # "Mera store kaisa chal raha hai?" / "Dukaan summary"
    CHITCHAT = "chitchat"           # Natural conversational chit-chat & greetings
    VOICE_TO_UPI = "voice_to_upi"   # "Ramesh se payment lo" / "Show UPI QR"
    CHECK_RISK = "check_risk"       # "Ramesh ka risk kaisa hai?" / "Khata Risk AI"
    UNKNOWN = "unknown"


# ── Request Schemas ───────────────────────────────────────────

class VoiceInput(BaseModel):
    """Raw voice input (audio bytes sent via WebSocket or REST)."""
    audio_base64: Optional[str] = None
    text: Optional[str] = None  # Pre-transcribed text (for testing)
    language: Optional[str] = None
    session_id: Optional[str] = "default_counter"
    owner_id: Optional[int] = None
    generate_audio: bool = True  # Automatically synthesize Gnani neural voice


class StoreOwnerSignup(BaseModel):
    """Merchant sign-up schema."""
    store_name: str
    owner_name: str
    phone: str
    pin: Optional[str] = "1234"
    address: Optional[str] = None
    language_preference: Optional[str] = "en-IN"


class StoreOwnerLogin(BaseModel):
    """Merchant login schema."""
    phone: str
    pin: Optional[str] = "1234"


class StoreOwnerCreate(BaseModel):
    """Register or update store owner profile."""
    store_name: str
    owner_name: str
    phone: Optional[str] = None
    pin: Optional[str] = "1234"
    address: Optional[str] = None
    language_preference: Optional[str] = "en-IN"


class StoreOwnerResponse(BaseModel):
    id: int
    store_name: str
    owner_name: str
    phone: Optional[str] = None
    address: Optional[str] = None
    language_preference: str = "en-IN"
    is_active: bool = True
    created_at: datetime
    total_credit: float = 0.0
    total_payments: float = 0.0
    net_outstanding: float = 0.0
    customer_count: int = 0

    class Config:
        from_attributes = True


class ManualTransactionCreate(BaseModel):
    """Create a transaction manually (REST API)."""
    customer_name: str
    amount: float = Field(gt=0)
    direction: TransactionDirection
    transaction_date: Optional[date] = None
    note: Optional[str] = None


class CustomerCreate(BaseModel):
    """Create a customer manually."""
    name: str
    phone: Optional[str] = None
    nickname: Optional[str] = None
    opted_in_reminders: bool = False


class CustomerUpdate(BaseModel):
    """Update customer details."""
    name: Optional[str] = None
    phone: Optional[str] = None
    nickname: Optional[str] = None
    opted_in_reminders: Optional[bool] = None


# ── Response Schemas ──────────────────────────────────────────

class CustomerResponse(BaseModel):
    id: int
    name: str
    phone: Optional[str]
    nickname: Optional[str]
    opted_in_reminders: bool
    balance: float = 0.0  # Net outstanding (positive = customer owes)
    created_at: datetime
    risk_level: str = "LOW RISK"
    risk_score: int = 10
    risk_badge_color: str = "emerald" 

    class Config:
        from_attributes = True


class TransactionResponse(BaseModel):
    id: int
    customer_id: int
    customer_name: str = ""
    amount: float
    direction: str
    transaction_date: date
    note: Optional[str]
    corrected: bool
    created_at: datetime

    class Config:
        from_attributes = True


class LedgerSummary(BaseModel):
    """Summary of all dues."""
    total_credit: float
    total_payments: float
    net_outstanding: float
    customer_count: int
    today_credit: float
    today_payments: float


class ParsedIntent(BaseModel):
    """Result of NLU parsing a voice command."""
    intent: IntentType
    customer_name: Optional[str] = None
    amount: Optional[float] = None
    direction: Optional[TransactionDirection] = None
    transaction_date: Optional[date] = None
    raw_text: str = ""
    confidence: float = 0.0
    needs_disambiguation: bool = False
    disambiguation_options: List[str] = []
    chitchat_topic: Optional[str] = None


class VoiceResponse(BaseModel):
    """Response sent back to the frontend after voice processing."""
    success: bool
    message: str  # Human-readable response (to be spoken via TTS)
    intent: Optional[ParsedIntent] = None
    transaction: Optional[TransactionResponse] = None
    audio_base64: Optional[str] = None  # TTS audio response
    needs_confirmation: bool = False
    needs_disambiguation: bool = False
    disambiguation_options: List[str] = []
    language: str = "hi-IN"
    correction_event: Optional[dict] = None  # UI strike-through: {old_amount, new_amount, customer}
    calculation_event: Optional[dict] = None  # Live table math: {customer, old_balance, change, new_balance, action, equation}
    counter_announcement: Optional[str] = None  # Two-Way Counter Audio Text for customer speaker
    counter_audio_base64: Optional[str] = None  # Synthesized audio for counter speaker
    whatsapp_receipt: Optional[dict] = None     # 1-click WhatsApp link and receipt text
    risk_analysis: Optional[dict] = None        # Khata Risk AI credit score and warnings
    upi_payload: Optional[dict] = None          # Dynamic voice-to-UPI QR code payload
