# yonnn

Unified bug bounty / attack-surface framework (FastAPI, PostgreSQL, Redis/Celery, MinIO).

**Security:** defaults, env files, and what to do if secrets hit Git — see [SECURITY.md](SECURITY.md). Optional: `scripts/check-tracked-secrets.ps1` before commits.

## Run everything with Docker

From the repo root:

```bash
docker compose up --build -d
```

- **API:** http://localhost:8000 — OpenAPI docs at http://localhost:8000/docs  
- **Postgres:** `localhost:5432`  
- **Redis:** `localhost:6379`  
- **MinIO API:** `localhost:9000` — console: http://localhost:9001  

On first start the API container runs `alembic upgrade head`, then starts Uvicorn.

**Celery worker** (optional profile):

```bash
docker compose --profile worker up --build -d
```

**Rebuild after code changes:**

```bash
docker compose build api --no-cache
docker compose up -d api
```

Use `.gitattributes` so `scripts/docker-entrypoint.sh` stays LF on Windows; otherwise the entrypoint may fail.

## Quick start (local Python)

1. Copy `.env.example` to `.env` and adjust values.
2. Start infra: `docker compose up -d` (Postgres, Redis, MinIO).
3. Install deps (Python 3.11+): `pip install -r requirements.txt` or `uv pip install -r requirements.txt`.
4. Run migrations (requires `DATABASE_URL`):

   ```bash
   set DATABASE_URL=postgresql+asyncpg://...
   alembic upgrade head
   ```

5. API:

   ```bash
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

6. Celery worker (optional):

   ```bash
   celery -A workers.celery_app worker --loglevel=info
   ```

## Authentication (JWT)

1. **Register:** `POST /auth/register` with JSON `{ "email", "password", "full_name?" }`.
2. **Token:** `POST /auth/token` (OAuth2 form) — `username` = email, `password` = password. Returns `access_token`.
3. **Use API:** send header `Authorization: Bearer <access_token>` for `/programs/*` and asset routes.
4. **Profile:** `GET /auth/me` with Bearer token.

Set **`JWT_SECRET_KEY`** in production (see `.env.example`). Docker Compose passes `JWT_SECRET_KEY` from your environment or a dev default.

### Superuser bootstrap

Optional env vars (see `.env.example`):

- **`SUPERUSER_EMAIL`** — on API startup, if set together with a password, this account is **created** (if missing) or **promoted** to `is_superuser=true`.
- **`SUPERUSER_PASSWORD`** — must be at least **8 characters** (same minimum as registration).

Use `GET /auth/me` to confirm `is_superuser`. Superuser-only routes live under **`/admin/*`** (e.g. `GET /admin/ping` with Bearer token).

Public without auth: `/health`, `/auth/register`, `/auth/token`, `/docs`, `/openapi.json`.

## API highlights

- `POST /programs` — create program (scope container) **(auth)**.
- `GET /programs/{id}/graph` — nodes (assets) and edges (relations) **(auth)**.
- `POST /programs/{id}/assets` — get-or-create asset + optional parent relation **(auth)**.
- `GET /admin/ping` — sanity check for superuser JWT **(superuser only)**.

## Layout

| Path | Role |
|------|------|
| `api/` | FastAPI routes |
| `core/` | DB, config, BaseTool |
| `models/` | SQLAlchemy ORM |
| `schemas/` | Pydantic DTOs |
| `services/` | Business logic |
| `workers/` | Celery tasks |
