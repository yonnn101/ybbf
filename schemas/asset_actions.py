"""Validation layer: request bodies for asset ingestion (get-or-create + relation)."""

from __future__ import annotations

import uuid
from typing import Any

from pydantic import BaseModel, Field


class AssetIngestRequest(BaseModel):
    """Add or touch an asset and optionally link it from a parent."""

    type: str = Field(..., min_length=1, max_length=32)
    value: str = Field(..., min_length=1, max_length=2048)
    metadata: dict[str, Any] = Field(default_factory=dict)
    parent_asset_id: uuid.UUID | None = None
    relation_type: str | None = Field(default=None, max_length=64)
