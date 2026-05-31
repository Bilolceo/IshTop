# IshTop — Production Deployment Guide

Authoritative deployment runbook for Railway (primary) and Render (fallback).
Pair this document with [SECURITY.md](../SECURITY.md) and run
`bash scripts/check-env-safety.sh` before any push.

## Architecture at a glance

```
┌─────────────────┐    ┌─────────────────┐    ┌──────────────┐
│  Next.js 14     │───▶│  FastAPI         │───▶│  PostgreSQL  │
│  standalone     │    │  + gunicorn      │    └──────────────┘
│  (frontend)     │    │  + cookie auth   │           │
└─────────────────┘    └─────────────────┘    ┌──────────────┐
        ▲                       │              │  Redis       │
        │                       └─────────────▶│  (blacklist  │
        │  https only           │              │   + rate)    │
        └───────────────────────┘              └──────────────┘
```

Required services in production:

| Service | Purpose | Required |
|---|---|---|
| Frontend (Next.js standalone) | UI | yes |
| Backend (FastAPI / gunicorn) | API + cookie auth | yes |
| PostgreSQL | Application DB | yes |
| Redis | JWT blacklist + rate limiter cross-instance state | yes |
| Object storage (optional) | Uploads beyond `/uploads` ephemeral | recommended |

## A. Railway deployment (primary)

### A.1 One-time setup

1. Create a new Railway project for IshTop.
2. Provision **PostgreSQL** plugin → copy `${{ Postgres.DATABASE_URL }}` reference.
3. Provision **Redis** plugin → copy `${{ Redis.REDIS_URL }}` reference.
4. Create two Railway services from this repo:
   - **backend** — root `backend/`, Dockerfile build, port `8000`.
     Already configured via [backend/railway.json](../backend/railway.json):
     - `startCommand`: runs `alembic upgrade head` then gunicorn
     - `healthcheckPath: /health` (timeout 30s)
   - **frontend** — root `frontend/`, Dockerfile build, port `3000`.
     Configured via [frontend/railway.json](../frontend/railway.json).
5. In each service → **Settings → Networking** → enable a public domain.

### A.2 Backend environment variables (Railway → Variables)

| Variable | Value | Notes |
|---|---|---|
| `DEBUG` | `false` | enforces production validator |
| `SECRET_KEY` | 32+ char random — generate with `python -c "import secrets; print(secrets.token_hex(32))"` | rotates JWTs |
| `AUTH_COOKIE_SECURE` | `true` | also auto-forced when DEBUG=false |
| `AUTH_COOKIE_HTTPONLY` | `true` | default |
| `AUTH_COOKIE_SAMESITE` | `lax` | works for OAuth redirects |
| `AUTH_COOKIE_PATH` | `/` | default |
| `AUTH_COOKIE_DOMAIN` | `.ishtop.uz` if FE & BE share root domain; else leave blank for host-only cookies on `up.railway.app` | see §C |
| `RATE_LIMIT_ENABLED` | `true` | required by validator |
| `RATE_LIMIT_USE_REDIS` | `true` | required for multi-replica |
| `REDIS_ENABLED` | `true` | required by validator |
| `REDIS_URL` | `${{ Redis.REDIS_URL }}` | Railway service reference |
| `TOKEN_BLACKLIST_USE_REDIS` | `true` | logout token revocation |
| `DATABASE_URL` | `${{ Postgres.DATABASE_URL }}` | Railway service reference |
| `CORS_ORIGINS` | exact comma-separated frontend URLs, e.g. `https://ishtop.uz,https://www.ishtop.uz` or `https://<frontend>.up.railway.app` | **no wildcards** |
| `FRONTEND_URL` | exact frontend URL (used in emails + OG) | |
| `AI_PROVIDER` | `gemini` | or `openai` |
| `GEMINI_API_KEY` | production key — rotate from any local `.env` value | |
| `GEMINI_MODEL` | `gemini-2.5-flash` | |
| `OAUTH_ENABLED` | `true` if Google login used | |
| `GOOGLE_CLIENT_ID` | from Google Cloud | |
| `GOOGLE_CLIENT_SECRET` | **rotated** production secret | |
| `GOOGLE_REDIRECT_URI` | `https://<backend>/api/v1/auth/callback/google` | |
| `SUPPORT_EMAIL` | `support@ishtop.uz` | |
| `EMAIL_TRANSPORT` | `sendgrid` or `smtp` (default `disabled`) | |
| `SENDGRID_API_KEY` | provider key | optional |

