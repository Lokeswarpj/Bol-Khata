# 🎙️ BolKhata (बोल खाता)
> **Hands-Free AI Voice Ledger for Kirana Stores**  
> *Theme: PS2: Voice Khata (Code-Mixed Voice AI for Informal Retail)*  
> **Team Drona** | Team ID: `F39B2FDB3CA4` | SJCIT | Build Bengaluru 2.0 Hackathon

---

## 🏆 Project Overview

**BolKhata** is an enterprise-grade, voice-first digital ledger crafted specifically for the chaotic, high-noise rush hours of Indian neighborhood Kirana stores. 

Kirana shopkeepers manage customer credit (*udhaar*) and daily cash reconciliations while weighing grains, packing groceries, and dealing with street traffic. **Nobody has time to type on a glass screen during a sale.**

BolKhata listens across the counter, parses code-mixed Indic-English shop speech, records credit/debit entries accurately, manages anaphora (multi-action compound utterances), and answers balance queries aloud within **2 seconds**—completely hands-free.

---

## 🎯 Hackathon Criteria Alignment & What Makes It a Winner

| Required Track Requirement | How BolKhata Solves It | Technical Implementation |
|---|---|---|
| **1. Numbers Under Noise** | Captures spoken numerals in any code-mixed format: `"340"`, `"teen sau chaalis"`, `"three-forty"`, and Indian Kirana idioms (`"dedh sau"`, `"dhai sau"`, `"sadhe teen sau"`). | Advanced hierarchical token stream parsing + colloquial English compound solver in `app/services/number_parser.py`. |
| **2. Compound & Anaphora Ledger Logic** | Accurately processes `"Ramesh ka 340 udhaar, kal 200 diya tha"` by creating two ledger entries: ₹340 credit today, and ₹200 payment for yesterday (*kal*), inheriting the customer name across clauses. | Multi-clause tokenizer, anaphora resolver & temporal relative date engine in `app/services/nlu_parser.py`. |
| **3. Spoken Corrections** | Spoken cues like `"nahi, 430"` instantly supersede and correct the previous erroneous transaction in session memory. | Contextual session state machine in `app/services/session_state.py` & atomic SQL correction replacement. |
| **4. Spoken Disambiguation** | If two customers share a name (e.g. Ramesh Sharma vs. Ramesh Verma), asks: *"Kaun wale Ramesh?"* and waits for conversational resolution. | Stateful pending action queue in `session_manager` with fuzzy name prefix matching. |
| **5. Sub-2s Voice Answers** | Instant answers to queries like `"Aaj kitna udhaar gaya?"` or `"Ramesh ka total?"`. | High-performance pre-aggregated async SQL queries + Gnani Timbre TTS streaming. |
| **6. Responsible AI & DPDP Guardrails** | AI disclosure on 1st turn (`"Namaste! Main BolKhata hoon..."`), opt-in-only polite reminders with zero coercive/threat language, AES-256 encrypted fields, and one-click demo transcript purge. | Compliant rules engine in `app/services/reminder_service.py` & `app/routers/compliance.py`. |

---

## 🛠️ Architecture & Tech Stack

```
                   ┌───────────────────────────────────────┐
                   │    Shopkeeper Spoken Counter Audio    │
                   └──────────────────┬────────────────────┘
                                      │
                                      ▼
               ┌───────────────────────────────────────────────┐
               │    Gnani.ai Prisma STT (Noise-Robust Multilingual)   │
               └──────────────────────┬────────────────────────┘
                                      │
                                      ▼ (Transcript: "Ramesh ka 340 udhaar, kal 200 diya tha")
               ┌───────────────────────────────────────────────┐
               │         BolKhata Code-Mixed NLU Engine         │
               │  • Clause Segmenter & Anaphora Resolver       │
               │  • Indic & English Colloquial Numeral Engine  │
               │  • Temporal Date Engine ("kal" / "parso")     │
               │  • State Machine (Disambiguation / Correction)│
               └──────────────────────┬────────────────────────┘
                                      │
                                      ▼
               ┌───────────────────────────────────────────────┐
               │              Ledger Execution Engine          │
               │  • Async SQLite with AES-256 Encryption       │
               │  • Real-time Net Balance Calculation          │
               │  • DPDP Opt-In & Compliance Validator         │
               └──────────────────────┬────────────────────────┘
                                      │
                                      ▼
               ┌───────────────────────────────────────────────┐
               │      Gnani.ai Timbre TTS (Indian Voices)      │
               │    "Done! Ramesh ka ₹340 udhaar darj kiya."   │
               └───────────────────────────────────────────────┘
```

