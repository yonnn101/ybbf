# Security notes

## Secrets and configuration

- **Never commit** `.env` or any file containing real passwords, API keys, or JWT secrets. This repository’s `.gitignore` is set to ignore common env filenames and key material; keep using **`.env.example`** only as a non-secret template.
- **JWT:** Set a strong `JWT_SECRET_KEY` in production (e.g. `openssl rand -hex 32`). If unset, the app falls back to a **development-only** default (`core/auth_settings.py`); that default must not be used in production.
- **Superuser bootstrap:** `SUPERUSER_EMAIL` / `SUPERUSER_PASSWORD` grant elevated access. Use long random passwords and restrict who can set these variables.
- **Docker Compose:** `docker-compose.yml` ships **local development** defaults (Postgres, MinIO, optional JWT fallback). Replace them with secrets from your environment or a secrets manager before any shared or production deployment.

## What is not a “live” secret in code

- Python code loads secrets from the environment (pydantic-settings), except the **documented dev default** for `JWT_SECRET_KEY` when the variable is missing.
- `.env.example` and README examples use placeholders (`change-me`, `your_key`, etc.).

## If a secret was committed to Git

If `.env` or any real key ever entered Git history, **rotate the exposed credential immediately** (new DB password, new JWT secret, revoke API keys, etc.). Removing the file in a new commit does **not** remove it from history.

1. **Preferred:** [git-filter-repo](https://github.com/newren/git-filter-repo) to purge the file or replace strings across history (install separately, then follow its docs for `--path` / `--replace-text`).
2. **Alternative:** [BFG Repo-Cleaner](https://rtyley.github.io/bfg-repo-cleaner/) to delete files or replace secrets in history.
3. After rewriting history, **force-push** coordinated with all collaborators and assume old clones may still contain the leak.

If this folder is **not** a Git repository yet, initialize Git only after confirming no secret files are staged; use `.env` locally and never `git add .env`.

### Before each commit (optional)

From the repo root, PowerShell:

```powershell
.\scripts\check-tracked-secrets.ps1
```

This errors if `.env`, `*.pem`, or similar files are tracked. It does **not** scan file contents for API keys.

## Reporting

If you discover a security issue in this project, report it responsibly to the maintainers (do not open a public issue with exploit details until fixed).
