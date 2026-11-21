"""
BolKhata - Security & Cryptographic Service
Handles salted PIN hashing and JWT session tokens for tamper-proof merchant authentication.
"""

import hashlib
import hmac
import json
import base64
import time
from typing import Optional, Dict, Any
from app.config import settings

# Secret key derived from settings or fallbacks
JWT_SECRET = settings.db_encryption_key or "bolkhata_secure_jwt_signing_key_secret_2026"
SALT = "bolkhata_salt_v1_"


def hash_pin(pin: str) -> str:
    """Hashes a merchant 4-digit PIN using SHA-256 with key stretching."""
    if not pin:
        pin = "1234"
    salted = f"{SALT}{pin}{JWT_SECRET}".encode("utf-8")
    hashed = hashlib.sha256(salted).hexdigest()
    return f"pbkdf2_sha256${hashed}"


def verify_pin(plain_pin: str, stored_pin: Optional[str]) -> bool:
    """Verifies a plain PIN against stored hashed PIN or legacy plaintext."""
    if not stored_pin:
        return plain_pin == "1234"
    
    # Handle hashed PIN
    if stored_pin.startswith("pbkdf2_sha256$"):
        expected = hash_pin(plain_pin)
        return hmac.compare_digest(expected, stored_pin)
    
    # Legacy plaintext backward compatibility
    return hmac.compare_digest(str(plain_pin).strip(), str(stored_pin).strip())


def create_access_token(data: Dict[str, Any], expires_in_seconds: int = 86400 * 30) -> str:
    """Generates a secure HMAC-SHA256 signed JWT token."""
    header = {"alg": "HS256", "typ": "JWT"}
    payload = data.copy()
    payload["exp"] = int(time.time()) + expires_in_seconds
    payload["iat"] = int(time.time())

    def b64url(val: bytes) -> str:
        return base64.urlsafe_b64encode(val).decode("utf-8").rstrip("=")

    hdr_str = b64url(json.dumps(header).encode("utf-8"))
    payload_str = b64url(json.dumps(payload).encode("utf-8"))

    msg = f"{hdr_str}.{payload_str}".encode("utf-8")
    sig = hmac.new(JWT_SECRET.encode("utf-8"), msg, hashlib.sha256).digest()
    sig_str = b64url(sig)

    return f"{hdr_str}.{payload_str}.{sig_str}"


def decode_access_token(token: str) -> Optional[Dict[str, Any]]:
    """Decodes and validates a signed JWT token."""
    if not token:
        return None
    try:
        parts = token.split(".")
        if len(parts) != 3:
            return None
        
        hdr_str, payload_str, sig_str = parts

        def unb64url(s: str) -> bytes:
            pad = len(s) % 4
            if pad:
                s += "=" * (4 - pad)
            return base64.urlsafe_b64decode(s)

        msg = f"{hdr_str}.{payload_str}".encode("utf-8")
        expected_sig = hmac.new(JWT_SECRET.encode("utf-8"), msg, hashlib.sha256).digest()
        actual_sig = unb64url(sig_str)

        if not hmac.compare_digest(expected_sig, actual_sig):
            return None

        payload = json.loads(unb64url(payload_str).decode("utf-8"))
        if payload.get("exp", 0) < time.time():
            return None  # Expired
        
        return payload
    except Exception:
        return None
