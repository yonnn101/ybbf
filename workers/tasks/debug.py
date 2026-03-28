"""Debug / health tasks: verify worker ↔ Redis ↔ PostgreSQL."""

from __future__ import annotations

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from loguru import logger

from workers.base_task import AsyncBaseTask
from workers.celery_app import celery_app


@celery_app.task(
    bind=True,
    base=AsyncBaseTask,
    name="yonnn.debug.ping",
    queue="fast",
    max_retries=0,
    autoretry_for=(),
)
def debug_ping(self) -> str:
    """Execute ``SELECT 1`` via async session; return ``pong`` if Redis + DB are reachable."""

    async def work(session: AsyncSession) -> str:
        await session.execute(text("SELECT 1"))
        logger.info("debug_ping OK task_id={}", self.request.id)
        return "pong"

    return self.run_with_session(work)
