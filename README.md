# Competitor Intelligence Monitor (CIM)

**Competitor Intelligence Monitor (CIM)** is an automated, AI-driven platform for tracking, analyzing, and synthesizing competitor behavior across the web.

---

## 📸 Application Screenshots

### 1. Sign In
<p float="left">
  <img src="images/signin_dark.png" width="49%" />
  <img src="images/signin_light.png" width="49%" />
</p>

### 2. Dashboard
<p float="left">
  <img src="images/dark_dashbaord.png" width="49%" />
  <img src="images/light_dashboard.png" width="49%" />
</p>

### 3. Dashboard Details
<img src="images/light_dashbaord2.png" width="100%" />

### 4. Run Analysis & Progress
<p float="left">
  <img src="images/run_analysis.png" width="49%" />
  <img src="images/analysis_progress.png" width="49%" />
</p>

### 5. Run History
<img src="images/run_history.png" width="100%" />

### 6. Watchlists & Competitors
<p float="left">
  <img src="images/watchlist.png" width="49%" />
  <img src="images/watchlist_comp.png" width="49%" />
</p>

### 7. Alerts
<img src="images/alerts.png" width="100%" />

### 8. Intelligence Reports
<img src="images/intel_report1.png" width="100%" />
<img src="images/intel_report2.png" width="100%" />
<img src="images/intel_report3.png" width="100%" />
<img src="images/intel_report4.png" width="100%" />
<img src="images/intel_report5.png" width="100%" />

### 9. Upcoming Features
*Features in development (v1.3+)*

**Trends**
<img src="images/trends.png" width="100%" />

**Battlecards**
<img src="images/battlecards.png" width="100%" />

**Intelligence Search**
<img src="images/intel_search.png" width="100%" />

---

## 🏃 Quick Start / Run Locally

This project is fully dockerized. To spin up the entire application on your machine, follow these steps:

**1. Clone the repository**
```bash
git clone https://github.com/your-username/competitor-intelligence-monitor.git
cd competitor-intelligence-monitor
```

**2. Configure Environment Variables**
Copy the example environment file and fill in your API keys:
```bash
cp backend/.env.example backend/.env
```
Open `backend/.env` and add:
* `OPENROUTER_API_KEY`: (Required) For the LLM synthesis pipeline.
* `JINA_API_KEY`: (Optional) For advanced JS scraping.
* `SERPER_API_KEY`: (Optional) For search engine queries.

**3. Build and Start the Application**
Start all services (Frontend, Backend, Postgres, Redis, Celery Workers) using Docker Compose:
```bash
docker compose up -d --build
```

