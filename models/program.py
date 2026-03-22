"""Data blueprint: Program (scope container) with in/out scope and settings JSONB."""

from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import BaseModel

if TYPE_CHECKING:
    from models.asset import Asset


class Program(BaseModel):
    """Bug bounty program / target: scope rules and metadata (spec section 1)."""

    __tablename__ = "programs"

    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    platform: Mapped[str] = mapped_column(String(16), nullable=False, default="H1")
    reward_type: Mapped[str | None] = mapped_column(String(64), nullable=True)
    in_scope: Mapped[dict | list] = mapped_column(JSONB, nullable=False, default=list)
    out_scope: Mapped[dict | list] = mapped_column(JSONB, nullable=False, default=list)
    settings: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)

    assets: Mapped[list[Asset]] = relationship(
        "Asset",
        back_populates="program",
        cascade="all, delete-orphan",
    )
