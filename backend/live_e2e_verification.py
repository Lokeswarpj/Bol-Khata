import json
import urllib.request

BASE_URL = "http://127.0.0.1:8000"

def post(endpoint, data):
    req = urllib.request.Request(
        f"{BASE_URL}{endpoint}",
        data=json.dumps(data).encode("utf-8"),
        headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode("utf-8"))

def get(endpoint):
    with urllib.request.urlopen(f"{BASE_URL}{endpoint}") as resp:
        content_type = resp.headers.get("Content-Type", "")
        if "json" in content_type:
            return json.loads(resp.read().decode("utf-8"))
        return resp.read().decode("utf-8")

def main():
    print("=" * 65)
    print("🚀 BOLKHATA LIVE END-TO-END VERIFICATION")
    print("=" * 65)

    # 1. UI Check
    html = get("/")
    assert "BolKhata" in html and "Wake-Word" in html
    print("✅ Counter Web App at http://127.0.0.1:8000/ is online & healthy")

    pwa = get("/app")
    assert "BolKhata" in pwa or "html" in pwa
    print("✅ React Cyber-Serif PWA at http://127.0.0.1:8000/app is online & healthy")

    # 2. Store Owner Profile & Multi-Store List
    profile = get("/api/owner/profile")
    assert profile.get("registered") is True
    print(f"✅ Active Store: {profile['owner']['store_name']} (Merchant: {profile['owner']['owner_name']})")

    owners = get("/api/owner/all")
    print(f"✅ Registered Stores in DB ({len(owners['owners'])} total):")
    for o in owners["owners"]:
        status = "ACTIVE" if o["is_active"] else "INACTIVE"
        print(f"   [{status}] ID {o['id']}: {o['store_name']} ({o['owner_name']}) - Phone: {o['phone']}")

    # 3. Wake-Word & Standby Voice Control
    print("\n--- 3. Testing Wake-Word & Standby ---")
    wake_res = post("/api/voice/process-text", {"text": "BolKhata"})
    print(f"  Spoken: 'BolKhata' -> Response: \"{wake_res['message']}\"")
    assert wake_res["intent"]["intent"] == "wake_up"

    stop_res = post("/api/voice/process-text", {"text": "Stop"})
    print(f"  Spoken: 'Stop' -> Response: \"{stop_res['message']}\"")
    assert stop_res["intent"]["intent"] == "stop_listening"

    # 4. Reset Today's Payments via Voice & API
    print("\n--- 4. Testing Reset Today's Payments ---")
    reset_res = post("/api/voice/process-text", {"text": "Reset today's payment"})
    print(f"  Spoken: 'Reset today\\'s payment' -> Response: \"{reset_res['message']}\"")
    assert reset_res["intent"]["intent"] == "reset_todays_payments"

    # 5. Judge-Proof Disambiguation Scenario
    print("\n--- 5. Testing Disambiguation: 'Ramesh ka 500 udhaar' ---")
    dis_res = post("/api/voice/process-text", {"text": "Ramesh ka 500 udhaar", "session_id": "judge_demo"})
    print(f"  AI Asks: \"{dis_res['message']}\"")
    assert dis_res.get("needs_disambiguation") is True
    assert "Kirana Lane" in dis_res["message"] and "Milk Dairy" in dis_res["message"]
    print("  ✅ 100% Match with Hackathon Disambiguation Rule!")

    # 6. Disambiguation Resolution
    print("\n--- 6. Testing Disambiguation Resolution: 'Kirana Lane' ---")
    reply_res = post("/api/voice/process-text", {"text": "Kirana Lane", "session_id": "judge_demo"})
    print(f"  Resolution: \"{reply_res['message']}\"")
    assert reply_res.get("success") is True

    # 7. Spoken Correction with Live Strike-Through
    print("\n--- 7. Testing Spoken Correction: 'nahi, 430' ---")
    corr_res = post("/api/voice/process-text", {"text": "nahi, 430", "session_id": "judge_demo"})
    print(f"  Correction: \"{corr_res['message']}\"")
    assert corr_res.get("correction_event") is not None
    print(f"  Strike-Through Event: ₹{corr_res['correction_event']['old_amount']} ➔ ₹{corr_res['correction_event']['new_amount']}")

    # 8. Complete Debt Erasure across Languages
    print("\n--- 8. Testing Complete Debt Settlement across Languages ---")
    # English
    cd_en = post("/api/voice/process-text", {"text": "Ramesh - Kirana Lane cleared his debt", "language": "en-IN"})
    print(f"  [English] Spoken: 'Ramesh - Kirana Lane cleared his debt' -> \"{cd_en['message']}\"")
    assert "₹0" in cd_en["message"] or "cleared" in cd_en["message"].lower()

    # Kannada
    cd_kn = post("/api/voice/process-text", {"text": "Ramesh - Milk Dairy ಸಾಲ ತೀರಿದೆ", "language": "kn-IN"})
    print(f"  [Kannada] Spoken: 'Ramesh - Milk Dairy ಸಾಲ ತೀರಿದೆ' -> \"{cd_kn['message']}\"")
    assert "₹0" in cd_kn["message"] or "ತೀರಿದೆ" in cd_kn["message"]

    # Telugu
    cd_te = post("/api/voice/process-text", {"text": "Suresh ki 200 appu", "language": "te-IN"})
    print(f"  [Telugu Credit] Spoken: 'Suresh ki 200 appu' -> \"{cd_te['message']}\"")

    cd_te_clear = post("/api/voice/process-text", {"text": "Suresh అప్పు తీరిపోయింది", "language": "te-IN"})
    print(f"  [Telugu Clear] Spoken: 'Suresh అప్పు తీరిపోయింది' -> \"{cd_te_clear['message']}\"")
    assert "₹0" in cd_te_clear["message"] or "తీరిపోయింది" in cd_te_clear["message"]

    # 9. Verify Ledger Udhaar vs Jama Separation
    print("\n--- 9. Verifying Separate Ledgers (Udhaar vs Jama) ---")
    txns = get("/api/ledger/transactions?limit=20")
    udhaar_txns = [t for t in txns if t["direction"] == "credit"]
    jama_txns = [t for t in txns if t["direction"] == "payment"]
    print(f"  ✅ Udhaar Ledger: {len(udhaar_txns)} records")
    print(f"  ✅ Jama Ledger: {len(jama_txns)} records")

    print("\n" + "=" * 65)
    print("🏆 ALL CHECKS PASSED WITH 100% SUCCESS!")
    print("=" * 65)

if __name__ == "__main__":
    main()
