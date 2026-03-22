"""Data blueprint: security finding with dedupe hash and optional MinIO raw output link."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import BaseModel

if TYPE_CHECKING:
    from models.asset import Asset


class Finding(BaseModel):
    """Vulnerability or signal tied to an asset; dedupe_hash prevents duplicate rows (spec)."""

    __tablename__ = "findings"

    asset_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("assets.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    tool_source: Mapped[str] = mapped_column(String(128), nullable=False)
    severity: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(512), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    raw_output_link: Mapped[str | None] = mapped_column(String(2048), nullable=True)
    dedupe_hash: Mapped[str] = mapped_column(String(64), nullable=False, unique=True, index=True)
    vulnerability_type: Mapped[str] = mapped_column(String(255), nullable=False, default="unknown")
    endpoint: Mapped[str | None] = mapped_column(String(2048), nullable=True)
    last_seen: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    asset: Mapped[Asset] = relationship("Asset", foreign_keys=[asset_id])
