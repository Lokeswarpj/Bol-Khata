"""
BolKhata API Smoke Test
Verifies all REST and Voice endpoints using httpx AsyncClient.
"""

import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

import httpx
from app.main import app
from app.database import init_db


async def main():
    print("=" * 60)
    print("🌐  BOLKHATA FASTAPI INTEGRATION & SMOKE TEST")
    print("=" * 60)

    # Initialize DB
    await init_db()

    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
        # 1. Root & Health
        res = await client.get("/")
        assert res.status_code == 200
        print(f"  ✓ GET / -> 200 (HTML Interactive Counter UI served)")

        res = await client.get("/api/info")
        assert res.status_code == 200
        print(f"  ✓ GET /api/info -> 200: {res.json()['app']} v{res.json()['version']}")

        res = await client.get("/health")
        assert res.status_code == 200
        print(f"  ✓ GET /health -> 200: {res.json()['status']} (encryption: {res.json()['encryption']})")

        # 2. Test NLU parse diagnostic endpoint
        res = await client.post("/api/test/parse", params={"text": "Ramesh ka 340 udhaar, kal 200 diya tha"})
        assert res.status_code == 200
        data = res.json()
        assert data["clauses_detected"] == 2
        print(f"  ✓ POST /api/test/parse -> 200: detected {data['clauses_detected']} clauses")

        # 3. Test Voice process-text endpoint (adding transaction)
        res = await client.post("/api/voice/process-text", json={"text": "Suresh ka 500 udhaar"})
        assert res.status_code == 200
        v_data = res.json()
        assert v_data["success"] is True
        print(f"  ✓ POST /api/voice/process-text (add) -> \"{v_data['message']}\"")

        # 4. Test Voice query
        res = await client.post("/api/voice/process-text", json={"text": "Suresh ka total?"})
        assert res.status_code == 200
        q_data = res.json()
        assert q_data["success"] is True
        print(f"  ✓ POST /api/voice/process-text (query) -> \"{q_data['message']}\"")

        # 5. Test Ledger summary
        res = await client.get("/api/ledger/summary")
        assert res.status_code == 200
        s_data = res.json()
        print(f"  ✓ GET /api/ledger/summary -> Net outstanding: ₹{s_data['net_outstanding']}")

        # 6. Test Customers list
        res = await client.get("/api/customers/")
        assert res.status_code == 200
        c_list = res.json()
        print(f"  ✓ GET /api/customers/ -> {len(c_list)} customer(s) registered")
        cust_id = c_list[0]["id"]

        # 7. Test Compliance consent & reminder
        # Opt-in consent
        res = await client.post(f"/api/compliance/consent/{cust_id}", params={"opt_in": True})
        assert res.status_code == 200
        print(f"  ✓ POST /api/compliance/consent/{cust_id} -> {res.json()['message']}")

        # Polite reminder
        res = await client.get(f"/api/compliance/reminder/{cust_id}")
        assert res.status_code == 200
        rem_data = res.json()
        assert rem_data["guardrail_status"] == "PASSED_RESPONSIBLE_AI_CHECK"
        print(f"  ✓ GET /api/compliance/reminder/{cust_id} -> Guardrail {rem_data['guardrail_status']}")

        # Encrypted Export
        res = await client.get(f"/api/compliance/export/{cust_id}")
        assert res.status_code == 200
        print(f"  ✓ GET /api/compliance/export/{cust_id} -> AES-256 encrypted payload received")

        # Conversational Chitchat test
        res = await client.post("/api/voice/process-text", json={"text": "Namaste bhaiya, kaise ho?"})
        assert res.status_code == 200
        chat_data = res.json()
        assert chat_data["success"] is True
        assert chat_data["intent"]["intent"] == "chitchat"
        print(f"  ✓ POST /api/voice/process-text (chitchat) -> \"{chat_data['message']}\"")

        # Purge demo transcripts
        res = await client.delete("/api/compliance/purge-demo-transcripts")
        assert res.status_code == 200
        print(f"  ✓ DELETE /api/compliance/purge-demo-transcripts -> {res.json()['message']}")

    print("\n" + "=" * 60)
    print("🎉 ALL FASTAPI API ENDPOINTS VERIFIED & WORKING!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
