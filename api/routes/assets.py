"""Interface layer: asset graph view and ingestion endpoints."""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from api.deps import get_current_active_user, get_db
from models.user import User
from schemas.asset_actions import AssetIngestRequest
from schemas.graph import GraphEdge, GraphNode, GraphView
from services import asset_service, program_service

router = APIRouter(tags=["assets"])


@router.get("/programs/{program_id}/graph", response_model=GraphView)
async def get_program_graph(
    program_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> GraphView:
    program = await program_service.get_program_for_owner(db, program_id, current_user.id)
    if program is None:
        raise HTTPException(status_code=404, detail="Program not found")
    assets, edges = await asset_service.get_program_graph(db, program_id)
    nodes = [GraphNode.model_validate(a) for a in assets]
    edge_dtos = [GraphEdge.model_validate(e) for e in edges]
    return GraphView(program_id=program_id, nodes=nodes, edges=edge_dtos)


@router.post(
    "/programs/{program_id}/assets",
    status_code=status.HTTP_201_CREATED,
)
async def ingest_asset(
    program_id: uuid.UUID,
    body: AssetIngestRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> dict[str, str | None]:
    try:
        program = await program_service.get_program_for_owner(db, program_id, current_user.id)
        if program is None:
            raise HTTPException(status_code=404, detail="Program not found")
        child, rel = await asset_service.add_asset_with_relation(
            db,
            program_id,
            body.type,
            body.value,
            metadata=body.metadata,
            parent_asset_id=body.parent_asset_id,
            relation_type=body.relation_type,
        )
    except HTTPException:
        raise
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {
        "asset_id": str(child.id),
        "relation_id": str(rel.id) if rel else None,
    }
