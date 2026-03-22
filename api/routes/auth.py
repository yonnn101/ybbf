"""Interface layer: registration, OAuth2 token, and current-user profile."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from api.deps import get_current_active_user, get_db
from models.user import User
from schemas.auth import Token, UserCreate, UserRead
from services import auth_service

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def register(
    body: UserCreate,
    db: AsyncSession = Depends(get_db),
) -> UserRead:
    """Create a new user (email + password)."""
    try:
        user = await auth_service.create_user(
            db,
            email=body.email,
            password=body.password,
            full_name=body.full_name,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc
    return UserRead.model_validate(user)


@router.post("/token", response_model=Token)
async def login_for_access_token(
    db: AsyncSession = Depends(get_db),
    form_data: OAuth2PasswordRequestForm = Depends(),
) -> Token:
    """OAuth2 password flow: use **username** = email, **password** = password."""
    user = await auth_service.authenticate_user(
        db,
        form_data.username,
        form_data.password,
    )
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    access_token = auth_service.issue_access_token(user.id)
    return Token(access_token=access_token)


@router.get("/me", response_model=UserRead)
async def read_me(
    current_user: User = Depends(get_current_active_user),
) -> UserRead:
    """Return the authenticated user (requires Bearer token)."""
    return UserRead.model_validate(current_user)
