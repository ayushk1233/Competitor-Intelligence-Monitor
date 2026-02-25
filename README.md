# 🔍 Competitor Intelligence Monitor

> **Strategic signals, not summaries.** Drop in 2–5 competitor names or URLs. Get a VC-grade intelligence briefing in under 90 seconds — powered by Gemini.

---

## What It Does

Most competitive research tools give you company descriptions. This gives you **signals** — the kind a founder or product strategist can act on today.

For each competitor it extracts:

| Signal | What it reveals |
|---|---|
| **Core Offering** | Exact problem solved and for whom |
| **ICP** | Who they're really selling to (from messaging evidence) |
| **Pricing Signals** | Tier names, price points, model, recent changes |
| **Hiring Signals** | Which functions dominate open roles → growth direction |
| **Recent Launches** | New features and product announcements |
| **Growth Signals** | Funding indicators, new markets, expansion patterns |
| **Risk Flags** | Pivot signals, inconsistent messaging, decline signs |
| **Momentum Score** | Calibrated 1–10 score using a 5-band rubric (not a default 7) |
| **Analyst Note** | One hard-hitting action item for the founder |

Then it synthesizes across all competitors:
- 🏆 **Market leader** + why they're hard to displace
- 🚀 **Fastest mover** + specific evidence
- 💡 **Messaging gaps** — the positioning territory nobody owns
- ⚠️ **Threat ranking** — who to watch most carefully
- 📋 **Executive briefing** — 6–8 sentence structured brief, ready to forward

---

## Two Ways to Use It

### 🖥️ Streamlit UI (Recommended)
Visual dashboard with progress tracking, competitor cards, and markdown export.

```bash
streamlit run frontend/app.py
```
→ Open `http://localhost:8501`

### ⚡ FastAPI + Swagger UI (API / Programmatic)
Full REST API with interactive docs — great for integrations, automation, or just exploring the response schema.

```bash
uvicorn backend.main:app --reload
```
→ Swagger UI: `http://localhost:8000/docs`  
→ ReDoc: `http://localhost:8000/redoc`

---

## Quick Start

### 1. Clone the repo
```bash
git clone https://github.com/YOUR_USERNAME/competitor-intel.git
cd competitor-intel
```

### 2. Create a virtual environment
```bash
python -m venv venv

# Mac / Linux
source venv/bin/activate

# Windows
venv\Scripts\activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure your API key
```bash
cp .env.example .env
```

Edit `.env`:
```env
GEMINI_API_KEY=your_key_here        # Required — get free at aistudio.google.com
JINA_API_KEY=your_key_here          # Optional — improves scraping quality
```

Get a free Gemini key → [aistudio.google.com/app/apikey](https://aistudio.google.com/app/apikey)

### 5. Launch
```bash
# Streamlit UI
streamlit run frontend/app.py

# OR FastAPI server
uvicorn backend.main:app --reload
```

---

## API Reference

### `POST /api/analyze`

Run the full 3-stage intelligence pipeline.

**Request body:**
```json
{
  "competitors": ["Notion", "Linear", "Basecamp"],
  "options": {
    "include_blog": true,
    "include_careers": true
  }
}
```

**Accepts names or URLs** — `"Notion"`, `"notion.so"`, or `"https://notion.so"` all work.

**Constraints:** minimum 2 competitors, maximum 5.

**Response:** Full `IntelligenceReport` — see schema at `/docs`.

---

### `GET /health`

Service health check.

```json
{ "status": "ok", "service": "competitor-intelligence-monitor" }
```

---

### Swagger UI

The FastAPI server auto-generates interactive docs with the full response schema, request validation, and a live **Try it out** button.

```
http://localhost:8000/docs
```

![Swagger UI](https://fastapi.tiangolo.com/img/index/index-03-swagger-02.png)

---

## Pipeline Architecture

```
Input (names or URLs)
        │
        ▼
┌─────────────────────────────────────────────────┐
│  Stage 1 — Scrape  (async, all competitors)      │
│  ├── Domain resolution (name → TLD probing)      │
│  ├── Jina AI Reader (clean markdown)             │
│  └── BeautifulSoup fallback (raw HTML clean)     │
│  Pages: homepage · pricing · about · blog · jobs │
└───────────────────────┬─────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────┐
│  Stage 2 — Analyze  (per competitor, sequential) │
│  ├── Token-aware page merging (priority order)   │
│  ├── Gemini prompt with 5-band momentum rubric   │
│  ├── Smart JSON cleaning (escape fixer + regex)  │
│  └── 429 rate-limit handler (reads retry_delay)  │
└───────────────────────┬─────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────┐
│  Stage 3 — Compare  (cross-competitor synthesis) │
│  ├── Structured comparison prompt                │
│  ├── Market leader · fastest mover · pivot       │
│  ├── Messaging gap analysis                      │
│  └── 6–8 sentence executive briefing             │
└───────────────────────┬─────────────────────────┘
                        │
                        ▼
              IntelligenceReport
        (Streamlit UI  /  API JSON)
