# BolKhata Frontend - Hands-Free AI Voice Ledger

Mobile-first voice ledger and pitch landing page for Indian Kirana stores, engineered following the **Cyber Serif** design system.

## 🚀 Key Features

- **Cyber Serif Visual Language:**
  - High-contrast Near-Black (`#050505`) & Paper (`#EBEBEB`) background
  - Surgical Emerald (`#10B981`) accenting active voice states, CTA glow, and Jama figures
  - Newsreader serif display typography paired with Inter and Space Grotesk technical labels
  - Shimmer borders, spotlight cursor tracking, and glass morphing blobs
  - **Adaptive Lite Tier:** Auto-detected for low-memory devices (<= 2 GB RAM / reduced motion) to prevent GPU blur lag on budget smartphones.

- **Voice Pipeline & Hackathon Demo Replay:**
  - Push-to-talk mic button with idle, listening, thinking, and speaking waveforms.
  - Streaming WebSocket integration with backend (`/api/voice/ws`) with REST fallback.
  - **5-Step Hackathon Demo Replay** in Developer Panel:
    1. `"Ramesh ka 340 udhaar"` (Code-mixed digits parsing)
    2. `"Nahi, 430"` (In-place dynamic ledger correction)
    3. `"Ramesh"` (Spoken disambiguation sheet)
    4. `"Ramesh ne 200 diya kal"` (Payment with relative date parsing)
    5. `"Ramesh ka total?"` (Sub-2s voice financial query answer)
  - Telemetry timer badge showing measured per-stage latency (STT, NLU, TTS).

- **Offline-First & Local Storage:**
  - IndexedDB caching powered by **Dexie.js**.
  - Service Worker precaching with **vite-plugin-pwa**.
  - Offline outbox sync for queued manual entries.

## 🛠️ Scripts

- `npm run dev` - Launch Vite development server at `http://localhost:5173`
- `npm run build` - TypeScript check & production bundle build (Gzipped: ~101 KB)
- `npm run preview` - Preview production build
