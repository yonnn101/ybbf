"""Execution layer: Celery application (broker from REDIS_URL)."""

from __future__ import annotations

import os

from celery import Celery

# Avoid importing DB settings here so workers can start without DATABASE_URL.
broker_url = os.environ.get("REDIS_URL", "redis://localhost:6379/0")

celery_app = Celery(
    "yonnn",
    broker=broker_url,
    backend=broker_url,
    include=["workers.tasks.subfinder"],
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
)