### A.3 Frontend environment variables (Railway → Variables)

| Variable | Value |
|---|---|
| `NEXT_PUBLIC_API_URL` | `https://<backend>.up.railway.app/api/v1` |
| `NEXT_PUBLIC_FRONTEND_URL` | `https://<frontend>.up.railway.app` |
| `NEXT_PUBLIC_VAPID_PUBLIC_KEY` | optional, leave blank to disable push |

> Note — `NEXT_PUBLIC_*` are baked into the JS bundle at `next build`. Changing
> them later requires a redeploy. The frontend Dockerfile accepts these via
> `ARG` so Railway passes them as build args automatically.

### A.4 Deploy order

1. **Provision DB + Redis** first.
2. Set **backend env vars** (incl. DB + Redis references).
3. Deploy backend → wait for `/health` to return 200.
   Migrations run automatically as part of `startCommand`.
4. Note the backend public URL → set `NEXT_PUBLIC_API_URL` on frontend.
5. Set backend `CORS_ORIGINS` to the frontend URL.
6. Deploy frontend.

## B. Render deployment (fallback)

The repo ships [render.yaml](../render.yaml) — a single-file blueprint that
provisions backend, frontend, and PostgreSQL. Redis must be added manually:

1. Create a **Render Redis** instance, copy `REDIS_URL`.
2. From dashboard, paste it into `ishtop-backend` env vars + set
   `REDIS_ENABLED=true`.
3. Click **New → Blueprint** → connect repo → Render reads `render.yaml` and
   creates the services. `SECRET_KEY` is auto-generated by Render.
4. Fill any `sync: false` vars in the dashboard (Gemini key, Google OAuth,
   `NEXT_PUBLIC_API_URL`, `NEXT_PUBLIC_FRONTEND_URL`, Stripe, SMTP).
5. Set backend env `DEBUG=false` (default), `RATE_LIMIT_ENABLED=true` (default
   in render.yaml), `AUTH_COOKIE_SECURE` will be auto-forced.

## C. Cookie domain & CORS — pick the right combo

The auth flow uses httpOnly cookies, so frontend and backend must share a
cookie scope or use the same browsing context.

### Option 1 — Same root domain (recommended for production)

```
frontend: https://ishtop.uz
backend:  https://api.ishtop.uz
```

- `AUTH_COOKIE_DOMAIN=.ishtop.uz`
- `CORS_ORIGINS=https://ishtop.uz,https://www.ishtop.uz`
- Browser sends cookie on cross-origin XHR because cookie domain matches.
- Best UX, no SameSite=None needed.

### Option 2 — Different Railway/Render subdomains

```
frontend: https://ishtop-frontend.up.railway.app
backend:  https://ishtop-backend.up.railway.app
```

- `AUTH_COOKIE_DOMAIN=` (leave blank — host-only cookies)
- Cookies are set on the backend host; cross-origin XHR from the frontend
  must use `credentials: "include"` (already done in axios).
- This works but requires `SameSite=Lax` and `Secure=true` (already enforced).
- **Limitation:** if browsers ever drop third-party cookies for top-level
  navigations between these subdomains, OAuth callback flow breaks. For
  customer demos this works; for a long-running product, configure Option 1.

## D. Google OAuth — production checklist

1. Google Cloud Console → **APIs & Services → Credentials**.
2. Create or open the production OAuth 2.0 Client.
3. **Authorized JavaScript origins** — add the exact frontend URL(s):
   - `https://ishtop.uz`
   - `https://www.ishtop.uz`
   - or `https://<frontend>.up.railway.app`
