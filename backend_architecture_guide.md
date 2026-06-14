# Backend Architecture & Data Flow Guide

## 1. Backend Guideline & Data Flow Overview
The Competitor Intelligence Monitor (CIM) backend is designed using **FastAPI** for high-performance HTTP endpoints, **Celery** for asynchronous background task orchestration, and **PostgreSQL** (via `SQLAlchemy` AsyncSession) for persistent data storage.

### High-Level Data Flow:
1. **User Request**: The Next.js frontend sends an HTTP request to FastAPI.
2. **Synchronous Handling**: If the request is a simple CRUD operation (e.g., getting a watchlist, updating a setting), FastAPI handles it synchronously via the `DatabaseService` and returns the data.
3. **Asynchronous Handling**: For heavy operations (like running an intelligence report), FastAPI creates a "queued" database record, pushes a job to **Redis**, and immediately returns a job ID to the frontend.
4. **Celery Worker Execution**: A background worker picks up the job, performs heavy scraping and LLM inferences, and updates the database record statuses (`scraping` -> `analyzing` -> `comparing` -> `completed`).
5. **Client Polling**: The frontend polls the job ID status and ultimately fetches the final generated report when it is marked as `completed`.

---

## 2. API Utilization Analysis

Here is the breakdown of all FastAPI endpoints, separated by those actively called by the Next.js frontend and those that are currently "orphaned" (present in backend but unused).

### ✅ APIs Used by the Frontend
These endpoints are actively called by `frontend/src/services/*.ts`:

**Authentication** (`auth.service.ts`)
* `POST /api/auth/signup`
* `POST /api/auth/login`
* `GET /api/auth/me`

**Dashboard** (`dashboard.service.ts`)
* `GET /api/dashboard/summary`
* `GET /api/dashboard/recent-runs`
* `GET /api/dashboard/recent-alerts`
* `GET /api/dashboard/activity`
* `GET /api/dashboard/competitors`

**Watchlists & Competitors** (`watchlist.service.ts`, `competitor.service.ts`)
* `GET /api/watchlists`
* `POST /api/watchlists`
* `GET /api/watchlists/{id}`
* `DELETE /api/watchlists/{id}`
* `GET /api/watchlists/{watchlistId}/competitors`
* `POST /api/watchlists/{watchlistId}/competitors`
* `GET /api/watchlists/{watchlistId}/runs`
* `DELETE /api/watchlists/{watchlistId}/runs/{runId}`

**Analysis & Reports** (`analysis.service.ts`, `reports/[runId]/page.tsx`)
* `POST /api/analyze` *(Triggers manual run)*
* `GET /api/status/{run_id}` *(Polling)*
* `GET /api/report/{run_id}` *(Fetches final payload)*
* `GET /api/runs`
* `DELETE /api/runs/{run_id}`

**Competitor Detail** (`competitor-detail.service.ts`)
* `GET /api/competitors/{competitor_name}/latest`
* `GET /api/competitors/{competitor_name}/history`
* `GET /api/competitors/{competitor_name}/drift`

**Alerts & Notifications** (`notification.service.ts`, `ChannelCard.tsx`, `alerts/page.tsx`)
* `GET /api/alerts`
* `GET /api/notifications/channels`
* `POST /api/notifications/channels`
* `PUT /api/notifications/channels/{id}`
* `DELETE /api/notifications/channels/{id}`
* `GET /api/notification-events`

---

### ❌ APIs Present in Backend but NOT Used by Frontend
These endpoints are fully implemented in the backend router but are currently untouched by the client UI. These represent "upcoming" features or backend capabilities waiting for frontend implementation:

**Granular Alert Management**
* `GET /api/alerts/latest`
* `GET /api/alerts/{company_name}`
* `GET /api/alerts/counts`
* `GET /api/alerts/detail/{alert_id}`
* `POST /api/alerts/{alert_id}/acknowledge`
* `POST /api/alerts/{alert_id}/resolve`
* `POST /api/suppress/{company_name}/{severity}` *(Allows suppressing alerts for a specific company)*

**Legacy/Duplicate Endpoints**
* `GET /api/history/{competitor_name}` *(Redundant, replaced by `/api/competitors/{name}/history`)*

**DevOps & Observability**
* `GET /health` *(Used by Docker/Kubernetes probes)*
* `GET /metrics` *(Scraped by Prometheus)*
* `GET /metrics-raw`

---

