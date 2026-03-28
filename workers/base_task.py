"""Execution layer: Celery task base with async DB session and default retry policy (spec §2, §4)."""

from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable
from typing import Any, TypeVar

from celery import Task
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import AsyncSessionLocal

T = TypeVar("T")


class YonnnTask(Task):
    """Base task: JSON-serializable args, default exponential retries, optional ``AsyncSession`` scope.

    Use ``bind=True`` and call ``self.run_with_session(coro, *args, **kwargs)`` where
    ``coro`` is ``async (session, *args, **kwargs) -> result``. The session is committed
    on success and rolled back on error — same pattern as FastAPI ``get_db``.

    For tasks that do not need the database, implement a regular ``run`` without
    ``run_with_session``.
    """

    abstract = True

    # Tool / IO failures: bounded exponential backoff (spec §4).
    autoretry_for: tuple[type[BaseException], ...] = (Exception,)
    retry_kwargs: dict[str, Any] = {"max_retries": 3}
    retry_backoff: bool = True
    retry_backoff_max: int = 600
    retry_jitter: bool = True

    def run_with_session(
        self,
        coro: Callable[..., Awaitable[T]],
        *args: Any,
        **kwargs: Any,
    ) -> T:
        """Run ``coro(session, *args, **kwargs)`` inside a committed async session."""

        async def _runner() -> T:
            async with AsyncSessionLocal() as session:
                try:
                    result = await coro(session, *args, **kwargs)
                    await session.commit()
                    return result
                except Exception:
                    await session.rollback()
                    logger.exception(
                        "YonnnTask session rollback task_id={} name={}",
                        getattr(self.request, "id", None),
                        self.name,
                    )
                    raise

        return asyncio.run(_runner())


# Spec / step-4 naming (Celery task base with ``run_with_session``).
AsyncBaseTask = YonnnTask
