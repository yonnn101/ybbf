"""Data blueprint: directed edges between assets (the correlation graph)."""

from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import BaseModel

if TYPE_CHECKING:
    from models.asset import Asset


class AssetRelation(BaseModel):
    """Parent -> child relationship with a typed edge (e.g. resolves_to, hosts)."""

    __tablename__ = "asset_relations"
    __table_args__ = (
        UniqueConstraint(
            "parent_id",
            "child_id",
            "relation_type",
            name="uq_asset_relations_parent_child_type",
        ),
    )

    parent_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("assets.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    child_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("assets.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    relation_type: Mapped[str] = mapped_column(String(64), nullable=False, index=True)

    parent: Mapped[Asset] = relationship(
        "Asset",
        foreign_keys=[parent_id],
        back_populates="parent_links",
    )
    child: Mapped[Asset] = relationship(
        "Asset",
        foreign_keys=[child_id],
        back_populates="child_links",
    )
