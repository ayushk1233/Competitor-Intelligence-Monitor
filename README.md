# Competitor Intelligence Monitor

AI-powered competitive intelligence system built with Gemini API.
Fetches public competitor data, extracts strategic signals, and generates 
an actionable intelligence report — not summaries, signals.

## What It Does

- Accepts 2–5 competitor names or URLs
- Fetches homepage, pricing, about, blog, and careers pages per competitor
- Sends content to Gemini for structured signal extraction
- Generates cross-competitor strategic comparison
- Displays results in a clean Streamlit dashboard

## Setup (5 Minutes)

### 1. Clone and enter the project
```bash
git clone https://github.com/YOUR_USERNAME/competitor-intel.git
cd competitor-intel
```

### 2. Create a virtual environment
```bash
python -m venv venv

# Mac/Linux
source venv/bin/activate

# Windows
venv\Scripts\activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Set up your API key
```bash
cp .env.example .env
```
Open `.env` and add your `GEMINI_API_KEY` (required).  
Get one free at: https://aistudio.google.com/app/apikey

### 5. Run the app
```bash
streamlit run frontend/app.py
```

Open your browser at `http://localhost:8501`

## Test Scenarios

Try these to see the system in action:

- **CRM tools:** HubSpot, Zoho CRM, Freshsales
- **AI productivity:** Notion AI, Coda, Craft Docs  
- **No-code tools:** Bubble, Webflow, Glide

## Project Structure
```
competitor-intel/
├── backend/
│   ├── config.py                  # Environment settings
│   ├── main.py                    # FastAPI app (optional API layer)
│   ├── services/
│   │   ├── scraper_service.py     # Fetches + cleans competitor pages
│   │   ├── analysis_service.py    # Gemini API calls + prompt management
│   │   └── comparison_service.py  # Cross-competitor synthesis
│   ├── models/
│   │   └── schemas.py             # Pydantic data shapes
│   └── utils/
│       ├── chunker.py             # Token-aware text splitter
│       └── cleaner.py             # HTML cleaning pipeline
└── frontend/
    └── app.py                     # Streamlit UI
```

## Architecture

Five-stage pipeline:
1. **Input** → normalize names/URLs
2. **Scrape** → async fetch up to 5 pages per competitor
3. **Preprocess** → clean, chunk, deduplicate
4. **Analyze** → Gemini extracts strategic signals per competitor
5. **Compare** → Gemini synthesizes cross-competitor intelligence

## Tech Stack

| Layer | Tool |
|-------|------|
| AI Brain | Gemini API (gemini-2.0-flash) |
| Backend | FastAPI + Python |
| HTTP | httpx (async) |
| Scraping | Jina AI Reader + BeautifulSoup fallback |
| Frontend | Streamlit |
```

---

