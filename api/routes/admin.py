"""Superuser-only endpoints (extend with platform admin actions)."""

from __future__ import annotations

from fastapi import APIRouter, Depends

from api.deps import require_superuser

router = APIRouter(
    prefix="/admin",
    tags=["admin"],
    dependencies=[Depends(require_superuser)],
)


@router.get("/ping")
async def admin_ping() -> dict[str, str]:
    """Verify Bearer token belongs to a superuser."""
    return {"status": "ok"}
