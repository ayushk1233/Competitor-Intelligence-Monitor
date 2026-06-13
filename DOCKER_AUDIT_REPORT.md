# Docker Audit Report

Generated: 2026-06-10

## Summary

8/8 containers healthy. Full stack operational.

| Container       | Status   | Port    | Notes                             |
|-----------------|----------|---------|-----------------------------------|
| cim_postgres    | healthy  | 5432    | PostgreSQL 16                     |
| cim_redis       | healthy  | 6379    | Redis 7                           |
| cim_backend     | healthy  | 8000    | FastAPI + uvicorn                 |
| cim_worker      | healthy  | —       | Celery worker                     |
| cim_beat        | healthy  | —       | Celery beat (300s schedule)       |
| cim_frontend    | healthy  | 3000    | Next.js 16 standalone             |
| cim_prometheus  | running  | 9090    | Prometheus + scrape config        |
| cim_grafana     | running  | **3001** | Grafana (moved off 3000)          |

## Issues Found & Fixed

### 1. Port 3000 Conflict: Frontend ↔ Grafana (CRITICAL)

**Problem:** Both `frontend` and `grafana` services mapped host port `3000:3000`. Whichever started second would fail with `port already allocated`. This is a hard blocker — the stack cannot boot with both services.

**Fix:** Changed Grafana host port to `3001:3000` in `docker-compose.yml:247`.

### 2. `.env` Contains Non-Config Garbage (MINOR)

**Problem:** Lines 41–46 of `.env` contained two stale JWT tokens and a bare UUID, likely artifacts from copy-pasting into the terminal. These are not referenced by any application config but pollute the environment.

**Fix:** Removed all three extraneous lines.

### 3. Frontend Healthcheck Fails on IPv6 Localhost (BUG)

**Problem:** The `HEALTHCHECK` in `frontend/Dockerfile:41` used `http://localhost:3000/`. Alpine's `wget` resolves `localhost` to `[::1]` (IPv6), but the Next.js server binds to `0.0.0.0:3000` (IPv4). This caused the healthcheck to always fail with `Connection refused`.

**Fix:** Changed `localhost` → `127.0.0.1` to force IPv4.

### 4. Local Redis Contention (ENVIRONMENT)

**Problem:** A local Redis instance was running on the host at PID 19449, occupying port 6379. Docker container also maps 6379, causing host-level port conflict.

**Fix:** Killed local Redis with `kill -9 19449`. Consider removing `ports` mapping from the `redis` service in `docker-compose.yml` if external access is not needed (backend connects via Docker network, not host).

## Verifications

- `docker compose build` passes for all 4 custom images (backend, frontend, worker, beat)
- `npm run build` passes with zero TypeScript errors
- Frontend HTTP healthcheck returns 200 at `/`
- Grafana accessible on `http://localhost:3001` (admin / competitor_intel)
- All services start with `docker compose up -d` and stabilize within 40s

## Recommendations

| Priority | Issue | Action |
|----------|-------|--------|
| Low | Redis port mapping | Remove `ports: "6379:6379"` from `redis` service — only backend needs it via Docker network |
| Low | Grafana/Prometheus healthcheck | Add healthchecks to grafana & prometheus services for consistency |
| Low | JWT_SECRET_KEY | Add `JWT_SECRET_KEY` to docker-compose `backend.environment` instead of relying on the default `"CHANGE_THIS_IN_PRODUCTION"` in config |
| Info | Celery worker/beat `FromAsCasing` warning | Fix casing `AS` → `as` in `Dockerfile.worker` line 2 — cosmetic, no functional impact |