- **Backend**: Python 3.12, FastAPI, Uvicorn (Async)
- **Database**: SQLite with `aiosqlite` & `SQLAlchemy 2.0` (Offline-first, encrypted at rest)
- **Speech Stack**: Gnani.ai Prisma v3.0 (STT) + Timbre v2.5 (TTS)
- **Security & Privacy**: Cryptography (AES-256 Fernet + PBKDF2), DPDP Act compliance

---

## 🚀 Quickstart Guide (Step-by-Step)

### 1. Prerequisites
- Python 3.10+ (Python 3.12 recommended)
- Git

### 2. Setup Virtual Environment & Install Dependencies
Open a terminal in the project directory:

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate on Windows PowerShell:
.\venv\Scripts\Activate.ps1
# (Or on Command Prompt: .\venv\Scripts\activate.bat)

# Install dependencies
pip install -r requirements.txt
```

### 3. Configure Environment Variables
Copy `.env.example` to `.env`:

```bash
cp .env.example .env
```

Open `.env` and set your credentials:
```ini
# Gnani.ai API Key (from https://app.gnani.ai)
GNANI_API_KEY=your_gnani_api_key_here

# SQLite Database URL
DATABASE_URL=sqlite+aiosqlite:///./bolkhata.db

# Encryption Key (Auto-generated or custom hex)
DB_ENCRYPTION_KEY=your_random_64_char_hex_key
```

### 4. Run the Verification Test Suite
Ensure all 5 hackathon test suites pass with 100%:

```bash
python test_suite.py
```

### 5. Launch the Server
```bash
python run.py
```
Or with Uvicorn:
```bash
uvicorn app.main:app --reload --port 8000
```

- **Interactive Counter Web App**: [http://127.0.0.1:8000/](http://127.0.0.1:8000/)
- **Swagger Interactive API Documentation**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

---

## 📡 API Reference Overview

### Voice Processing Endpoints
- `POST /api/voice/process`: Accepts audio file upload (`.wav`, `.mp3`, `.m4a`) or form data.
- `POST /api/voice/process-text`: Accepts raw text command (useful for testing without microphone).
- `WS /api/voice/ws`: High-performance bidirectional WebSocket for real-time streaming audio and spoken responses.

### Ledger Endpoints
- `GET /api/ledger/summary`: Overall ledger metrics (today credit, today payment, total net balance).
- `GET /api/ledger/transactions`: Filterable list of all ledger transactions.
- `POST /api/ledger/transaction`: Manually create a ledger entry.
- `DELETE /api/ledger/transaction/{id}`: Cancel/correct a transaction.

### Customer Endpoints
- `GET /api/customers/`: List all registered customers and current balances.
- `POST /api/customers/`: Register new customer with optional contact details.
- `GET /api/customers/{id}`: Detailed customer balance breakdown.

### Compliance & DPDP Endpoints
- `POST /api/compliance/consent/{id}`: Update opt-in consent for polite payment reminders.
- `GET /api/compliance/reminder/{id}`: Generate non-coercive, courteous reminder notice.
- `GET /api/compliance/export/{id}`: Export customer history in AES-256 encrypted payload.
- `DELETE /api/compliance/purge-demo-transcripts`: Wipe all stored demo transcripts after judging.

---

## 🧪 Testing with Real Counter Audio or Gnani API

When you receive your official Gnani API key from the hackathon organizers:
1. Paste it into `backend/.env` under `GNANI_API_KEY=...`
2. Restart the server (`python run.py`).
3. Now any uploaded audio file or WebSocket audio chunk will automatically route to Gnani Prisma STT and synthesize natural Indian speech responses via Gnani Timbre TTS!
