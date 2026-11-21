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


class Transaction(Base):
    """A single ledger entry (credit/udhaar or payment/jama)."""
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, autoincrement=True)
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
    QUERY_BALANCE = "query_balance" # "Ramesh ka total?"
    QUERY_TODAY = "query_today"     # "Aaj kitna udhaar gaya?"
    CORRECTION = "correction"       # "nahi, 430"
    LIST_DUES = "list_dues"         # "Sabka hisaab bata"
    UNKNOWN = "unknown"


# ── Request Schemas ───────────────────────────────────────────

class VoiceInput(BaseModel):
    """Raw voice input (audio bytes sent via WebSocket or REST)."""
    audio_base64: Optional[str] = None
    text: Optional[str] = None  # Pre-transcribed text (for testing)
    language: str = Field(default="hi-IN")


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
