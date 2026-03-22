"""Data blueprint: declarative ORM base plus shared UUID primary key and audit timestamps."""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """SQLAlchemy 2.0 declarative base for all yonnn ORM models."""


class BaseModel(Base):
    """Abstract mapped class with id, created_at, and updated_at (no table of its own).

    Note: ``onupdate=func.now()`` updates ``updated_at`` when SQLAlchemy issues UPDATEs
    for changed columns; for guaranteed DB-level freshness you can add triggers in migrations.
    """

    __abstract__ = True

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
