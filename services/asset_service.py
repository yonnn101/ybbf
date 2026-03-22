"""Business logic: asset graph get-or-create and relation edges (spec sections 1 & 3)."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import Any

from loguru import logger
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.asset import Asset
from models.asset_relation import AssetRelation


async def get_or_create_asset(
    session: AsyncSession,
    program_id: uuid.UUID,
    asset_type: str,
    value: str,
    *,
    metadata: dict[str, Any] | None = None,
) -> Asset:
    """Return existing asset for (program_id, type, value) or insert a new row.

    Use within a request-scoped session (``get_db`` commits after the handler).
    """
    stmt = select(Asset).where(
        Asset.program_id == program_id,
        Asset.type == asset_type,
        Asset.value == value,
    )
    result = await session.execute(stmt)
    existing = result.scalar_one_or_none()
    now = datetime.now(UTC)
    if existing is not None:
        existing.last_seen = now
        if metadata:
            merged = dict(existing.metadata_)
            merged.update(metadata)
            existing.metadata_ = merged
        await session.flush()
        return existing

    asset = Asset(
        program_id=program_id,
        type=asset_type,
        value=value,
        metadata_=metadata or {},
        first_seen=now,
        last_seen=now,
    )
    session.add(asset)
    await session.flush()
    return asset


async def add_asset_with_relation(
    session: AsyncSession,
    program_id: uuid.UUID,
    asset_type: str,
    value: str,
    *,
    metadata: dict[str, Any] | None = None,
    parent_asset_id: uuid.UUID | None = None,
    relation_type: str | None = None,
) -> tuple[Asset, AssetRelation | None]:
    """Get or create an asset and optionally link it from a parent (graph edge).

    Enforces same-program parent, skips self-edges, and deduplicates relations.
    Commits are handled by the FastAPI ``get_db`` dependency for HTTP handlers.
    """
    child = await get_or_create_asset(
        session,
        program_id,
        asset_type,
        value,
        metadata=metadata,
    )

    if parent_asset_id is None or relation_type is None:
        return child, None

    if parent_asset_id == child.id:
        logger.warning("Skipping self-relation for asset {}", child.id)
        return child, None

    parent = await session.get(Asset, parent_asset_id)
    if parent is None:
        msg = f"Parent asset {parent_asset_id} not found"
        raise ValueError(msg)
    if parent.program_id != program_id:
        msg = "Parent asset belongs to a different program"
        raise ValueError(msg)

    rel_stmt = select(AssetRelation).where(
        AssetRelation.parent_id == parent_asset_id,
        AssetRelation.child_id == child.id,
        AssetRelation.relation_type == relation_type,
    )
    rel_result = await session.execute(rel_stmt)
    existing_rel = rel_result.scalar_one_or_none()
    if existing_rel is not None:
        return child, existing_rel

    relation = AssetRelation(
        parent_id=parent_asset_id,
        child_id=child.id,
        relation_type=relation_type,
    )
    session.add(relation)
    await session.flush()
    await session.refresh(relation)
    return child, relation


async def get_program_graph(
    session: AsyncSession,
    program_id: uuid.UUID,
) -> tuple[list[Asset], list[AssetRelation]]:
    """Load all assets for a program and relations whose endpoints are in that set."""
    assets_result = await session.execute(select(Asset).where(Asset.program_id == program_id))
    assets = list(assets_result.scalars().all())
    id_set = {a.id for a in assets}
    if not id_set:
        return [], []

    rel_result = await session.execute(
        select(AssetRelation).where(
            AssetRelation.parent_id.in_(id_set),
            AssetRelation.child_id.in_(id_set),
        )
    )
    edges = list(rel_result.scalars().all())
    return assets, edges
