"""
BolKhata - AES-256 Encryption Utilities
DPDP Act compliant: Ledger data encrypted at rest.
"""

import base64
import os
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

from app.config import settings


def _derive_key(password: str, salt: bytes = b"bolkhata_salt_v1") -> bytes:
    """Derive a Fernet-compatible key from a password string."""
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=480000,
    )
    key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
    return key


# Global Fernet instance
_fernet = Fernet(_derive_key(settings.db_encryption_key))


def encrypt_text(plaintext: str) -> str:
    """Encrypt a string and return base64-encoded ciphertext."""
    return _fernet.encrypt(plaintext.encode()).decode()


def decrypt_text(ciphertext: str) -> str:
    """Decrypt a base64-encoded ciphertext back to plaintext."""
    return _fernet.decrypt(ciphertext.encode()).decode()


def encrypt_bytes(data: bytes) -> bytes:
    """Encrypt raw bytes."""
    return _fernet.encrypt(data)


def decrypt_bytes(data: bytes) -> bytes:
    """Decrypt raw bytes."""
    return _fernet.decrypt(data)
