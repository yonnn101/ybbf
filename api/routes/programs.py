"""Interface layer: HTTP routes for Program CRUD."""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from api.deps import get_current_active_user, get_db
from schemas.program import ProgramCreate, ProgramRead, ProgramUpdate
from services import program_service

router = APIRouter(
    prefix="/programs",
    tags=["programs"],
    dependencies=[Depends(get_current_active_user)],
)


@router.post("", response_model=ProgramRead, status_code=status.HTTP_201_CREATED)
async def create_program(
    body: ProgramCreate,
    db: AsyncSession = Depends(get_db),
) -> ProgramRead:
    program = await program_service.create_program(
        db,
        name=body.name,
        platform=body.platform,
        reward_type=body.reward_type,
        in_scope=body.in_scope,
        out_scope=body.out_scope,
        settings=body.settings,
    )
    return ProgramRead.model_validate(program)


@router.get("", response_model=list[ProgramRead])
async def list_programs(db: AsyncSession = Depends(get_db)) -> list[ProgramRead]:
    programs = await program_service.list_programs(db)
    return [ProgramRead.model_validate(p) for p in programs]


@router.get("/{program_id}", response_model=ProgramRead)
async def get_program(
    program_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> ProgramRead:
    program = await program_service.get_program(db, program_id)
    if program is None:
        raise HTTPException(status_code=404, detail="Program not found")
    return ProgramRead.model_validate(program)


@router.patch("/{program_id}", response_model=ProgramRead)
async def update_program(
    program_id: uuid.UUID,
    body: ProgramUpdate,
    db: AsyncSession = Depends(get_db),
) -> ProgramRead:
    program = await program_service.update_program(
        db,
        program_id,
        name=body.name,
        platform=body.platform,
        reward_type=body.reward_type,
        in_scope=body.in_scope,
        out_scope=body.out_scope,
        settings=body.settings,
    )
    if program is None:
        raise HTTPException(status_code=404, detail="Program not found")
    return ProgramRead.model_validate(program)


@router.delete("/{program_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_program(
    program_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> None:
    deleted = await program_service.delete_program(db, program_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Program not found")
