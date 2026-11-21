"""
BolKhata - Gnani.ai Text-to-Speech (TTS) Integration with Smart Token Saver
Features:
- Token-Saver Disk Cache: Caches generated audio hashes so repeated responses use 0 tokens!
- First-turn Responsible AI disclosure
- Graceful fallback to browser speech if tokens run low or offline
"""

import os
import hashlib
import httpx
import base64
import logging
from typing import Optional

from app.config import settings

logger = logging.getLogger("bolkhata.tts")

# AI Disclosure messages
AI_DISCLOSURE = {
    "hi-IN": "Namaste! Main BolKhata hoon, ek AI assistant. Dukaan ka hisaab rakhne mein madad karungi.",
    "en-IN": "Hello! I am BolKhata, an AI assistant. I will help manage your shop's accounts.",
    "kn-IN": "Namaskara! Naanu BolKhata, ondu AI sahayaka. Nimma angadiya lekka nodikollalu sahaya maaduttene.",
    "te-IN": "Namaskaram! Nenu BolKhata, oka AI sahayakudu. Mee shop lekkalalo sahayam chestanu.",
}

# Optimal language-specific native voices in Gnani timbre-v2.5
LANGUAGE_VOICES = {
    "hi-IN": "Madhuri",   # Native crystal clear Hindi
    "en-IN": "Vidya",     # Clean Indian English
    "kn-IN": "Nayana",    # Native Kannada
    "te-IN": "Lalita",    # Native Telugu
}

# Local disk cache directory for audio files
CACHE_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".audio_cache")
os.makedirs(CACHE_DIR, exist_ok=True)


class GnaniTTSService:
    """Gnani.ai TTS with disk caching to protect limited hackathon tokens."""

    def __init__(self):
        self.api_key = settings.gnani_api_key
        self.base_url = settings.gnani_api_base_url
        self.model = settings.gnani_tts_model
        self.voice = settings.gnani_tts_voice
        self.language = settings.default_language
        self._first_turn_done = {}

    def _get_cache_path(self, text: str, lang: str, voice: str) -> str:
        key = f"{text}|{lang}|{voice}".encode("utf-8")
        h = hashlib.sha256(key).hexdigest()
        return os.path.join(CACHE_DIR, f"{h}.wav")

    async def synthesize(
        self,
        text: str,
        language: Optional[str] = None,
        voice: Optional[str] = None,
        speed: float = 1.0,
        session_id: Optional[str] = None,
    ) -> dict:
        lang = language or self.language
        if lang.startswith("hi"):
            lang = "hi-IN"
        elif lang.startswith("kn"):
            lang = "kn-IN"
        elif lang.startswith("te"):
            lang = "te-IN"
        elif lang.startswith("en"):
            lang = "en-IN"

        voice_name = voice or LANGUAGE_VOICES.get(lang, self.voice)

        # Check local cache first (Saves 100% of Gnani tokens for cached sentences!)
        cache_file = self._get_cache_path(text, lang, voice_name)
        if os.path.exists(cache_file):
            try:
                with open(cache_file, "rb") as f:
                    cached_bytes = f.read()
                logger.info(f"⚡ [Token Saver] Served from cache (0 tokens consumed): {text[:40]}...")
                return {
                    "audio_base64": base64.b64encode(cached_bytes).decode("utf-8"),
                    "cached": True,
                    "text_spoken": text,
                    "success": True,
                }
            except Exception as e:
                logger.warning(f"Failed to read audio cache: {e}")

        # If no API key configured, return success=False so frontend uses browser WebSpeech (0 tokens)
        if not self.api_key or self.api_key == "your_gnani_api_key_here":
            return {
                "audio_base64": "",
                "cached": False,
                "text_spoken": text,
                "success": False,
                "message": "Gnani API key not set - falling back to browser speech.",
            }

        headers = {
            "X-API-Key-ID": self.api_key,
            "Content-Type": "application/json",
        }
        payload = {
            "text": text,
            "voice": voice_name,
            "model": self.model,
            "language": lang,
            "speed": speed,
        }

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(
                    f"{self.base_url}/api/v1/tts/inference",
                    json=payload,
                    headers=headers,
                )
                response.raise_for_status()
                audio_data = response.content

                # Cache audio to disk to save future tokens
                with open(cache_file, "wb") as f:
                    f.write(audio_data)

                logger.info(f"🔊 Gnani TTS generated & cached ({len(audio_data)} bytes)")
                return {
                    "audio_base64": base64.b64encode(audio_data).decode("utf-8"),
                    "cached": False,
                    "text_spoken": text,
                    "success": True,
                }
        except Exception as e:
            logger.error(f"Gnani TTS error: {e}")
            return {
                "audio_base64": "",
                "cached": False,
                "text_spoken": text,
                "success": False,
                "error": str(e),
            }

    def get_ai_disclosure(self, language: Optional[str] = None) -> str:
        lang = language or self.language
        return AI_DISCLOSURE.get(lang, AI_DISCLOSURE["en-IN"])


tts_service = GnaniTTSService()
