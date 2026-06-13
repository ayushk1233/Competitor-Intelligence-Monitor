# Deployment Guide — Competitor Intelligence Monitor

## Architecture Overview

```
┌─────────────────────────────────────────────────┐
│                  Frontend (Next.js)             │
│                  :3000                          │
└────────────────────┬────────────────────────────┘
                     │ HTTP
┌────────────────────▼────────────────────────────┐
│               Backend (FastAPI)                 │
│               :8000                             │
└──┬──────────────────────┬───────────────────────┘
   │                      │
┌──▼──────────┐    ┌─────▼──────────┐
│ PostgreSQL  │    │   Redis        │
│ :5432       │    │   :6379        │
└─────────────┘    └────┬───────────┘
                        │
                  ┌─────▼──────────┐
                  │  Celery Worker │
                  │  + Beat        │
                  └────────────────┘
```

---

## Prerequisites

- **Docker** 24+ and **Docker Compose** v2
- **OpenRouter API key** (required) — set in `.env`
- At least **2 GB RAM** allocated to Docker

---

## Quick Start (Full Stack)

### 1. Clone & Configure

```bash
git clone <repo-url>
cd competitor-intelligence-monitor
cp .env.example .env
```

Edit `.env` and set at minimum:

```env
OPENROUTER_API_KEY=sk-or-v1-your-key-here
```

### 2. Start All Services

```bash
docker compose up -d
```

This starts:

| Service       | Container     | Port  | Status |
|---------------|---------------|-------|--------|
| PostgreSQL    | cim_postgres  | 5432  | Healthy |
| Redis         | cim_redis     | 6379  | Healthy |
| Backend       | cim_backend   | 8000  | Healthy |
| Celery Worker | cim_worker    | —     | Running |
| Celery Beat   | cim_beat      | —     | Running |
| Frontend      | cim_frontend  | 3000  | Running |
| Prometheus    | cim_prometheus| 9090  | Running |
| Grafana       | cim_grafana   | 3000  | Running |

### 3. Verify

```bash
# Backend health
curl http://localhost:8000/health

# Frontend
open http://localhost:3000

# Grafana
open http://localhost:3000  # admin / competitor_intel
```

### 4. Access the Application

1. Open `http://localhost:3000`
2. **Sign up** with email + password
3. Create a **watchlist**
4. Add **competitors**
5. Trigger a **monitoring run**
6. View **alerts** on the dashboard

---

## Environment Variables

### Required

| Variable | Description |
|---|---|
| `OPENROUTER_API_KEY` | OpenRouter API key for LLM access |

### Optional — Recommended

| Variable | Description |
|---|---|
| `JINA_API_KEY` | Jina AI API key (fallback scraper) |
| `SERPER_API_KEY` | Serper API key (web search) |

### Optional — Notifications

| Variable | Description | Default |
|---|---|---|
| `SMTP_HOST` | SMTP server host | — |
| `SMTP_PORT` | SMTP server port | — |
| `SMTP_USERNAME` | SMTP username | — |
| `SMTP_PASSWORD` | SMTP password | — |
| `SMTP_FROM_EMAIL` | From address for emails | — |
| `ADMIN_EMAIL` | Admin email for alerts | — |
| `SLACK_WEBHOOK_URL` | Slack webhook URL | — |
| `ENABLE_EMAIL_NOTIFICATIONS` | Enable email alerts | `true` |
| `ENABLE_SLACK_NOTIFICATIONS` | Enable Slack alerts | `true` |
| `ENABLE_WEBHOOK_NOTIFICATIONS` | Enable webhook alerts | `true` |

### Frontend

| Variable | Description | Default |
|---|---|---|
| `NEXT_PUBLIC_API_URL` | Backend API URL (set automatically in Docker) | `http://localhost:8000` |

---

## Manual Setup (Without Docker)

### Backend

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Start postgres + redis manually
docker compose up -d postgres redis

uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

### Celery Worker

```bash
celery -A backend.celery_app worker --loglevel=info
celery -A backend.celery_app beat --loglevel=info
```

### Frontend

```bash
cd frontend
npm install
npm run dev    # → http://localhost:3000
```

The frontend reads `NEXT_PUBLIC_API_URL` from `frontend/.env.local`:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

---

## Production Deployment

### Building Images

```bash
# Backend
docker build -t cim-backend:latest -f Dockerfile .

# Worker
docker build -t cim-worker:latest -f Dockerfile.worker .

# Frontend
docker build \
  --build-arg NEXT_PUBLIC_API_URL=https://api.yourdomain.com \
  -t cim-frontend:latest \
  ./frontend
```

### Production Checklist

- [ ] Set strong database passwords
- [ ] Disable debug mode in backend
- [ ] Configure CORS for your domain
- [ ] Use a reverse proxy (nginx / Caddy) for TLS termination
- [ ] Set up regular database backups
- [ ] Monitor with Prometheus + Grafana
- [ ] Configure log aggregation

### Kubernetes

K8s manifests are available in `k8s/`:

```bash
kubectl apply -f k8s/
```

Components:

- `backend-deployment.yaml` / `backend-service.yaml`
- `worker-deployment.yaml`
- `postgres-deployment.yaml` / `postgres-service.yaml` + PVC
- `redis-deployment.yaml` / `redis-service.yaml`
- `prometheus-*`
- `grafana-*`

> Note: Frontend K8s manifests are not included. Deploy as a standard Next.js deployment with the `cim-frontend:latest` image.

---

## Docker Compose Reference

```bash
# Start everything
docker compose up -d

# View logs
docker compose logs -f backend frontend

# Rebuild frontend after changes
docker compose up -d --build frontend

# Stop everything
docker compose down

# Stop and delete volumes (⚠️ destroys data)
docker compose down -v
```

---

## CI/CD

The CI pipeline (`.github/workflows/ci.yml`) runs:

1. `pytest tests -q` — unit tests
2. `python scripts/eval_gate.py` — evaluation gate

For production, extend with:

```yaml
- name: Build Docker images
  run: |
    docker build -t cim-frontend:${{ github.sha }} ./frontend
    docker push ...
```

---

## Troubleshooting

| Problem | Solution |
|---|---|
| Frontend can't reach backend | Check `NEXT_PUBLIC_API_URL` matches backend address |
| `docker compose` fails on ARM Mac | All images support `linux/amd64`; no action needed |
| Celery tasks not running | Verify `cim_redis` is healthy; check worker logs |
| Database connection refused | Wait for `cim_postgres` healthcheck to pass |
| 401 on every page | Token expired; log out and log back in |

---

## Monitoring

| Tool    | URL                        | Credentials              |
|---------|----------------------------|--------------------------|
| Grafana | http://localhost:3000       | admin / competitor_intel |
| Prometheus | http://localhost:9090    | —                        |

Grafana dashboards contain:

- Backend request rate / latency / errors
- Celery task queue depth
- Database connection pool
- System resource usage
