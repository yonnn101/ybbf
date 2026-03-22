"""Execution layer: sample Subfinder task (placeholder — wire BaseTool + MinIO later)."""

from __future__ import annotations

from loguru import logger

from workers.celery_app import celery_app


@celery_app.task(name="yonnn.subfinder.run")
def run_subfinder_scan(program_id: str, domain: str) -> dict[str, str]:
    """Queue-friendly stub: logs intent; replace with docker/subprocess + result upload."""
    logger.info(
        "Subfinder task queued program_id={} domain={} (stub — no binary executed)",
        program_id,
        domain,
    )
    return {
        "status": "stub_complete",
        "program_id": program_id,
        "domain": domain,
        "message": "Implement BaseTool + job row + MinIO upload in next iteration",
    }
