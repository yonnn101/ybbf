"""Business logic: user registration, credential verification, and token issuance."""

from __future__ import annotations

import uuid

from loguru import logger
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.security import create_access_token, hash_password, verify_password
from models.user import User


async def get_user_by_id(session: AsyncSession, user_id: uuid.UUID) -> User | None:
    """Load user by primary key."""
    return await session.get(User, user_id)


async def get_user_by_email(session: AsyncSession, email: str) -> User | None:
    """Load user by normalized email (case-insensitive match)."""
    normalized = email.strip().lower()
    result = await session.execute(select(User).where(User.email == normalized))
    return result.scalar_one_or_none()


async def create_user(
    session: AsyncSession,
    *,
    email: str,
    password: str,
    full_name: str | None = None,
) -> User:
    """Create user; session is committed by the FastAPI ``get_db`` dependency."""
    normalized = email.strip().lower()
    existing = await get_user_by_email(session, normalized)
    if existing is not None:
        msg = "Email already registered"
        raise ValueError(msg)
    user = User(
        email=normalized,
        hashed_password=hash_password(password),
        full_name=full_name,
        is_active=True,
        is_superuser=False,
    )
    session.add(user)
    await session.flush()
    await session.refresh(user)
    return user


async def authenticate_user(session: AsyncSession, email: str, password: str) -> User | None:
    """Return user if credentials match; otherwise None."""
    user = await get_user_by_email(session, email)
    if user is None:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user


def issue_access_token(user_id: uuid.UUID) -> str:
    """Mint a JWT for the given user id."""
    return create_access_token(subject_user_id=user_id)


async def ensure_bootstrap_superuser(
    session: AsyncSession,
    email: str,
    password: str,
) -> None:
    """Create or promote the configured bootstrap account to superuser (idempotent)."""
    normalized = email.strip().lower()
    user = await get_user_by_email(session, normalized)
    if user is None:
        session.add(
            User(
                email=normalized,
                hashed_password=hash_password(password),
                full_name="Bootstrap superuser",
                is_active=True,
                is_superuser=True,
            ),
        )
        logger.info("Created bootstrap superuser for email {}", normalized)
    else:
        if not user.is_superuser:
            user.is_superuser = True
            logger.info("Promoted existing user {} to superuser", normalized)
        if not user.is_active:
            user.is_active = True
    await session.flush()
