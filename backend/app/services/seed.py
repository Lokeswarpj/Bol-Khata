"""
BolKhata - Pre-Seeder for Hackathon Live Demo
Pre-seeds two 'Ramesh' customers to guarantee the Judge-Proof Disambiguation demo:
1. Ramesh - Kirana Lane (nickname: Kirana Lane)
2. Ramesh - Milk Dairy (nickname: Milk Dairy)
"""

import logging
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import Customer, Transaction

logger = logging.getLogger("bolkhata.seed")


async def seed_demo_data(db: AsyncSession):
    """Seed initial customers for zero-fail judge testing."""
    result = await db.execute(select(Customer))
    existing = result.scalars().all()
    if existing:
        return  # Already seeded

    logger.info("🌱 Seeding pre-configured demo customers for Build Bengaluru 2.0...")

    c1 = Customer(
        name="Ramesh - Kirana Lane",
        nickname="Kirana Lane",
        phone="9876543210",
        opted_in_reminders=True,
    )
    c2 = Customer(
        name="Ramesh - Milk Dairy",
        nickname="Milk Dairy",
        phone="9876543211",
        opted_in_reminders=False,
    )
    c3 = Customer(
        name="Suresh General Store",
        nickname="Suresh",
        phone="9876543212",
        opted_in_reminders=True,
    )

    db.add_all([c1, c2, c3])
    await db.flush()

    # Pre-seed sample transactions so 'Ramesh ka total?' or 'Aaj kitna udhaar gaya?' returns live data
    t1 = Transaction(
        customer_id=c1.id,
        amount=250.0,
        direction="credit",
        note="Initial opening udhaar balance",
    )
    t2 = Transaction(
        customer_id=c2.id,
        amount=100.0,
        direction="credit",
        note="Initial opening udhaar balance",
    )
    db.add_all([t1, t2])
    await db.commit()

    logger.info("✅ Pre-seeded 'Ramesh - Kirana Lane' and 'Ramesh - Milk Dairy' successfully.")
