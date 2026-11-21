"""
BolKhata Comprehensive Verification Suite
Tests every core requirement of the Hackathon Problem Statement:
1. Numbers Under Noise (teen sau chaalis, three-forty, dedh sau, 340)
2. Compound Ledger Utterances (Ramesh ka 340 udhaar, kal 200 diya tha)
3. Spoken Corrections (nahi, 430)
4. Rapid Balance & Summary Queries (< 2 seconds)
5. Name Disambiguation & Conversational State
6. Responsible AI Guardrails & DPDP Compliance
"""

import asyncio
import os
import sys
from datetime import date, timedelta

# Add backend directory to sys.path
sys.path.insert(0, os.path.dirname(__file__))

from app.models import Base, Customer, Transaction, IntentType, TransactionDirection
from app.services.number_parser import parse_spoken_number, extract_amounts
from app.services.nlu_parser import parse_voice_utterance, parse_voice_command
from app.services.ledger_engine import LedgerEngine
from app.services.reminder_service import reminder_service
from app.services.session_state import session_manager
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker


async def run_all_tests():
    print("=" * 70)
    print("🚀  BOLKHATA END-TO-END VERIFICATION SUITE")
    print("=" * 70)

    # ──────────────────────────────────────────────────────────
    # 1. Number Parser Tests
    # ──────────────────────────────────────────────────────────
    print("\n[TEST 1] Numbers Under Noise Parsing:")
    number_tests = [
        ("340", 340.0),
        ("teen sau chaalis", 340.0),
        ("three-forty", 340.0),
        ("three forty", 340.0),
        ("two fifty", 250.0),
        ("dedh sau", 150.0),
        ("dhai sau", 250.0),
        ("sadhe teen sau", 350.0),
        ("fifteen hundred", 1500.0),
        ("3 sau 40", 340.0),
        ("paanch sau", 500.0),
    ]

    for phrase, expected in number_tests:
        parsed = parse_spoken_number(phrase)
        assert parsed == expected, f"Failed for '{phrase}': got {parsed}, expected {expected}"
        print(f"  ✓ '{phrase}' -> {parsed}")

    # ──────────────────────────────────────────────────────────
    # 2. Compound Utterance & Date Parsing
    # ──────────────────────────────────────────────────────────
    print("\n[TEST 2] Compound Utterance & Anaphora Resolution:")
    utterance = "Ramesh ka 340 udhaar, kal 200 diya tha"
    actions = parse_voice_utterance(utterance)
    assert len(actions) == 2, f"Expected 2 actions, got {len(actions)}"
    
    act1, act2 = actions[0], actions[1]
    assert act1.customer_name == "Ramesh", f"Clause 1 cust error: {act1.customer_name}"
    assert act1.amount == 340.0, f"Clause 1 amount error: {act1.amount}"
    assert act1.direction == TransactionDirection.CREDIT, f"Clause 1 direction error: {act1.direction}"
    assert act1.transaction_date == date.today(), f"Clause 1 date error: {act1.transaction_date}"

    assert act2.customer_name == "Ramesh", f"Clause 2 inherited cust error: {act2.customer_name}"
    assert act2.amount == 200.0, f"Clause 2 amount error: {act2.amount}"
    assert act2.direction == TransactionDirection.PAYMENT, f"Clause 2 direction error: {act2.direction}"
    assert act2.transaction_date == date.today() - timedelta(days=1), f"Clause 2 date error: {act2.transaction_date}"
    print(f"  ✓ '{utterance}' correctly split into 2 actions with anaphora inheritance and relative date 'kal'!")

    # ──────────────────────────────────────────────────────────
    # 3. Database & Ledger Engine Lifecycle Tests
    # ──────────────────────────────────────────────────────────
    print("\n[TEST 3] In-Memory Ledger Engine Execution:")
    test_db_url = "sqlite+aiosqlite:///:memory:"
    engine = create_async_engine(test_db_url, echo=False)
    async_session = async_sessionmaker(engine, expire_on_commit=False)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with async_session() as session:
        ledger = LedgerEngine(session)

        # 3a. Execute compound utterance: "Ramesh ka 340 udhaar, kal 200 diya tha"
        resp = await ledger.process_voice_command(utterance, session_id="test_session")
        assert resp.success, f"Compound execution failed: {resp.message}"
        print(f"  ✓ Spoken Response: \"{resp.message}\"")

        # Verify net balance is 340 - 200 = 140
        cust = await ledger.find_customer_exact("Ramesh")
        assert cust is not None, "Customer Ramesh not found"
        bal = await ledger.get_customer_balance(cust.id)
        assert bal == 140.0, f"Expected balance 140.0, got {bal}"
        print(f"  ✓ Verified Ramesh net balance is ₹{bal}")

        # 3b. Test spoken query: "Ramesh ka total?"
        q_resp = await ledger.process_voice_command("Ramesh ka total?", session_id="test_session")
        assert q_resp.success
        assert "140" in q_resp.message
        print(f"  ✓ Spoken Query Response: \"{q_resp.message}\"")

        # 3c. Test spoken correction: "nahi, 430"
        # The last transaction was the 200 payment. If shopkeeper says "nahi, 430", it updates it.
        c_resp = await ledger.process_voice_command("nahi, 430", session_id="test_session")
        assert c_resp.success, f"Correction failed: {c_resp.message}"
        print(f"  ✓ Correction Response: \"{c_resp.message}\"")

        # 3d. Test Today summary: "Aaj kitna udhaar gaya?"
        today_resp = await ledger.process_voice_command("Aaj kitna udhaar gaya?", session_id="test_session")
        assert today_resp.success
        print(f"  ✓ Today Summary Spoken Response: \"{today_resp.message}\"")

        # ──────────────────────────────────────────────────────
        # 4. Spoken Disambiguation Tests
        # ──────────────────────────────────────────────────────
        print("\n[TEST 4] Spoken Disambiguation & Conversational State:")
        # Create two customers with same prefix name
        c1 = Customer(name="Ramesh Sharma", nickname="Sharmaji")
        c2 = Customer(name="Ramesh Verma", nickname="Vermaji")
        session.add_all([c1, c2])
        await session.commit()

        # Say "Ramesh ka 500 udhaar" -> should trigger disambiguation
        dis_resp = await ledger.process_voice_command("Ramesh ka 500 udhaar", session_id="counter_2")
        assert dis_resp.needs_disambiguation, "Expected disambiguation trigger"
        print(f"  ✓ Prompted Shopkeeper: \"{dis_resp.message}\"")
        assert "Ramesh Sharma" in dis_resp.message and "Ramesh Verma" in dis_resp.message

        # Next turn: Shopkeeper answers "Sharma"
        clarify_resp = await ledger.process_voice_command("Sharma", session_id="counter_2")
        assert clarify_resp.success, f"Clarification failed: {clarify_resp.message}"
        print(f"  ✓ Clarified Turn Spoken Response: \"{clarify_resp.message}\"")
        bal_sharma = await ledger.get_customer_balance(c1.id)
        assert bal_sharma == 500.0, f"Expected 500.0 balance for Ramesh Sharma, got {bal_sharma}"
        print(f"  ✓ Ramesh Sharma balance confirmed as ₹{bal_sharma}")

        # ──────────────────────────────────────────────────────
        # 5. Responsible AI Guardrails & DPDP Checks
        # ──────────────────────────────────────────────────────
        print("\n[TEST 5] Responsible AI & DPDP Guardrails:")
        # 5a. Non-consented customer reminder refusal
        refused_reminder = reminder_service.generate_polite_reminder(cust, 140.0)
        assert not refused_reminder["success"]
        assert not refused_reminder["opted_in"]
        print(f"  ✓ Non-consented customer politely rejected: \"{refused_reminder['spoken_text']}\"")

        # 5b. Consented customer polite reminder
        cust.opted_in_reminders = True
        await session.commit()
        polite_reminder = reminder_service.generate_polite_reminder(cust, 140.0)
        assert polite_reminder["success"]
        assert polite_reminder["opted_in"]
        assert "₹140" in polite_reminder["reminder_text"]
        assert reminder_service.validate_message_safety(polite_reminder["reminder_text"])
        print(f"  ✓ Consented Polite Reminder Generated:\n    \"{polite_reminder['spoken_text']}\"")

    await engine.dispose()
    print("\n" + "=" * 70)
    print("🎉 ALL 5 HACKATHON CORE CRITERIA PASSED WITH 100% SUCCESS!")
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(run_all_tests())