4. **Authorized redirect URIs** — add the backend callback exactly:
   - `https://api.ishtop.uz/api/v1/auth/callback/google`
   - or `https://<backend>.up.railway.app/api/v1/auth/callback/google`
5. **Reset secret** — if the secret ever lived in a local `.env`, click
   *Reset client secret* and update `GOOGLE_CLIENT_SECRET` in Railway/Render.

## E. Database & migrations

Alembic is wired. Backend `startCommand` runs `alembic upgrade head` before
gunicorn boots, so each deploy is automatically migrated.

Manual operations:

```bash
# View current revision
railway run --service backend alembic current

# Generate a new migration after editing models
cd backend && alembic revision --autogenerate -m "describe change"

# Rollback last migration
railway run --service backend alembic downgrade -1

# Backup before risky migrations
railway run --service postgres pg_dump > backup-$(date +%F).sql
```

Seed / demo data:

- No standalone seed script exists. To create a first admin in production,
  set `BOOTSTRAP_ADMIN_EMAIL` + `BOOTSTRAP_ADMIN_PASSWORD` env vars
  temporarily; the backend creates/promotes that user on next start.
- **Remove these env vars from the dashboard immediately after the admin is
  created** — otherwise every restart re-applies them.

## F. Health checks

| Service | Path | Expected |
|---|---|---|
| Backend | `GET /health` | `200 { "status": "healthy", "database": "connected", ... }` |
| Frontend | `GET /` | `200` HTML |
| Backend (deep) | `GET /api/v1/auth/me` | `401` unauthenticated, `200` after cookie login |

Railway uses backend `healthcheckPath: /health` (configured in
[backend/railway.json](../backend/railway.json)). Render uses the same path
via `healthCheckPath` in [render.yaml](../render.yaml).

## G. Post-deploy QA checklist

Run this against the production URLs immediately after deploy:

1. `curl https://<backend>/health` → 200, `database: connected`.
2. `curl -I https://<frontend>` → 200, `Content-Security-Policy` header present.
3. Register a throwaway account → backend sets `access_token` + `refresh_token`
   cookies with `HttpOnly`, `Secure`, `SameSite=Lax`.
4. Refresh the dashboard page → session persists.
5. Open DevTools → Application → Local Storage. Confirm `auth-storage` value
   has `user` + `isAuthenticated` only, **no access_token field**.
6. Open DevTools → Network → any API call → confirm `Cookie` header present,
   no `Authorization: Bearer`.
7. Logout → cookies cleared, `/student` redirects to `/login`.
8. Try `/admin` as student → blocked.
9. Mobile (375 wide) → bottom nav present on `/student`, `/company`, `/admin`.
10. Hard-refresh `/student/jobs` → 1 `<h1>`, no horizontal overflow.

## H. Rollback plan

Railway and Render both retain prior deployments:

1. Railway → service → **Deployments** tab → **Rollback** on the last
   known-good build.
2. Render → service → **Manual Deploy → Deploy from previous commit**.
3. If a migration introduced the regression, also `alembic downgrade -1`.
4. Notify users via banner if downtime exceeded 5 minutes.

## I. Manual operations still required before first prod deploy

Run these **before** flipping DNS:

- [ ] Rotate `GOOGLE_CLIENT_SECRET` (Cloud Console)
- [ ] Generate new `SECRET_KEY` and set in Railway/Render dashboard
- [ ] Rotate `GEMINI_API_KEY` if any local `.env` value was ever shared
- [ ] Set all backend env vars listed in §A.2
- [ ] Set all frontend env vars listed in §A.3
- [ ] Provision Redis, set `REDIS_URL`, flip `REDIS_ENABLED=true`
- [ ] Provision Postgres, set `DATABASE_URL`
- [ ] Configure Google OAuth authorized origins + redirect URI
- [ ] `bash scripts/check-env-safety.sh` → all green
- [ ] First deploy with `BOOTSTRAP_ADMIN_EMAIL` + `BOOTSTRAP_ADMIN_PASSWORD`,
      then immediately remove those env vars
- [ ] Walk through Post-deploy QA checklist (§G)
