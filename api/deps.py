"""Interface layer: FastAPI dependencies (DB session, current user, etc.)."""

from __future__ import annotations

from collections.abc import AsyncGenerator
from typing import Annotated

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from core.auth_settings import get_auth_settings
from core.database import get_db as _get_db
from core.security import decode_access_token
from models.user import User
from services import auth_service

http_bearer_optional = HTTPBearer(auto_error=False)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Re-export async session dependency for routers."""
    async for session in _get_db():
        yield session


credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)


def _raw_access_token(
    request: Request,
    credentials: HTTPAuthorizationCredentials | None,
) -> str | None:
    """Bearer header wins; else httpOnly cookie (browser UI)."""
    if credentials and credentials.credentials:
        return credentials.credentials
    cookie_name = get_auth_settings().access_token_cookie_name
    return request.cookies.get(cookie_name)


async def get_access_token_str(
    request: Request,
    credentials: Annotated[
        HTTPAuthorizationCredentials | None,
        Depends(http_bearer_optional),
    ],
) -> str:
    raw = _raw_access_token(request, credentials)
    if not raw:
        raise credentials_exception
    return raw


async def get_current_user(
    db: Annotated[AsyncSession, Depends(get_db)],
    token: Annotated[str, Depends(get_access_token_str)],
) -> User:
    """Resolve JWT from ``Authorization: Bearer`` or ``access_token`` cookie to a User row."""
    user_id = decode_access_token(token)
    if user_id is None:
        raise credentials_exception
    user = await auth_service.get_user_by_id(db, user_id)
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)],
) -> User:
    """Require an active (non-disabled) account."""
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


async def require_superuser(
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> User:
    """Require ``is_superuser`` (use for admin-only routes)."""
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Superuser privileges required",
        )
    return current_user
