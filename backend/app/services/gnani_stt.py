"""
BolKhata - Gnani.ai Speech-to-Text (STT) Integration
Uses Gnani Prisma for noise-resilient, code-mixed Indic+English transcription.
"""

import httpx
import json
import base64
import logging
from typing import Optional, AsyncGenerator

from app.config import settings

logger = logging.getLogger("bolkhata.stt")


class GnaniSTTService:
    """
    Gnani.ai Speech-to-Text service using Prisma models.
    
    Supports:
    - REST API for short audio clips (< 30s)
    - WebSocket streaming for real-time transcription
    - Auto language detection with code-mix support
    """

    def __init__(self):
        self.api_key = settings.gnani_api_key
        self.base_url = settings.gnani_api_base_url
        self.model = settings.gnani_stt_model
        self.language = settings.default_language
        self.headers = {
            "X-API-Key-ID": self.api_key,
            "Content-Type": "application/json",
        }

    async def transcribe_audio(
        self,
        audio_data: bytes,
        language: Optional[str] = None,
        content_type: str = "audio/wav",
    ) -> dict:
        """
        Transcribe audio using Gnani STT REST API.
        
        Args:
            audio_data: Raw audio bytes (WAV, MP3, OGG, FLAC, AAC, M4A)
            language: Language code (e.g., "hi-IN", "en-IN", "indic-auto")
            content_type: MIME type of audio
        
        Returns:
            Dict with 'transcript', 'confidence', 'language', etc.
        """
        lang = language or self.language
        if not lang or lang == "auto":
            lang = "indic-auto"
        
        # Determine audio extension
        ext = "wav"
        if "webm" in content_type:
            ext = "webm"
        elif "ogg" in content_type:
            ext = "ogg"
        elif "mp3" in content_type:
            ext = "mp3"

        headers = {
            "X-API-Key-ID": self.api_key,
        }

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.base_url}/stt/v3",
                    headers=headers,
                    files={"audio_file": (f"speech.{ext}", audio_data, content_type)},
                    data={"language_code": lang},
                )
                response.raise_for_status()
                result = response.json()
                
                transcript = result.get("transcript", "")
                logger.info(f"STT result: {transcript[:100]}")
                
                return {
                    "transcript": transcript,
                    "confidence": result.get("confidence", 0.9),
                    "language": result.get("language", lang),
                    "words": result.get("words", []),
                    "success": True,
                }

        except httpx.HTTPStatusError as e:
            logger.error(f"Gnani STT HTTP error: {e.response.status_code} - {e.response.text}")
            return {
                "transcript": "",
                "confidence": 0.0,
                "language": lang,
                "success": False,
                "error": f"STT API error: {e.response.status_code}",
            }
        except Exception as e:
            logger.error(f"Gnani STT error: {str(e)}")
            return {
                "transcript": "",
                "confidence": 0.0,
                "language": lang,
                "success": False,
                "error": str(e),
            }

    async def transcribe_file(
        self,
        file_path: str,
        language: Optional[str] = None,
    ) -> dict:
        """Transcribe an audio file from disk."""
        with open(file_path, "rb") as f:
            audio_data = f.read()
        
        # Detect content type from extension
        ext = file_path.rsplit(".", 1)[-1].lower()
        content_types = {
            "wav": "audio/wav",
            "mp3": "audio/mp3",
            "ogg": "audio/ogg",
            "flac": "audio/flac",
            "m4a": "audio/m4a",
            "webm": "audio/webm",
        }
        content_type = content_types.get(ext, "audio/wav")
        
        return await self.transcribe_audio(audio_data, language, content_type)

    def get_websocket_url(self, language: Optional[str] = None) -> str:
        """
        Get WebSocket URL for real-time streaming STT.
        Used by the frontend to connect directly for low-latency streaming.
        """
        lang = language or self.language
        ws_base = self.base_url.replace("https://", "wss://").replace("http://", "ws://")
        return f"{ws_base}/stt/v3/stream?model={self.model}&language={lang}"

    def get_websocket_headers(self) -> dict:
        """Get headers needed for WebSocket connection to Gnani."""
        return {"X-API-Key-ID": self.api_key}


# Singleton instance
stt_service = GnaniSTTService()
