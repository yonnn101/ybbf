"""Data blueprint: singleton-style global settings (API keys, rate limits, webhooks)."""

from __future__ import annotations

from sqlalchemy import String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from models.base import BaseModel


class FrameworkSettings(BaseModel):
    """One logical row per environment (use name='default'); stores JSONB blobs (spec section 1)."""

    __tablename__ = "framework_settings"

    name: Mapped[str] = mapped_column(String(64), nullable=False, unique=True, default="default")
    api_keys: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    rate_limits: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    notification_webhooks: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