## 3. How the Final Intel Report is Generated

The Final Intel Report is not generated synchronously. It is produced by a Celery background task (`run_analysis_task`).

### Breakdown of the Pipeline

#### Step 1: Orchestration (`backend/tasks.py`)
* **Function**: `run_analysis_task(run_id, competitors)`
* **Role**: This is the master conductor. It manages the database state, handles error catching, updates the run `status`, and coordinates the three distinct services below.

#### Step 2: Scraping (`backend/services/scraper_service.py`)
* **Class**: `ScraperService`
* **Method**: `fetch_competitor(company_name)`
* **Action**: It attempts to fetch target pages (homepage, about us, news, pricing) using `BeautifulSoup`. If the page relies heavily on JavaScript, it falls back to using the `Jina AI` scraping API.
* **Output**: A collection of raw HTML/text strings.
* **Database Action**: Saved to `page_snapshots` table.

#### Step 3: Analysis (`backend/services/analysis_service.py`)
* **Class**: `AnalysisService`
* **Method**: `analyze_competitor(pages)`
* **Action**: Takes the raw text gathered by the scraper and sends it to an LLM (specifically `deepseek/deepseek-chat` via OpenRouter). The LLM is given a strict JSON schema prompt to extract standardized metrics (momentum score, pricing changes, messaging focus).
* **Output**: A structured Pydantic model (`CompetitorAnalysis`) for *each* individual competitor.
* **Database Action**: Saved to `competitor_analyses` table.

#### Step 4: Comparison & Synthesis (`backend/services/comparison_service.py`)
* **Class**: `ComparisonService`
* **Method**: `generate_report(analyses)`
* **Action**: Gathers the individual analyses from Step 3 and passes them to a high-tier LLM (`google/gemini-2.5-flash`). This LLM acts as an executive strategist, synthesizing the data to determine the "Market Leader", "Fastest Mover", and identifying strategic gaps or messaging overlaps between the competitors.
* **Output**: A structured `ComparisonResult` containing the executive briefing and positioning map.
* **Database Action**: Saved to `comparison_results` table. The overall `Run` status is updated to `completed`.

#### Step 5: Retrieval (`backend/main.py`)
* **Endpoint**: `GET /api/report/{run_id}`
* **Action**: Once the frontend sees the run is `completed`, it hits this endpoint. The endpoint uses `DatabaseService` to query the `competitor_analyses` and `comparison_results` tables, reconstituting the data into the final `IntelligenceReport` Pydantic schema (`backend/models/schemas.py`), and serves it to the frontend for rendering.

---

## 4. Unstructured Data Framing & Structuring
The transformation of chaotic, raw scraped text into the structured JSON used by the frontend relies on a specific set of files and multi-agent reasoning modules. 

Here is the exact code path responsible for this framing:

### 1. Initial Signal Extraction
* **File:** `backend/services/analysis_service.py` (`analyze_competitor`)
* **Action:** Before hitting the main LLM, the raw text is passed through `extract_signals()` and `compress_signals()` (located in `backend/retrieval/`). This acts as an initial filter to find hard evidence of new features, pricing, and growth without hallucinations.

### 2. Multi-Agent Orchestration
* **File:** `backend/reasoning/orchestrator.py` (`run_intelligence_pipeline`)
* **Action:** Instead of dumping all raw text into one prompt, the text is routed (`route_evidence()`) into specialized chunks. Three separate sub-agents run concurrently:
  * `analyze_momentum()` (`backend/reasoning/momentum_reasoner.py`): Exclusively looks at "launch" and "hiring" signals.
  * `analyze_tone()` (`backend/reasoning/tone_reasoner.py`): Looks at how the company speaks (Enterprise vs Startup).
  * `analyze_icp()` (`backend/reasoning/icp_reasoner.py`): Determines the Ideal Customer Profile.
* **Synthesis:** The outputs of these three focused agents are then passed into `synthesize_intelligence()`, which formulates the final analysis.

### 3. Strict JSON Enforcement & Schema Validation
* **File:** `backend/services/analysis_service.py` (`_parse_response`)
* **Action:** The final LLM output is intercepted here. It enforces the rules defined in `backend/models/schemas.py` (specifically the `CompetitorAnalysis` Pydantic model). 
* **Fallback Recovery:** If the LLM generates slightly malformed JSON, a regex-based fallback parser strips out markdown formatting or weird control characters, ensuring the frontend never receives a broken payload.
