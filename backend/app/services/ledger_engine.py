"""
BolKhata - Advanced Ledger Engine (Core Business Logic)
Features:
- Multi-action compound sentence execution: "Ramesh ka 340 udhaar, kal 200 diya tha"
- State-aware disambiguation: Holds pending transactions and prompts shopkeeper
- Spoken corrections: "nahi, 430"
- Rapid queries (< 2 seconds): "Ramesh ka total?", "Aaj kitna udhaar gaya?"
- DPDP Act compliant persistence with AES-256 encrypted fields
- Session context management
"""

import logging
from datetime import date, datetime
from typing import Optional, List, Tuple, Dict, Any

from sqlalchemy import select, func, and_, or_, desc, case
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import (
    Customer, Transaction,
    TransactionDirection, IntentType, ParsedIntent,
    CustomerResponse, TransactionResponse, LedgerSummary,
    VoiceResponse,
)
from app.services.nlu_parser import parse_voice_utterance, parse_voice_command
from app.services.number_parser import parse_spoken_number, extract_first_amount
from app.services.session_state import session_manager, SessionState

logger = logging.getLogger("bolkhata.ledger")


class LedgerEngine:
    """Core business logic for the BolKhata ledger."""

    def __init__(self, db: AsyncSession):
        self.db = db

    # ═══════════════════════════════════════════════════════════
    # Customer Lookups & Disambiguation
    # ═══════════════════════════════════════════════════════════

    async def find_customer_exact(self, name: str) -> Optional[Customer]:
        name_clean = name.strip().lower()
        result = await self.db.execute(
            select(Customer).where(
                or_(
                    func.lower(Customer.name) == name_clean,
                    func.lower(Customer.nickname) == name_clean,
                )
            )
        )
        return result.scalars().first()

    async def find_matching_customers(self, name: str) -> List[Customer]:
        """Finds all customers matching a given name prefix or substring."""
        name_clean = name.strip().lower()
        result = await self.db.execute(
            select(Customer).where(
                or_(
                    func.lower(Customer.name).like(f"%{name_clean}%"),
                    func.lower(Customer.nickname).like(f"%{name_clean}%"),
                )
            )
        )
        return list(result.scalars().all())

    async def get_or_create_customer(self, name: str) -> Tuple[Customer, bool]:
        customer = await self.find_customer_exact(name)
        if customer:
            return customer, False
        
        customer = Customer(
            name=name.strip().title(),
            opted_in_reminders=False,  # Responsible AI default: opt-in required
        )
        self.db.add(customer)
        await self.db.flush()
        return customer, True

    async def get_all_customers(self) -> List[Customer]:
        result = await self.db.execute(select(Customer).order_by(Customer.name))
        return list(result.scalars().all())

    async def get_customer_balance(self, customer_id: int) -> float:
        """Net outstanding balance (positive = customer owes money)."""
        result = await self.db.execute(
            select(
                func.coalesce(
                    func.sum(
                        case(
                            (Transaction.direction == "credit", Transaction.amount),
                            else_=0
                        )
                    ), 0
                ).label("total_credit"),
                func.coalesce(
                    func.sum(
                        case(
                            (Transaction.direction == "payment", Transaction.amount),
                            else_=0
                        )
                    ), 0
                ).label("total_payment"),
            ).where(
                and_(
                    Transaction.customer_id == customer_id,
                    Transaction.corrected == False,
                )
            )
        )
        row = result.first()
        if row:
            return float((row.total_credit or 0) - (row.total_payment or 0))
        return 0.0

    # ═══════════════════════════════════════════════════════════
    # Transaction Management
    # ═══════════════════════════════════════════════════════════

    async def add_transaction(
        self,
        customer_id: int,
        amount: float,
        direction: TransactionDirection,
        transaction_date: Optional[date] = None,
        note: Optional[str] = None,
        raw_transcript: Optional[str] = None,
        session: Optional[SessionState] = None,
    ) -> Transaction:
        txn = Transaction(
            customer_id=customer_id,
            amount=amount,
            direction=direction.value,
            transaction_date=transaction_date or date.today(),
            note=note,
            raw_transcript=raw_transcript,
        )
        self.db.add(txn)
        await self.db.flush()

        # Update session memory for rapid spoken corrections
        if session:
            # Fetch customer name
            res = await self.db.execute(select(Customer).where(Customer.id == customer_id))
            c = res.scalars().first()
            c_name = c.name if c else ""
            session.record_transaction(
                txn_id=txn.id,
                customer_id=customer_id,
                customer_name=c_name,
                amount=amount,
                direction=direction.value,
            )

        logger.info(f"Added txn {txn.id}: {direction.value} ₹{amount} for customer {customer_id}")
        return txn

    async def correct_last_transaction(
        self,
        new_amount: float,
        session: Optional[SessionState] = None,
    ) -> Optional[Transaction]:
        """
        Handles spoken corrections like "nahi, 430".
        Finds the last uncorrected transaction in this session and corrects it.
        """
        target_txn_id = session.last_transaction_id if session else None

        if not target_txn_id:
            # Fall back to most recent transaction in DB
            res = await self.db.execute(
                select(Transaction).where(Transaction.corrected == False).order_by(desc(Transaction.id)).limit(1)
            )
            latest = res.scalars().first()
            if latest:
                target_txn_id = latest.id

        if not target_txn_id:
            return None

        # Fetch old transaction
        res = await self.db.execute(select(Transaction).where(Transaction.id == target_txn_id))
        old_txn = res.scalars().first()
        if not old_txn:
            return None

        # Invalidate old transaction
        old_txn.corrected = True

        # Insert replacement transaction
        new_txn = Transaction(
            customer_id=old_txn.customer_id,
            amount=new_amount,
            direction=old_txn.direction,
            transaction_date=old_txn.transaction_date,
            note=f"Corrected via voice from ₹{old_txn.amount:g}",
            correction_of=old_txn.id,
            raw_transcript=old_txn.raw_transcript,
        )
        self.db.add(new_txn)
        await self.db.flush()

        if session:
            res_c = await self.db.execute(select(Customer).where(Customer.id == old_txn.customer_id))
            cust = res_c.scalars().first()
            session.record_transaction(
                txn_id=new_txn.id,
                customer_id=old_txn.customer_id,
                customer_name=cust.name if cust else "",
                amount=new_amount,
                direction=old_txn.direction,
            )

        logger.info(f"Corrected transaction {old_txn.id} (₹{old_txn.amount}) -> new txn {new_txn.id} (₹{new_amount})")
        return new_txn

    async def get_today_summary(self) -> dict:
        today = date.today()
        result = await self.db.execute(
            select(
                func.coalesce(
                    func.sum(
                        case(
                            (Transaction.direction == "credit", Transaction.amount),
                            else_=0
                        )
                    ), 0
                ).label("today_credit"),
                func.coalesce(
                    func.sum(
                        case(
                            (Transaction.direction == "payment", Transaction.amount),
                            else_=0
                        )
                    ), 0
                ).label("today_payment"),
                func.count().label("txn_count"),
            ).where(
                and_(
                    Transaction.transaction_date == today,
                    Transaction.corrected == False,
                )
            )
        )
        row = result.first()
        return {
            "today_credit": float(row.today_credit or 0),
            "today_payment": float(row.today_payment or 0),
            "transaction_count": int(row.txn_count or 0),
        }

    async def get_customer_transactions(self, customer_id: int, limit: int = 50) -> List[Transaction]:
        result = await self.db.execute(
            select(Transaction)
            .where(
                and_(
                    Transaction.customer_id == customer_id,
                    Transaction.corrected == False,
                )
            )
            .order_by(desc(Transaction.created_at))
            .limit(limit)
        )
        return list(result.scalars().all())

    # ═══════════════════════════════════════════════════════════
    # Complete Voice Utterance Processor (Compound + Clarification)
    # ═══════════════════════════════════════════════════════════

    async def process_voice_command(
        self,
        text: str,
        session_id: Optional[str] = None,
    ) -> VoiceResponse:
        session = session_manager.get_or_create(session_id or "default_counter")

        # ── Step A: Check for Pending Disambiguation Resolution ──
        if session.pending_action:
            pending = session.pending_action
            clean_reply = text.strip().lower()

            matched_cust: Optional[Dict[str, Any]] = None
            for cand in pending.candidates:
                cand_name = cand["name"].lower()
                cand_nick = (cand.get("nickname") or "").lower()
                if cand_name in clean_reply or clean_reply in cand_name or (cand_nick and cand_nick in clean_reply):
                    matched_cust = cand
                    break

            if matched_cust:
                session.clear_pending_action()
                intent = pending.intent
                direction = intent.direction or TransactionDirection.CREDIT
                txn = await self.add_transaction(
                    customer_id=matched_cust["id"],
                    amount=intent.amount,
                    direction=direction,
                    transaction_date=intent.transaction_date,
                    note=f"{direction.value.title()}: {matched_cust['name']} - ₹{intent.amount:g}",
                    raw_transcript=text,
                    session=session,
                )
                await self.db.commit()
                bal = await self.get_customer_balance(matched_cust["id"])

                act_word = "udhaar likha" if direction == TransactionDirection.CREDIT else "jama kiya"
                msg = f"Done! {matched_cust['name']} ka ₹{intent.amount:g} {act_word}. Ab total baaki: ₹{bal:g}."
                return VoiceResponse(
                    success=True,
                    message=msg,
                    intent=intent,
                    transaction=TransactionResponse(
                        id=txn.id,
                        customer_id=matched_cust["id"],
                        customer_name=matched_cust["name"],
                        amount=txn.amount,
                        direction=txn.direction,
                        transaction_date=txn.transaction_date,
                        note=txn.note,
                        corrected=txn.corrected,
                        created_at=txn.created_at,
                    ),
                )

        # ── Step B: Parse Utterance into Clauses ──
        actions = parse_voice_utterance(text)

        # Check for instant spoken correction: "nahi, 430"
        if len(actions) == 1 and actions[0].intent == IntentType.CORRECTION:
            corr_amount = actions[0].amount or extract_first_amount(text)
            if corr_amount is not None:
                new_txn = await self.correct_last_transaction(corr_amount, session=session)
                if new_txn:
                    await self.db.commit()
                    cust_name = session.last_customer_name or "Customer"
                    bal = await self.get_customer_balance(new_txn.customer_id)
                    return VoiceResponse(
                        success=True,
                        message=f"Theek hai, sudhar diya! ₹{corr_amount:g} darj hua. {cust_name} ka total baaki: ₹{bal:g}.",
                        intent=actions[0],
                    )
            return VoiceResponse(
                success=False,
                message="Koi pichli entry nahi mili sudharne ke liye.",
                intent=actions[0],
            )

        # Check for Rapid Query: "Ramesh ka total?"
        if len(actions) == 1 and actions[0].intent == IntentType.QUERY_BALANCE:
            target_name = actions[0].customer_name
            if not target_name:
                return VoiceResponse(success=False, message="Kiska hisaab chahiye? Kripya naam bataiye.", intent=actions[0])
            
            cust = await self.find_customer_exact(target_name)
            if not cust:
                # Try prefix search
                matches = await self.find_matching_customers(target_name)
                if len(matches) == 1:
                    cust = matches[0]
                elif len(matches) > 1:
                    names = [c.name for c in matches]
                    return VoiceResponse(
                        success=False,
                        message=f"Kaun wale {target_name}? {', '.join(names)}?",
                        needs_disambiguation=True,
                        disambiguation_options=names,
                        intent=actions[0],
                    )

            if not cust:
                return VoiceResponse(success=False, message=f"{target_name} naam ka koi customer nahi mila.", intent=actions[0])

            balance = await self.get_customer_balance(cust.id)
            if balance > 0:
                msg = f"{cust.name} ka total baaki ₹{balance:g} hai."
            elif balance < 0:
                msg = f"{cust.name} ka ₹{abs(balance):g} advance jama hai."
            else:
                msg = f"{cust.name} ka hisaab bilkul clear hai!"
            return VoiceResponse(success=True, message=msg, intent=actions[0])

        # Check for Rapid Query: "Aaj kitna udhaar gaya?"
        if len(actions) == 1 and actions[0].intent == IntentType.QUERY_TODAY:
            today_data = await self.get_today_summary()
            u_gaya = today_data["today_credit"]
            j_aaya = today_data["today_payment"]
            net = u_gaya - j_aaya
            cnt = today_data["transaction_count"]
            msg = f"Aaj kul ₹{u_gaya:g} udhaar gaya, aur ₹{j_aaya:g} jama aaya. Net ₹{net:g}. Total {cnt} entries."
            return VoiceResponse(success=True, message=msg, intent=actions[0])

        # ── Step C: Execute Ledger Actions (Single or Compound) ──
        success_messages = []
        created_txns = []

        for act in actions:
            if act.intent not in (IntentType.ADD_CREDIT, IntentType.ADD_PAYMENT):
                continue
            if not act.customer_name or act.amount is None:
                continue

            # Check for multiple customers with same name (Disambiguation required!)
            similar = await self.find_matching_customers(act.customer_name)
            if len(similar) > 1:
                # Save pending state in session
                candidates = [{"id": c.id, "name": c.name, "nickname": c.nickname} for c in similar]
                session.set_pending_action(act, candidates)
                names = [c.name for c in similar]
                dis_prompt = f"Kaun wale {act.customer_name}? {' ya '.join(names)}?"
                return VoiceResponse(
                    success=False,
                    message=dis_prompt,
                    intent=act,
                    needs_disambiguation=True,
                    disambiguation_options=names,
                )

            # Get or create
            customer, is_new = await self.get_or_create_customer(act.customer_name)
            direction = act.direction or TransactionDirection.CREDIT

            txn = await self.add_transaction(
                customer_id=customer.id,
                amount=act.amount,
                direction=direction,
                transaction_date=act.transaction_date,
                note=f"{direction.value.title()}: {customer.name} - ₹{act.amount:g}",
                raw_transcript=act.raw_text,
                session=session,
            )
            created_txns.append(txn)

            act_str = "udhaar" if direction == TransactionDirection.CREDIT else "jama"
            date_str = "kal ka " if act.transaction_date and act.transaction_date < date.today() else ""
            success_messages.append(f"{date_str}₹{act.amount:g} {act_str}")

        if created_txns:
            await self.db.commit()
            last_cust_id = created_txns[-1].customer_id
            last_cust_res = await self.db.execute(select(Customer).where(Customer.id == last_cust_id))
            last_cust = last_cust_res.scalars().first()
            final_bal = await self.get_customer_balance(last_cust_id)
            c_name = last_cust.name if last_cust else "Customer"

            details = ", aur ".join(success_messages)
            final_message = f"Done! {c_name} ka {details} likha. Ab kul baaki: ₹{final_bal:g}."

            return VoiceResponse(
                success=True,
                message=final_message,
                intent=actions[0],
                transaction=TransactionResponse(
                    id=created_txns[-1].id,
                    customer_id=last_cust_id,
                    customer_name=c_name,
                    amount=created_txns[-1].amount,
                    direction=created_txns[-1].direction,
                    transaction_date=created_txns[-1].transaction_date,
                    note=created_txns[-1].note,
                    corrected=created_txns[-1].corrected,
                    created_at=created_txns[-1].created_at,
                ),
            )

        return VoiceResponse(
            success=False,
            message="Samajh nahi aaya. Kripya dubaara boliye.",
            intent=actions[0] if actions else None,
        )
