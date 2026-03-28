"""Validation layer: background discovery / recon task triggers."""

from __future__ import annotations

import uuid

from pydantic import BaseModel, Field


class SubdomainDiscoveryRequest(BaseModel):
    """Enqueue Subfinder against ``domain``, linking results under ``root_domain_asset_id``."""

    root_domain_asset_id: uuid.UUID = Field(
        ...,
        description="Existing DOMAIN asset id for this program (parent for discovered subdomains).",
    )
    domain: str | None = Field(
        None,
        description="Optional override; defaults to the root DOMAIN asset's value.",
    )


class SubdomainDiscoveryResponse(BaseModel):
    """Celery task handle for the queued discovery run."""

    task_id: str
    status: str = "queued"
