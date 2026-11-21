import asyncio
from app.database import async_session
from app.services.ledger_engine import LedgerEngine
from app.services.nlu_parser import parse_voice_utterance, detect_language

async def test_backend():
    print("=" * 60)
    print("Testing NLU Parsing...")
    print("=" * 60)
    tests = [
        "Stop",
        "Ruko",
        "BolKhata",
        "BolKhata Ramesh ka 500 udhaar",
        "Reset today's payment",
        "Aaj ki jama reset karo",
        "Ramesh cleared his debt",
        "Ramesh ka pura hisaab chukta ho gaya",
        "ರಮೇಶ್ ಸಾಲ ತೀರಿದೆ",
        "రమేష్ అప్పు తీరిపోయింది",
    ]
    for t in tests:
        res = parse_voice_utterance(t)
        print(f'Input: "{t}"')
        print(f'  -> Intent: {res[0].intent.value} | Cust: {res[0].customer_name} | Amt: {res[0].amount}')

    print("\n" + "=" * 60)
    print("Testing Ledger Engine Execution...")
    print("=" * 60)
    async with async_session() as session:
        ledger = LedgerEngine(session)
        # Test Wake Up
        w_res = await ledger.process_voice_command("BolKhata")
        print("Wake-Up Response:", w_res.message)
        
        # Test Stop
        s_res = await ledger.process_voice_command("Stop")
        print("Stop Response:", s_res.message)
        
        # Test Reset Payments
        r_res = await ledger.process_voice_command("Reset today's payment")
        print("Reset Payments Response:", r_res.message)
        
        # Test Clear Debt English
        cd_res = await ledger.process_voice_command("Ramesh - Kirana Lane cleared his debt")
        print("Clear Debt (EN):", cd_res.message)

        # Test Clear Debt Hindi
        cd_hi = await ledger.process_voice_command("Ramesh - Kirana Lane ka hisaab chukta ho gaya")
        print("Clear Debt (HI):", cd_hi.message)

        # Test Clear Debt Kannada
        cd_kn = await ledger.process_voice_command("Ramesh - Kirana Lane ಸಾಲ ತೀರಿದೆ", language="kn-IN")
        print("Clear Debt (KN):", cd_kn.message)

        # Test Clear Debt Telugu
        cd_te = await ledger.process_voice_command("Ramesh - Kirana Lane అప్పు తీరిపోయింది", language="te-IN")
        print("Clear Debt (TE):", cd_te.message)

if __name__ == "__main__":
    asyncio.run(test_backend())
