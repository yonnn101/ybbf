#!/bin/sh
set -e

cd /app

if [ "$1" = "api" ]; then
  echo "Running Alembic migrations..."
  alembic upgrade head
  echo "Starting uvicorn..."
  exec uvicorn main:app --host 0.0.0.0 --port 8000
fi

if [ "$1" = "worker" ]; then
  shift
  exec celery -A workers.celery_app worker \
    -Q fast,slow \
    --loglevel="${CELERY_LOG_LEVEL:-info}" \
    "$@"
fi

exec "$@"