**4. Access the App**
* **Frontend UI**: Open your browser to [http://localhost:3000](http://localhost:3000)
* **Backend API Docs**: Open your browser to [http://localhost:8000/docs](http://localhost:8000/docs)

*Note: The FastAPI backend automatically creates the database tables upon startup. Celery and Celery Beat run automatically as separate containers to handle background tasks.*

---

## 🧠 Application & Data Flow

This document outlines the complete user journey and data architecture for the Competitor Intelligence Monitor, starting from initial user onboarding through the core intelligence scraping and alerting pipelines.

### 1. User Onboarding & Authentication
The application secures user sessions using JSON Web Tokens (JWT).

**Flow:**
* **Signup/Login** (`POST /api/auth/signup` / `POST /api/auth/login`)
  * The Next.js frontend sends credentials to the FastAPI backend.
  * The backend `DatabaseService` verifies or creates the user in the `users` table.
  * Passwords are hashed using bcrypt (`hash_password`).
  * A JWT access token is generated via `create_access_token` and returned to the client.
* **Session Persistence**
  * The frontend stores the token and attaches it as a Bearer token in the `Authorization` header for all subsequent API requests.
  * The `get_current_user` FastAPI dependency validates the token and attaches the `User` object to the request context.

### 2. Dashboard & Watchlist Management
Once authenticated, users land on the Dashboard where they manage the companies they want to monitor.

**Flow:**
* **Fetching Watchlists** (`GET /api/watchlists`)
  * Retrieves the user's watchlists and their associated competitors from the `watchlists` and `watchlist_competitors` tables.
* **Adding Competitors**
  * Users add a company to their watchlist. The backend resolves the company domain (if not provided) and saves it to `WatchlistCompetitor`.
* **Configuration**
  * Users configure the `monitoring_frequency` (e.g., DAILY, WEEKLY) and notification channels (e.g., Email, Slack). This sets the `next_run_at` timestamp on the `Watchlist` table.

### 3. The Core Intelligence Pipeline (Data Flow)
This is the heart of the application. It can be triggered manually (Ad-hoc Analysis) or automatically via a schedule (Monitoring).

#### A. Initiation
* **Manual Trigger** (`POST /api/analyze`)
  * The frontend sends a list of competitors.
  * The backend creates a `Run` record in the database with status `queued`.
  * The backend enqueues a Celery background task (`run_analysis_task`) via Redis and immediately returns a `run_id` to the frontend.
  * **Frontend Polling**: The frontend begins polling `GET /api/status/{run_id}` to update the user on pipeline progress (Queued -> Scraping -> Analyzing -> Comparing -> Completed).
* **Scheduled Trigger** (`scheduled_monitoring_task`)
  * Celery Beat wakes up every 5 minutes.
  * It queries the database for Watchlists where `next_run_at <= NOW()`.
  * For each due watchlist, it creates a `MonitoringRun` and enqueues `monitor_watchlist_task`.

#### B. Execution (Celery Workers)
The pipeline is executed inside the Celery worker, which spins up an isolated SQLAlchemy `AsyncSession` to prevent event-loop conflicts. The pipeline runs in three distinct stages:

* **Stage 1: Scraping** (`ScraperService`)
  * The worker iterates through the list of competitors.
  * It uses BeautifulSoup (for static content) and Jina AI (for JS-heavy content) to scrape target pages (homepage, about, news, careers).
  * **Data Persistence**: The raw HTML/Text content is saved to the `page_snapshots` table. This raw text acts as a historical baseline for future drift detection.
* **Stage 2: Analyzing** (`AnalysisService`)
  * The raw scraped text for each competitor is sent to the primary LLM (OpenRouter: `deepseek/deepseek-chat`).
  * The LLM extracts structured intelligence: Momentum score, messaging tone, key product changes, and pricing updates.
  * **Data Persistence**: The structured JSON response and computed metrics are saved to the `competitor_analyses` table (linked to the Run).
* **Stage 3: Comparing** (`ComparisonService`)
  * Once all competitors are analyzed, their structured profiles are bundled together and sent to a synthesis LLM (`google/gemini-2.5-flash`).
  * The LLM acts as an executive strategist, determining the "Market Leader", "Fastest Mover", and generating an "Executive Briefing" identifying messaging gaps.
  * **Data Persistence**: The synthesis is saved to the `comparison_results` table.
  * The Run status is updated to `completed`.
  * For manual runs, the frontend stops polling and fetches the final JSON from `GET /api/report/{run_id}`.

### 4. Drift Detection & Alerting
For scheduled monitoring runs, an additional stage occurs after the intelligence pipeline completes.

**Flow:**
* **Detecting Drift** (`MonitoringService.detect_drift`)
  * The backend compares the just-completed analysis (newest) with the previous analysis (previous) from the database.
  * It runs an LLM diff to identify significant changes (e.g., "Competitor A dropped their pricing by 20%").
* **Alert Generation**
  * If drift is detected, a record is created in the `alert_history` table with a severity level (LOW, MEDIUM, HIGH) and a generated headline.
* **Notification Dispatch**
  * The system checks the `notification_channels` linked to the user's Watchlist.
  * A `NotificationEvent` is created and the alert is dispatched to the configured destinations (e.g., via Email or Webhook).
* **Alert Management**
  * On the frontend, users can view alerts (`GET /api/alerts`), acknowledge them (`POST /api/alerts/{id}/acknowledge`), resolve them, or globally suppress specific alert types for a period of time (`POST /api/suppress/...`).

### 5. High-Level Data Model Map
Here is how the data connects in PostgreSQL:
* **users**: The core entity.
* **watchlists**: Owned by users. Dictates monitoring schedules.
* **watchlist_competitors**: The companies attached to a watchlist.
* **runs**: Represents a single execution of the intelligence pipeline. Can be tied to a user (manual) or a watchlist.
* **page_snapshots**: (Child of runs) The raw scraped data from the internet.
* **competitor_analyses**: (Child of runs) The structured, LLM-extracted intelligence for a single company.
* **comparison_results**: (Child of runs) The 1-to-1 synthesis report for the whole run.
* **monitoring_runs**: Represents the scheduled execution wrapper around a run.
* **alert_history**: Alerts generated by the drift detection service.

---

## 🛠 Setup & Notification Configuration

### Option A — Email Alerts (Gmail SMTP)

**Step 1: Enable 2-Factor Authentication**
1. Go to: Google Account Security
2. Enable: 2-Step Verification

**Step 2: Create App Password**
1. Go to: Google App Passwords
2. Select App: `Mail`
3. Device: `Other (Custom Name)`
4. Name: `CIM`
5. Google generates a 16-letter password (e.g., `abcd efgh ijkl mnop`). This is your SMTP password.

**Step 3: Configure Environment Variables**
Add the following to your backend `.env` file:
```env
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587

SMTP_USERNAME=your_email@gmail.com
SMTP_PASSWORD=generated_app_password

EMAIL_FROM=your_email@gmail.com
```

**Step 4: Restart Services**
FastAPI and Celery will automatically pick up the SMTP configurations on restart. 
* Note: Gmail requires Port 587 and TLS enabled (configured by default).

### Option B — Slack Webhook Alerts

**Step 1: Create Slack Workspace**
1. Go to Slack and create or log in to a workspace.

**Step 2: Create Incoming Webhook App**
1. Go to: Slack API Apps
2. Click **Create New App** > **From Scratch**
3. Name it (e.g., "CIM Alerts") and select your workspace.

**Step 3: Enable Incoming Webhooks**
1. Inside app settings, go to **Incoming Webhooks**.
2. Toggle to **Activate Incoming Webhooks**.

**Step 4: Add Webhook**
1. Click **Add New Webhook to Workspace**.
2. Choose the channel to post alerts to (e.g., `#competitive-intel` or `#alerts`).
3. Slack will generate a URL: `https://hooks.slack.com/services/...`

**Step 5: Store in Environment**
Add the following to your backend `.env` file:
```env
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/xxxxx
```

**Step 6: Test**
Send a test payload to ensure the connection works:
```json
{
  "text": "CIM Alert Test"
}
```

---

## 🚀 Future Roadmap

**v1.3**
* RAG
* Vector Databases
* Semantic Search
* Long-Term Memory

**v2.0**
* Recommendation Systems
* Threat Assessment
* Opportunity Discovery

**v3.0**
* Multi-Agent Systems
* LangGraph
* Agent Orchestration
* Autonomous Workflows

**v4.0**
* Production SaaS AI Platform
* Multi-Tenant Architecture
* Enterprise AI Infrastructure
