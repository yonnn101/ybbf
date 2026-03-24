"""Data blueprint: Program (scope container) with in/out scope and settings JSONB."""

from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import BaseModel

if TYPE_CHECKING:
    from models.asset import Asset
    from models.user import User


class Program(BaseModel):
    """Bug bounty program / target: scope rules and metadata (spec section 1)."""

    __tablename__ = "programs"

    owner_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    platform: Mapped[str] = mapped_column(String(16), nullable=False, default="H1")
    reward_type: Mapped[str | None] = mapped_column(String(64), nullable=True)
    in_scope: Mapped[dict | list] = mapped_column(JSONB, nullable=False, default=list)
    out_scope: Mapped[dict | list] = mapped_column(JSONB, nullable=False, default=list)
    settings: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)

    owner: Mapped[User] = relationship("User", back_populates="programs")
    assets: Mapped[list[Asset]] = relationship(
        "Asset",
        back_populates="program",
        cascade="all, delete-orphan",
    )
