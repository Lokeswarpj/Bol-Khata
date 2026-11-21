"""
BolKhata - Pre-Seeder for Hackathon Live Demo & Multi-Store Merchants
Ensures zero-fail judge evaluation:
1. Pre-seeds two 'Ramesh' customers for the Disambiguation Demo:
   - Ramesh - Kirana Lane (nickname: Kirana Lane)
   - Ramesh - Milk Dairy (nickname: Milk Dairy)
2. Pre-seeds demo Kirana Store Owners for seamless multi-store merchant switching:
   - Sri Balaji Kirana (Niranjan)
   - Gupta Provision Store (Ramesh Gupta)
   - Royal Super Market (Suresh Kumar)
"""

import logging
from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import Customer, Transaction, StoreOwner

logger = logging.getLogger("bolkhata.seed")


async def seed_demo_data(db: AsyncSession):
    """Seed initial customers & merchants for zero-fail judge testing."""
    
    # ── 1. Ensure Default Store Owners Exist ──
    owner_res = await db.execute(select(StoreOwner))
    existing_owners = owner_res.scalars().all()
    
    if not existing_owners:
        logger.info("🌱 Seeding default Kirana store merchants...")
        o1 = StoreOwner(
            id=1,
            store_name="Sri Balaji Kirana",
            owner_name="Niranjan",
            phone="9876543210",
            pin="1234",
            language_preference="en-IN",
            is_active=True,
        )
        o2 = StoreOwner(
            store_name="Gupta Provision Store",
            owner_name="Ramesh Gupta",
            phone="9876543220",
            pin="1234",
            language_preference="hi-IN",
            is_active=False,
        )
        o3 = StoreOwner(
            store_name="Royal Super Market",
            owner_name="Suresh Kumar",
            phone="9876543230",
            pin="1234",
            language_preference="kn-IN",
            is_active=False,
        )
        db.add_all([o1, o2, o3])
        await db.commit()
    else:
        # Ensure active owner exists
        active_res = await db.execute(select(StoreOwner).where(StoreOwner.is_active == True))
        if not active_res.scalars().first():
            existing_owners[0].is_active = True
            await db.commit()

    # Get active owner ID
    active_owner_res = await db.execute(select(StoreOwner).where(StoreOwner.is_active == True))
    active_owner = active_owner_res.scalars().first()
    owner_id = active_owner.id if active_owner else 1

    # ── 2. Ensure the Two Ramesh Demo Customers Exist (Judge-Proof Disambiguation) ──
    c1_res = await db.execute(
        select(Customer).where(
            or_(
                Customer.name == "Ramesh - Kirana Lane",
                Customer.nickname == "Kirana Lane",
            )
        )
    )
    c1 = c1_res.scalars().first()

    if not c1:
        logger.info("🌱 Seeding 'Ramesh - Kirana Lane' for disambiguation demo...")
        c1 = Customer(
            name="Ramesh - Kirana Lane",
            nickname="Kirana Lane",
            phone="9876543210",
            owner_id=owner_id,
            opted_in_reminders=True,
        )
        db.add(c1)
        await db.flush()

        t1 = Transaction(
            owner_id=owner_id,
            customer_id=c1.id,
            amount=250.0,
            direction="credit",
            note="Opening udhaar balance for Ramesh (Kirana Lane)",
        )
        db.add(t1)

    c2_res = await db.execute(
        select(Customer).where(
            or_(
                Customer.name == "Ramesh - Milk Dairy",
                Customer.nickname == "Milk Dairy",
            )
        )
    )
    c2 = c2_res.scalars().first()

    if not c2:
        logger.info("🌱 Seeding 'Ramesh - Milk Dairy' for disambiguation demo...")
        c2 = Customer(
            name="Ramesh - Milk Dairy",
            nickname="Milk Dairy",
            phone="9876543211",
            owner_id=owner_id,
            opted_in_reminders=False,
        )
        db.add(c2)
        await db.flush()

        t2 = Transaction(
            owner_id=owner_id,
            customer_id=c2.id,
            amount=100.0,
            direction="credit",
            note="Opening udhaar balance for Ramesh (Milk Dairy)",
        )
        db.add(t2)

    await db.commit()
    logger.info("✅ Verified demo customers 'Ramesh - Kirana Lane' & 'Ramesh - Milk Dairy'")
