"""
BolKhata - FastAPI Application Entry Point
Hands-Free AI Voice Ledger for Kirana Stores
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
import os

from app.config import settings
from app.database import init_db, async_session
from app.services.seed import seed_demo_data

# ── Logging Setup ─────────────────────────────────────────────
logging.basicConfig(
    level=logging.DEBUG if settings.debug else logging.INFO,
    format="%(asctime)s | %(name)-28s | %(levelname)-7s | %(message)s",
)
logger = logging.getLogger("bolkhata")


# ── App Lifespan ──────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("=" * 65)
    logger.info("🎙️   BolKhata - Hands-Free AI Voice Ledger Initializing...")
    logger.info("=" * 65)
    
    # Initialize database schema
    await init_db()
    logger.info("✅ Database schema initialized & ready (Real data mode)")
    
    # Check Gnani.ai credentials
    if settings.gnani_api_key and settings.gnani_api_key != "your_gnani_api_key_here":
        logger.info(f"✅ Gnani.ai API Key loaded (Base URL: {settings.gnani_api_base_url})")
        logger.info(f"   STT Model: {settings.gnani_stt_model} | TTS Model: {settings.gnani_tts_model}")
    else:
        logger.warning("⚠️  Gnani API key not configured yet!")
        logger.warning("   Please update GNANI_API_KEY in backend/.env when available.")
        logger.info("   (Mock voice/text processing will remain fully operational for testing)")

    logger.info(f"🌐 Server running at: http://{settings.host}:{settings.port}")
    logger.info(f"📚 Interactive Swagger API Docs: http://{settings.host}:{settings.port}/docs")
    logger.info("=" * 65)
    
    yield
    
    logger.info("BolKhata backend shutting down cleanly.")


# ── FastAPI Application Instance ──────────────────────────────

app = FastAPI(
    title="BolKhata API",
    description=(
        "🎙️ **BolKhata**: Hands-Free AI Voice Ledger for Kirana Stores.\n\n"
        "Built for **Build Bengaluru 2.0 Hackathon (Theme: Voice Khata)** by **Team Drona (SJCIT)**.\n\n"
        "### Key Capabilities:\n"
        "- **Numbers Under Noise**: High-resilience parsing of digits, Hindi ('teen sau chaalis'), English ('three-forty'), and colloquial fractions ('dedh sau', 'dhai sau').\n"
        "- **Ledger Logic**: Multi-action compound sentence execution ('Ramesh ka 340 udhaar, kal 200 diya tha') with relative date recognition.\n"
        "- **Spoken Corrections**: 'nahi, 430' dynamically resolves and replaces prior erroneous entries.\n"
        "- **Spoken Disambiguation**: Queries ambiguous names and maintains state until clarified.\n"
        "- **Sub-2s Voice Answers**: Rapid financial queries ('Aaj kitna udhaar gaya?', 'Ramesh ka total?').\n"
        "- **Responsible AI & DPDP Compliance**: AI disclosure on first turn, polite opt-in-only reminders, encrypted at rest, and demo transcript purge."
    ),
    version="1.0.0",
    lifespan=lifespan,
)

# ── CORS Middleware ───────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Include Routers ───────────────────────────────────────────
from app.routers import voice, ledger, customers, compliance, owner

app.include_router(voice.router)
app.include_router(ledger.router)
app.include_router(customers.router)
app.include_router(compliance.router)
app.include_router(owner.router)


from fastapi.responses import JSONResponse, HTMLResponse, RedirectResponse
from app.services.supabase_service import supabase_service

# ── UI & Health Endpoints ─────────────────────────────────────

@app.get("/app", tags=["UI"])
@app.get("/pwa", tags=["UI"])
async def redirect_to_counter():
    """Redirects legacy PWA paths directly to the unified Counter Web App."""
    return RedirectResponse(url="/", status_code=302)


@app.get("/api/supabase/status", tags=["Cloud Database"])
async def get_supabase_status():
    """Returns real-time status of Supabase Cloud Database connection."""
    return await supabase_service.get_cloud_status()


@app.post("/api/supabase/sync", tags=["Cloud Database"])
async def trigger_supabase_sync():
    """Triggers full sync of all store owners, customers, and transactions to Supabase Cloud."""
    async with async_session() as session:
        return await supabase_service.sync_all_database(session)


@app.get("/", tags=["UI"])
async def demo_ui():
    """Serves the interactive BolKhata Counter Web App."""
    static_file = os.path.join(os.path.dirname(__file__), "static", "index.html")
    if os.path.exists(static_file):
        with open(static_file, "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    return {
        "app": "BolKhata",
        "version": "1.0.0",
        "status": "online",
        "team": "Drona (SJCIT)",
        "theme": "PS2: Voice Khata (Code-Mixed Voice AI for Informal Retail)",
        "docs_url": "/docs",
    }


@app.get("/api/info", tags=["Health"])
async def root():
    return {
        "app": "BolKhata",
        "version": "1.0.0",
        "status": "online",
        "team": "Drona (SJCIT)",
        "theme": "PS2: Voice Khata (Code-Mixed Voice AI for Informal Retail)",
        "docs_url": "/docs",
    }


@app.get("/health", tags=["Health"])
async def health():
    gnani_configured = bool(
        settings.gnani_api_key
        and settings.gnani_api_key != "your_gnani_api_key_here"
    )
    return {
        "status": "healthy",
        "database": "sqlite_async",
        "encryption": "AES-256",
        "gnani_api_ready": gnani_configured,
        "stt_model": settings.gnani_stt_model,
        "tts_model": settings.gnani_tts_model,
        "default_language": settings.default_language,
    }


@app.post("/api/test/parse", tags=["Testing"])
async def test_nlu_parse(text: str):
    """Diagnostic tool to inspect NLU parsing breakdown without DB mutation."""
    from app.services.nlu_parser import parse_voice_utterance
    actions = parse_voice_utterance(text)
    return {
        "input_utterance": text,
        "clauses_detected": len(actions),
        "actions": [
            {
                "clause": a.raw_text,
                "intent": a.intent.value,
                "customer": a.customer_name,
                "amount": a.amount,
                "direction": a.direction.value if a.direction else None,
                "date": str(a.transaction_date),
                "confidence": a.confidence,
            }
            for a in actions
        ],
    }
