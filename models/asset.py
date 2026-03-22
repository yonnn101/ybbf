"""Data blueprint: Asset node in the attack-surface graph (unique per program, type, value)."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, String, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import BaseModel

if TYPE_CHECKING:
    from models.asset_relation import AssetRelation
    from models.program import Program


class Asset(BaseModel):
    """Single asset vertex; metadata holds tech, ASN, DNS, screenshot keys, etc."""

    __tablename__ = "assets"
    __table_args__ = (
        UniqueConstraint("program_id", "type", "value", name="uq_assets_program_type_value"),
    )

    program_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("programs.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    type: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    value: Mapped[str] = mapped_column(String(2048), nullable=False, index=True)
    metadata_: Mapped[dict] = mapped_column("metadata", JSONB, nullable=False, default=dict)
    first_seen: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    last_seen: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    program: Mapped[Program] = relationship("Program", back_populates="assets")
    parent_links: Mapped[list[AssetRelation]] = relationship(
        "AssetRelation",
        foreign_keys="AssetRelation.parent_id",
        back_populates="parent",
        passive_deletes=True,
    )
    child_links: Mapped[list[AssetRelation]] = relationship(
        "AssetRelation",
        foreign_keys="AssetRelation.child_id",
        back_populates="child",
        passive_deletes=True,
    )
