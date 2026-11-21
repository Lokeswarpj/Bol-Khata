"""
BolKhata - Voice WebSocket Router
Handles real-time voice input via WebSocket and REST endpoints.
Complete voice pipeline: Audio → STT → NLU → Ledger → TTS → Response
"""

import base64
import json
import logging
import uuid
from typing import Optional

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, UploadFile, File, Form
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.services.gnani_stt import stt_service
from app.services.gnani_tts import tts_service
from app.services.ledger_engine import LedgerEngine
from app.models import VoiceInput, VoiceResponse

logger = logging.getLogger("bolkhata.voice")

router = APIRouter(prefix="/api/voice", tags=["Voice"])


# ═══════════════════════════════════════════════════════════════
# REST Endpoint: Process voice (audio file upload)
# ═══════════════════════════════════════════════════════════════

@router.post("/process", response_model=VoiceResponse)
async def process_voice(
    audio: Optional[UploadFile] = File(None),
    text: Optional[str] = Form(None),
    language: str = Form("hi-IN"),
    session_id: str = Form(default_factory=lambda: str(uuid.uuid4())),
    db: AsyncSession = Depends(get_db),
):
    """
    Process a voice command (audio file or pre-transcribed text).
    
    - Upload audio → STT transcription → NLU parsing → Ledger action → TTS response
    - Or send pre-transcribed text directly (for testing)
    """
    transcript = text
    
    # Step 1: STT - Transcribe audio if provided
    if audio and not text:
        audio_data = await audio.read()
        stt_result = await stt_service.transcribe_audio(
            audio_data=audio_data,
            language=language,
            content_type=audio.content_type or "audio/wav",
        )
        
        if not stt_result["success"] or not stt_result["transcript"]:
            return VoiceResponse(
                success=False,
                message="Awaaz samajh nahi aayi. Kripya phir se boliye. (Could not understand the audio. Please try again.)",
            )
        
        transcript = stt_result["transcript"]
    
    if not transcript:
        return VoiceResponse(
            success=False,
            message="Koi input nahi mila. Audio ya text bhejiye. (No input received.)",
        )
    
    # Step 2: NLU + Ledger - Process the transcribed text
    ledger = LedgerEngine(db)
    response = await ledger.process_voice_command(transcript, session_id=session_id)
    
    # Step 3: TTS - Generate spoken response
    if response.message:
        tts_result = await tts_service.synthesize(
            text=response.message,
            language=language,
            session_id=session_id,
        )
        if tts_result["success"]:
            response.audio_base64 = tts_result["audio_base64"]
    
    return response


@router.post("/process-text", response_model=VoiceResponse)
async def process_text(
    input_data: VoiceInput,
    db: AsyncSession = Depends(get_db),
):
    """
    Process a text command directly (no audio).
    Useful for testing the NLU pipeline without STT.
    """
    if not input_data.text:
        return VoiceResponse(
            success=False,
            message="Koi text nahi mila. (No text received.)",
        )
    
    session_id = str(uuid.uuid4())
    ledger = LedgerEngine(db)
    response = await ledger.process_voice_command(input_data.text, session_id=session_id)
    
    # Optionally generate TTS
    if input_data.audio_base64 is not None and response.message:
        tts_result = await tts_service.synthesize(
            text=response.message,
            language=input_data.language,
            session_id=session_id,
        )
        if tts_result["success"]:
            response.audio_base64 = tts_result["audio_base64"]
    
    return response


# ═══════════════════════════════════════════════════════════════
# WebSocket: Real-time voice processing
# ═══════════════════════════════════════════════════════════════

