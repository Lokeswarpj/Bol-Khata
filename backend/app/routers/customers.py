"""
BolKhata - Customer REST Router
CRUD operations for customer management.
"""

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import Customer, Transaction, CustomerCreate, CustomerUpdate, CustomerResponse
from app.services.ledger_engine import LedgerEngine

router = APIRouter(prefix="/api/customers", tags=["Customers"])


@router.get("/", response_model=List[CustomerResponse])
async def list_customers(
    search: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
):
    """List all customers with their balances."""
    query = select(Customer).order_by(Customer.name)
    
    if search:
        query = query.where(
            or_(
                func.lower(Customer.name).like(f"%{search.lower()}%"),
                func.lower(Customer.nickname).like(f"%{search.lower()}%"),
            )
        )
    
    result = await db.execute(query)
    customers = result.scalars().all()
    
    ledger = LedgerEngine(db)
    responses = []
    for c in customers:
        balance = await ledger.get_customer_balance(c.id)
        responses.append(CustomerResponse(
            id=c.id,
            name=c.name,
            phone=c.phone,
            nickname=c.nickname,
            opted_in_reminders=c.opted_in_reminders,
            balance=balance,
            created_at=c.created_at,
        ))
    
    return responses


@router.get("/{customer_id}", response_model=CustomerResponse)
async def get_customer(
    customer_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Get customer details with balance."""
    result = await db.execute(select(Customer).where(Customer.id == customer_id))
    customer = result.scalars().first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    ledger = LedgerEngine(db)
    balance = await ledger.get_customer_balance(customer.id)
    
    return CustomerResponse(
        id=customer.id,
        name=customer.name,
        phone=customer.phone,
        nickname=customer.nickname,
        opted_in_reminders=customer.opted_in_reminders,
        balance=balance,
        created_at=customer.created_at,
    )


@router.post("/", response_model=CustomerResponse)
async def create_customer(
    data: CustomerCreate,
    db: AsyncSession = Depends(get_db),
):
    """Create a new customer."""
    # Check for duplicate
    existing = await db.execute(
        select(Customer).where(func.lower(Customer.name) == data.name.lower())
    )
    if existing.scalars().first():
        raise HTTPException(status_code=400, detail=f"Customer '{data.name}' already exists")
    
    customer = Customer(
        name=data.name.strip().title(),
        phone=data.phone,
        nickname=data.nickname,
        opted_in_reminders=data.opted_in_reminders,
    )
    db.add(customer)
    await db.commit()
    await db.refresh(customer)
    
    return CustomerResponse(
        id=customer.id,
        name=customer.name,
        phone=customer.phone,
        nickname=customer.nickname,
        opted_in_reminders=customer.opted_in_reminders,
        balance=0.0,
        created_at=customer.created_at,
    )


@router.put("/{customer_id}", response_model=CustomerResponse)
async def update_customer(
    customer_id: int,
    data: CustomerUpdate,
    db: AsyncSession = Depends(get_db),
):
    """Update customer details."""
    result = await db.execute(select(Customer).where(Customer.id == customer_id))
    customer = result.scalars().first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    if data.name is not None:
        customer.name = data.name.strip().title()
    if data.phone is not None:
        customer.phone = data.phone
    if data.nickname is not None:
        customer.nickname = data.nickname
    if data.opted_in_reminders is not None:
        customer.opted_in_reminders = data.opted_in_reminders
    
    await db.commit()
    await db.refresh(customer)
    
    ledger = LedgerEngine(db)
    balance = await ledger.get_customer_balance(customer.id)
    
    return CustomerResponse(
        id=customer.id,
        name=customer.name,
        phone=customer.phone,
        nickname=customer.nickname,
        opted_in_reminders=customer.opted_in_reminders,
        balance=balance,
        created_at=customer.created_at,
    )


@router.get("/{customer_id}/dues")
async def get_customer_dues(
    customer_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Get detailed dues breakdown for a customer."""
    result = await db.execute(select(Customer).where(Customer.id == customer_id))
    customer = result.scalars().first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    ledger = LedgerEngine(db)
    balance = await ledger.get_customer_balance(customer.id)
    transactions = await ledger.get_customer_transactions(customer.id)
    
    return {
        "customer": {
            "id": customer.id,
            "name": customer.name,
        },
        "balance": balance,
        "transactions": [
            {
                "id": t.id,
                "amount": t.amount,
                "direction": t.direction,
                "date": str(t.transaction_date),
                "note": t.note,
                "created_at": t.created_at.isoformat() if t.created_at else None,
            }
            for t in transactions
        ],
    }
