# Frontend Environment Audit

## Root Cause

`NEXT_PUBLIC_API_URL=http://backend:8000` was passed as a **Docker build arg** in `docker-compose.yml:75`. During `npm run build`, Next.js inlines all `NEXT_PUBLIC_*` environment variables directly into the JS bundle. Since actual process environment vars have highest priority, the build arg overrode `.env.local` (`http://localhost:8000`).

The running Docker container shipped a bundle with `http://backend:8000` hardcoded. From the browser (which runs on the host machine), `backend` is not a resolvable hostname — the browser needs `http://localhost:8000`.

## Nexth auth priority (short version)
Actual process env (Docker build arg) > `.env.local` > `.env.production` > `.env`

Since the Docker build arg set `NEXT_PUBLIC_API_URL=http://backend:8000`, the correct value in `.env.local` was ignored during the build.

## Files inspected

| File | Contents | Role |
|------|----------|------|
| `frontend/.env.local` | `NEXT_PUBLIC_API_URL=http://localhost:8000` | Local dev ✅ |
| `frontend/.env.production` | does not exist | Fallback not triggered |
| `frontend/.env` | does not exist | Fallback not triggered |
| `frontend/src/lib/api-client.ts` | `baseURL: process.env.NEXT_PUBLIC_API_URL \|\| "http://localhost:8000"` | Runtime fallback |
| `frontend/next.config.ts` | `output: "standalone"` | No env override |
| `docker-compose.yml` | build arg: `NEXT_PUBLIC_API_URL: http://backend:8000` | **The bug** |

## Proof

Before fix — Docker production bundle:
```
$ docker compose exec frontend grep -o 'http[^"]*8000' /app/.next/static/chunks/384wrgcnyvm9a.js
http://backend:8000
```

After fix — Docker production bundle:
```
$ docker compose exec frontend grep -o 'http[^"]*8000' /app/.next/static/chunks/0ntj2-3iu24d9.js
http://localhost:8000
```

Local build (loaded `.env.local`):
```
$ rg -o 'http[^"]*8000' frontend/.next/static/chunks/
http://localhost:8000
```

## Files changed

**`docker-compose.yml:75,80`** — Changed `NEXT_PUBLIC_API_URL` from `http://backend:8000` to `http://localhost:8000` in both `build.args` and `environment`.

## Final API URL used by browser

```
http://localhost:8000
```

All environments (local dev, Docker, local production build).

## Verification steps

1. **Search frontend for `backend:8000`** — zero results in source files:
   ```bash
   grep -rn "backend:8000" frontend/   # no output
   ```

2. **Check Docker production bundle**:
   ```bash
   docker compose exec frontend sh -c \
     'grep -o "http[^\"]*8000" /app/.next/static/chunks/*.js | sort -u'
   # http://localhost:8000
   ```

3. **Check browser-served chunk**:
   ```bash
   curl -s http://localhost:3000/_next/static/chunks/0ntj2-3iu24d9.js \
     | rg -o 'http[^"]*8000'
   # http://localhost:8000
   ```

4. **Check local build**:
   ```bash
   rg -o 'http[^"]*8000' frontend/.next/static/chunks/
   # http://localhost:8000
   ```

5. **Browser DevTools** — open `http://localhost:3000`, go to Network tab, submit signup form. Requests should go to `http://localhost:8000/api/auth/signup`.

## Env file priority reference

Next.js `NEXT_PUBLIC_*` priority (highest → lowest):
1. Actual `process.env` (Docker build arg, CI env, shell export)
2. `.env.local`
3. `.env.[NODE_ENV]` (e.g. `.env.production`)
4. `.env`