@router.websocket("/ws")
async def voice_websocket(websocket: WebSocket, db: AsyncSession = Depends(get_db)):
    """
    WebSocket endpoint for real-time voice processing.
    
    Protocol:
    1. Client connects
    2. Server sends AI disclosure (Responsible AI)
    3. Client sends audio chunks (base64 JSON) or text commands
    4. Server responds with text + audio (base64)
    
    Message format (client → server):
    {
        "type": "audio" | "text",
        "data": "<base64 audio>" | "<text command>",
        "language": "hi-IN"
    }
    
    Message format (server → client):
    {
        "type": "response" | "error" | "disclosure",
        "text": "spoken response text",
        "audio": "<base64 audio>",
        "intent": { ... parsed intent ... },
        "transaction": { ... if any ... },
        "needs_disambiguation": false,
        "disambiguation_options": []
    }
    """
    await websocket.accept()
    session_id = str(uuid.uuid4())
    ledger = LedgerEngine(db)
    
    logger.info(f"WebSocket connected: session={session_id}")
    
    try:
        # Send AI disclosure on first connection (Responsible AI requirement)
        disclosure = tts_service.get_ai_disclosure()
        await websocket.send_json({
            "type": "disclosure",
            "text": disclosure,
            "session_id": session_id,
        })
        
        while True:
            # Receive message from client
            raw_data = await websocket.receive_text()
            
            try:
                message = json.loads(raw_data)
            except json.JSONDecodeError:
                await websocket.send_json({
                    "type": "error",
                    "text": "Invalid message format. Send JSON.",
                })
                continue
            
            msg_type = message.get("type", "text")
            language = message.get("language", "hi-IN")
            transcript = None
            
            # Process based on message type
            if msg_type == "audio":
                # Decode and transcribe audio
                audio_b64 = message.get("data", "")
                if not audio_b64:
                    await websocket.send_json({
                        "type": "error",
                        "text": "No audio data received.",
                    })
                    continue
                
                audio_data = base64.b64decode(audio_b64)
                stt_result = await stt_service.transcribe_audio(
                    audio_data=audio_data,
                    language=language,
                )
                
                if not stt_result["success"] or not stt_result["transcript"]:
                    await websocket.send_json({
                        "type": "error",
                        "text": "Awaaz samajh nahi aayi. Phir se boliye.",
                    })
                    continue
                
                transcript = stt_result["transcript"]
            
            elif msg_type == "text":
                transcript = message.get("data", "").strip()
            
            if not transcript:
                continue
            
            # Process the command through ledger engine
            response = await ledger.process_voice_command(transcript, session_id)
            
            # Generate TTS response
            audio_b64 = None
            if response.message:
                tts_result = await tts_service.synthesize(
                    text=response.message,
                    language=language,
                    session_id=session_id,
                )
                if tts_result["success"]:
                    audio_b64 = tts_result["audio_base64"]
            
            # Send response
            response_data = {
                "type": "response",
                "text": response.message,
                "audio": audio_b64,
                "success": response.success,
                "transcript": transcript,
                "needs_disambiguation": response.needs_disambiguation,
                "disambiguation_options": response.disambiguation_options,
            }
            
            if response.intent:
                response_data["intent"] = {
                    "type": response.intent.intent.value,
                    "customer": response.intent.customer_name,
                    "amount": response.intent.amount,
                    "direction": response.intent.direction.value if response.intent.direction else None,
                    "confidence": response.intent.confidence,
                }
            
            if response.transaction:
                response_data["transaction"] = {
                    "id": response.transaction.id,
                    "customer_name": response.transaction.customer_name,
                    "amount": response.transaction.amount,
                    "direction": response.transaction.direction,
                    "date": str(response.transaction.transaction_date),
                }
            
            await websocket.send_json(response_data)
    
    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected: session={session_id}")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        try:
            await websocket.send_json({
                "type": "error",
                "text": f"Server error: {str(e)}",
            })
        except Exception:
            pass


# ═══════════════════════════════════════════════════════════════
# Utility endpoints
# ═══════════════════════════════════════════════════════════════

@router.get("/stt-config")
async def get_stt_config():
    """
    Get STT WebSocket configuration for direct browser-to-Gnani streaming.
    Frontend can use this to connect directly to Gnani for lower latency.
    """
    return {
        "websocket_url": stt_service.get_websocket_url(),
        "headers": stt_service.get_websocket_headers(),
        "model": stt_service.model,
        "language": stt_service.language,
    }


@router.post("/tts")
async def text_to_speech(
    text: str = Form(...),
    language: str = Form("hi-IN"),
):
    """Generate TTS audio from text."""
    result = await tts_service.synthesize(text=text, language=language)
    return result
