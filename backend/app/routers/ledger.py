"""
BolKhata - Ledger REST Router
CRUD operations for ledger entries (transactions).
"""

from datetime import date
from typing import Optional, List

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func, and_, desc, case
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import (
    Transaction, Customer,
    ManualTransactionCreate, TransactionResponse, LedgerSummary,
    TransactionDirection,
)

router = APIRouter(prefix="/api/ledger", tags=["Ledger"])


@router.post("/transaction", response_model=TransactionResponse)
async def create_transaction(
    data: ManualTransactionCreate,
    db: AsyncSession = Depends(get_db),
):
    """Create a ledger entry manually (REST fallback)."""
    # Find or create customer
    result = await db.execute(
        select(Customer).where(func.lower(Customer.name) == data.customer_name.lower())
    )
    customer = result.scalars().first()
    
    if not customer:
        customer = Customer(name=data.customer_name.strip().title())
        db.add(customer)
        await db.flush()
    
    txn = Transaction(
        customer_id=customer.id,
        amount=data.amount,
        direction=data.direction.value,
        transaction_date=data.transaction_date or date.today(),
        note=data.note,
    )
    db.add(txn)
    await db.commit()
    await db.refresh(txn)
    
    return TransactionResponse(
        id=txn.id,
        customer_id=txn.customer_id,
        customer_name=customer.name,
        amount=txn.amount,
        direction=txn.direction,
        transaction_date=txn.transaction_date,
        note=txn.note,
        corrected=txn.corrected,
        created_at=txn.created_at,
    )


@router.get("/transactions", response_model=List[TransactionResponse])
async def list_transactions(
    customer_id: Optional[int] = Query(None),
    direction: Optional[str] = Query(None),
    from_date: Optional[date] = Query(None),
    to_date: Optional[date] = Query(None),
    limit: int = Query(50, le=200),
    db: AsyncSession = Depends(get_db),
):
    """List ledger entries with optional filters."""
    query = select(Transaction, Customer.name).join(
        Customer, Transaction.customer_id == Customer.id
    ).where(Transaction.corrected == False)
    
    if customer_id:
        query = query.where(Transaction.customer_id == customer_id)
    if direction:
        query = query.where(Transaction.direction == direction)
    if from_date:
        query = query.where(Transaction.transaction_date >= from_date)
    if to_date:
        query = query.where(Transaction.transaction_date <= to_date)
    
    query = query.order_by(desc(Transaction.created_at)).limit(limit)
    
    result = await db.execute(query)
    rows = result.all()
    
    return [
        TransactionResponse(
            id=txn.id,
            customer_id=txn.customer_id,
            customer_name=name,
            amount=txn.amount,
            direction=txn.direction,
            transaction_date=txn.transaction_date,
            note=txn.note,
            corrected=txn.corrected,
            created_at=txn.created_at,
        )
        for txn, name in rows
    ]


@router.get("/summary", response_model=LedgerSummary)
async def get_summary(
    db: AsyncSession = Depends(get_db),
):
    """Get overall ledger summary."""
    today = date.today()
    
    # Overall totals
    overall = await db.execute(
        select(
            func.coalesce(func.sum(case(
                (Transaction.direction == "credit", Transaction.amount), else_=0
            )), 0).label("total_credit"),
            func.coalesce(func.sum(case(
                (Transaction.direction == "payment", Transaction.amount), else_=0
            )), 0).label("total_payment"),
        ).where(Transaction.corrected == False)
    )
    overall_row = overall.first()
    
    # Today totals
    today_result = await db.execute(
        select(
            func.coalesce(func.sum(case(
                (Transaction.direction == "credit", Transaction.amount), else_=0
            )), 0).label("today_credit"),
            func.coalesce(func.sum(case(
                (Transaction.direction == "payment", Transaction.amount), else_=0
            )), 0).label("today_payment"),
        ).where(and_(
            Transaction.corrected == False,
            Transaction.transaction_date == today,
        ))
    )
    today_row = today_result.first()
    
    # Customer count with dues
    customer_count = await db.execute(
        select(func.count(func.distinct(Transaction.customer_id))).where(
            Transaction.corrected == False
        )
    )
    
    return LedgerSummary(
        total_credit=overall_row.total_credit,
        total_payments=overall_row.total_payment,
        net_outstanding=overall_row.total_credit - overall_row.total_payment,
        customer_count=customer_count.scalar() or 0,
        today_credit=today_row.today_credit,
        today_payments=today_row.today_payment,
    )


@router.delete("/transaction/{txn_id}")
async def delete_transaction(
    txn_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Mark a transaction as corrected/deleted."""
    result = await db.execute(select(Transaction).where(Transaction.id == txn_id))
    txn = result.scalars().first()
    if not txn:
        raise HTTPException(status_code=404, detail="Transaction not found")
    
    txn.corrected = True
    await db.commit()
    return {"message": "Transaction cancelled", "id": txn_id}
