"""Data blueprint: tool execution job linked to a target asset (spec section 1)."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import BaseModel

if TYPE_CHECKING:
    from models.asset import Asset


class Job(BaseModel):
    """Long-running or background scan record (stdout/stderr go to MinIO in production)."""

    __tablename__ = "jobs"

    tool_name: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="pending", index=True)
    target_asset_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("assets.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    start_time: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    end_time: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    raw_output_link: Mapped[str | None] = mapped_column(String(2048), nullable=True)

    target_asset: Mapped[Asset | None] = relationship("Asset", foreign_keys=[target_asset_id])
