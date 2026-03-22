"""Validation layer: graph view DTOs for assets and relations."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class GraphNode(BaseModel):
    """One vertex in the attack-surface graph."""

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: uuid.UUID
    type: str
    value: str
    metadata: dict[str, Any] = Field(
        validation_alias="metadata_",
        serialization_alias="metadata",
    )
    first_seen: datetime
    last_seen: datetime


class GraphEdge(BaseModel):
    """Directed edge parent -> child."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    parent_id: uuid.UUID
    child_id: uuid.UUID
    relation_type: str


class GraphView(BaseModel):
    """Full graph for a program (nodes + edges)."""

    program_id: uuid.UUID
    nodes: list[GraphNode]
    edges: list[GraphEdge]