```

---

## Project Structure

```
competitor-intel/
├── backend/
│   ├── main.py                    # FastAPI app + run_intelligence_pipeline()
│   ├── config.py                  # Pydantic settings (env vars)
│   ├── services/
│   │   ├── scraper_service.py     # Async scraper — Jina + BS4 fallback
│   │   ├── analysis_service.py    # Gemini analysis with momentum rubric
│   │   └── comparison_service.py # Cross-competitor synthesis
│   ├── models/
│   │   └── schemas.py             # Pydantic schemas (request + response)
│   └── utils/
│       ├── chunker.py             # Token-aware page merger
│       └── cleaner.py             # HTML → plain text cleaner
├── frontend/
│   └── app.py                     # Streamlit UI with progress + export
├── requirements.txt
└── .env                           # Your API keys (not committed)
```

---

## Configuration

All settings live in `config.py` and are loaded from `.env`:

| Variable | Default | Description |
|---|---|---|
| `GEMINI_API_KEY` | — | **Required.** Your Gemini API key |
| `JINA_API_KEY` | `""` | Optional. Improves scraping quality significantly |
| `DEFAULT_MODEL` | `gemini-2.0-flash` | Gemini model to use |
| `MAX_PAGES_PER_COMPETITOR` | `4` | Homepage + up to 3 sub-pages |
| `MAX_TOKENS_PER_CHUNK` | `6000` | Token budget per Gemini call |
| `REQUEST_TIMEOUT_SECONDS` | `15` | HTTP timeout per page fetch |

---

## Momentum Score Rubric

Gemini scores each competitor 1–10 using a calibrated 5-band rubric — not a "safe 7":

| Score | Meaning |
|---|---|
| **9–10** | All signals firing: major launches + broad hiring + pricing expansion + AI push + new markets |
| **7–8** | Most signals present: recent updates, moderate hiring, growth messaging, some AI |
| **5–6** | Maintaining not expanding: mature product, stable messaging, selective hiring |
| **3–4** | Few growth signals: defensive messaging, static pricing, thin content, no launches |
| **1–2** | Stagnation or decline: anti-growth messaging, no hiring, no updates, legacy positioning |

> **Calibration rules:** Large company ≠ high momentum (TCS ≠ 9). Small startup with thin content scores 3–4, not 7. When uncertain, Gemini scores lower, not higher.

---

## Test Scenarios

Try these to see differentiated momentum scores in action:

| Category | Competitors to compare |
|---|---|
| **Project management** | Linear, Notion, Basecamp |
| **AI writing** | Jasper, Copy.ai, Writesonic |
| **Indian ed-tech** | Scaler, Internshala, Unstop |
| **AI dev tools** | Cursor, Replit, GitHub Copilot |
| **CRM** | HubSpot, Zoho CRM, Freshsales |

---

## Tech Stack

| Layer | Tool | Why |
|---|---|---|
| **AI Brain** | Gemini 2.0 Flash | Fast, cheap, long context window |
| **Backend API** | FastAPI + uvicorn | Auto-generates Swagger UI, async-native |
| **HTTP client** | httpx (async) | Concurrent scraping across competitors |
| **Scraping** | Jina AI Reader + BeautifulSoup | Clean markdown first, HTML fallback |
| **Frontend** | Streamlit | Rapid UI with progress tracking |
| **Validation** | Pydantic v2 | Request/response schema enforcement |
| **Settings** | pydantic-settings | Type-safe env var loading |

---

## Known Behaviours

- **Rate limits** — Gemini free tier has per-minute quotas. The analyzer reads the `retry_delay` from 429 errors and waits exactly that long before retrying. Running 3+ competitors sequentially takes 40–90 seconds.
- **Domain resolution** — When you enter a company name (not a URL), the scraper probes `.com → .io → .co → .ai` and uses the first that responds with HTTP < 400.
- **Jina fallback** — If Jina AI fails, the scraper fetches raw HTML and cleans it with BeautifulSoup. Content quality may be slightly lower but the pipeline never silently drops pages.
- **JSON recovery** — If Gemini returns malformed JSON (e.g. unescaped backslashes), the parser attempts two recovery passes before falling back to an empty analysis.

---

## License

MIT — use it, fork it, ship it.
