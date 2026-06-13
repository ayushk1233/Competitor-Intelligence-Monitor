# AGENTS.md — Competitor Intelligence Monitor (CIM)

## Quick start
- `pip install -r requirements.txt && pip install -r requirements-dev.txt`
- Copy `.env.example` → `.env`; set `OPENROUTER_API_KEY` (required), `JINA_API_KEY` / `SERPER_API_KEY` (optional)
- `docker compose up -d` — starts postgres, redis, prometheus, grafana
- `uvicorn backend.main:app --reload` — FastAPI on :8000
- `streamlit run frontend/app.py` — UI on :8501, calls backend at localhost:8000
- `python -m pytest tests -q` — unit tests (DB mocked, no postgres needed)
- `python scripts/eval_gate.py` — eval gate compares vs `evaluation_baselines/` (3% tolerance)

## Lint & format
- `ruff check .` (select E/F/I), `black .` (line-length 100, target py311)
- Config in `pyproject.toml`

## Architecture
- **FastAPI** entry: `backend.main:app`. Auto-creates DB tables on startup via `create_tables()`
- **Celery** app: `backend.celery_app` (broker/backend = Redis). Tasks live in `backend.tasks`
- **Celery Beat** runs `scheduled_monitoring` every 300s (config in `celery_app.py:40`)
- **Async SQLAlchemy** + asyncpg. Each Celery task creates a fresh engine + event loop via `_make_session_factory()` (`tasks.py:33`) to avoid asyncpg cross-loop conflicts
- **LLM**: OpenRouter via OpenAI SDK (`base_url` override). Models: `deepseek/deepseek-chat` (analysis), `google/gemini-2.5-flash` (comparison), `anthropic/claude-3-haiku` (fallback). Prompts in `backend/prompts/`
- **Scraping**: BeautifulSoup for static pages, Jina AI as fallback. Target paths in `backend/services/scraper_service.py`
- **Frontend**: Single-page Streamlit app (`frontend/app.py`). No framework — uses `requests` directly

## Celery (docker-compose already configured)
- Worker: `celery -A backend.celery_app worker --loglevel=info`
- Beat: `celery -A backend.celery_app beat --loglevel=info`

## DB migrations
- Alembic configured in `alembic.ini` (script_location = alembic)
- Tables also auto-created at FastAPI startup — migrations may be out of sync

## Monitoring
- Prometheus `/metrics` (auto-instrumented). Custom metrics in `backend/metrics.py`
- Grafana at localhost:3000 (admin / competitor_intel). Dashboards in `monitoring/grafana/`

## Tailwind v4 quirks
- **JIT does NOT detect** arbitrary color values (`border-[#000]`, `text-[#123456]`) inside template literals (dynamic `className`). Always use inline `style` prop for dynamic colors: `style={theme !== "dark" ? { borderColor: "#000" } : undefined}`.
- This applies to ALL `#`-prefixed arbitrary values in dynamic className strings, not just border colors.

## CI (`.github/workflows/ci.yml`)
- On push to main/develop/feature/* and PRs: `pytest tests -q` → `python scripts/eval_gate.py`

## Testing quirks
- All tests mock `DatabaseService` — no database needed
- `pytest.ini` sets `asyncio_default_fixture_loop_scope=function`
- `backend/__init__.py` and all sub-package `__init__.py` files are empty and gitignored (see `.gitignore`)

## K8s
- Manifests in `k8s/` for backend, worker, postgres, redis, prometheus, grafana
