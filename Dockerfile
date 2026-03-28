# yonnn API (FastAPI) — Python 3.11
FROM python:3.11-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

COPY . .

# Windows CRLF breaks shebang/exec ("no such file or directory"); normalize line endings.
RUN sed -i 's/\r$//' /app/scripts/docker-entrypoint.sh \
    && chmod +x /app/scripts/docker-entrypoint.sh \
    && groupadd --system yonnn \
    && useradd --system --gid yonnn --home-dir /app --shell /usr/sbin/nologin yonnn \
    && chown -R yonnn:yonnn /app

USER yonnn

EXPOSE 8000

# Invoke via sh so a bad shebang/CRLF cannot break container start.
ENTRYPOINT ["/bin/sh", "/app/scripts/docker-entrypoint.sh"]
CMD ["api"]
