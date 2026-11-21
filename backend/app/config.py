"""
BolKhata Configuration
Loads environment variables and provides typed settings.
"""

from pydantic_settings import BaseSettings
from typing import List
import secrets


class Settings(BaseSettings):
    """Application settings loaded from .env file."""

    # ── Gnani.ai API ──────────────────────────────────────────
    gnani_api_key: str = ""
    gnani_api_base_url: str = "https://api.vachana.ai"
    gnani_stt_model: str = "prisma-v3.0"
    gnani_tts_model: str = "timbre-v2.5"
    gnani_tts_voice: str = "Nalini"
    default_language: str = "hi-IN"

    # ── Database ──────────────────────────────────────────────
    database_url: str = "sqlite+aiosqlite:///./bolkhata.db"
    db_encryption_key: str = secrets.token_hex(32)
    supabase_url: str = "https://bniyjwlqzrnszxzacomp.supabase.co"
    supabase_anon_key: str = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImJuaXlqd2xxenJuc3p4emFjb21wIiwicm9sZSI6ImFub24iLCJpYXQiOjE3OTUyNzE2MzEsImV4cCI6MjExMDg0NzYzMX0.7-YfHIR2yBEL6WicrC8jDNVZOT6CbDnufbiDjFZFl_c"

    # ── Server ────────────────────────────────────────────────
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = True
    cors_origins: str = "http://localhost:3000,http://localhost:5173,http://127.0.0.1:3000,http://127.0.0.1:5173"

    @property
    def cors_origins_list(self) -> List[str]:
        return [origin.strip() for origin in self.cors_origins.split(",")]

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Singleton settings instance
settings = Settings()
