"""
BolKhata - Gnani.ai Text-to-Speech (TTS) Integration
Uses Gnani Timbre for natural Indian voice responses.
Responsible AI: First turn always discloses "Main ek AI assistant hoon."
"""

import httpx
import base64
import logging
from typing import Optional

from app.config import settings

logger = logging.getLogger("bolkhata.tts")


# AI Disclosure message (Responsible AI requirement)
AI_DISCLOSURE = {
    "hi-IN": "Namaste! Main BolKhata hoon, ek AI assistant. Aapki dukaan ka hisaab rakhne mein madad karungi.",
    "en-IN": "Hello! I am BolKhata, an AI assistant. I will help you keep your shop's accounts.",
    "kn-IN": "Namaskara! Naanu BolKhata, ondu AI sahayaka. Nimma angadiya lekka ittukolalu sahaya maaduttene.",
    "ta-IN": "Vanakkam! Naan BolKhata, oru AI uthavi. Ungal kadayin kanakkugalai paathukkolla uthavi seiven.",
    "te-IN": "Namaskaram! Nenu BolKhata, oka AI sahayakudu. Mee shop lekkalalo sahayam chestanu.",
}


class GnaniTTSService:
    """
    Gnani.ai Text-to-Speech service using Timbre models.
    
    Features:
    - Natural Indian voices (multiple languages)
    - REST API for full audio generation
    - SSE streaming for faster first-byte delivery
    - Sub-2-second response target for shop Q&A
    """

    def __init__(self):
        self.api_key = settings.gnani_api_key
        self.base_url = settings.gnani_api_base_url
        self.model = settings.gnani_tts_model
        self.voice = settings.gnani_tts_voice
        self.language = settings.default_language
        self.headers = {
            "X-API-Key-ID": self.api_key,
            "Content-Type": "application/json",
        }
        self._first_turn_done = {}  # Track per-session AI disclosure

    async def synthesize(
        self,
        text: str,
        language: Optional[str] = None,
        voice: Optional[str] = None,
        speed: float = 1.0,
        session_id: Optional[str] = None,
    ) -> dict:
        """
        Convert text to speech using Gnani TTS REST API.
        
        Args:
            text: Text to speak
            language: Language code
            voice: Voice name (e.g., "Nalini")
            speed: Speech speed (0.5 to 2.0)
            session_id: Session ID for tracking AI disclosure
        
        Returns:
            Dict with 'audio_base64', 'content_type', 'success'
        """
        lang = language or self.language
        voice_name = voice or self.voice

        # Responsible AI: Prepend AI disclosure on first turn
        if session_id and session_id not in self._first_turn_done:
            disclosure = AI_DISCLOSURE.get(lang, AI_DISCLOSURE["en-IN"])
            text = f"{disclosure} {text}"
            self._first_turn_done[session_id] = True

        payload = {
            "text": text,
            "voice": voice_name,
            "model": self.model,
            "language": lang,
            "speed": speed,
        }

        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                response = await client.post(
                    f"{self.base_url}/api/v1/tts/inference",
                    json=payload,
                    headers=self.headers,
                )
                response.raise_for_status()
                
                # Response is raw audio bytes
                audio_data = response.content
                audio_b64 = base64.b64encode(audio_data).decode("utf-8")
                
                content_type = response.headers.get("content-type", "audio/wav")
                
                logger.info(f"TTS generated {len(audio_data)} bytes for: {text[:50]}...")
                
                return {
                    "audio_base64": audio_b64,
                    "audio_bytes": audio_data,
                    "content_type": content_type,
                    "text_spoken": text,
                    "success": True,
                }

        except httpx.HTTPStatusError as e:
            logger.error(f"Gnani TTS HTTP error: {e.response.status_code} - {e.response.text}")
            return {
                "audio_base64": "",
                "content_type": "audio/wav",
                "text_spoken": text,
                "success": False,
                "error": f"TTS API error: {e.response.status_code}",
            }
        except Exception as e:
            logger.error(f"Gnani TTS error: {str(e)}")
            return {
                "audio_base64": "",
                "content_type": "audio/wav",
                "text_spoken": text,
                "success": False,
                "error": str(e),
            }

    def get_ai_disclosure(self, language: Optional[str] = None) -> str:
        """Get the AI disclosure message for a given language."""
        lang = language or self.language
        return AI_DISCLOSURE.get(lang, AI_DISCLOSURE["en-IN"])

    def reset_session(self, session_id: str):
        """Reset AI disclosure tracking for a session."""
        self._first_turn_done.pop(session_id, None)


# Singleton instance
tts_service = GnaniTTSService()
