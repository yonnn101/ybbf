"""Infrastructure: password hashing (bcrypt) and JWT creation/validation."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import Any
from uuid import UUID

import bcrypt
from jose import JWTError, jwt
from loguru import logger

from core.auth_settings import get_auth_settings


def hash_password(plain_password: str) -> str:
    """Hash a password for storage (bcrypt)."""
    return bcrypt.hashpw(plain_password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Return True if plain password matches stored bcrypt hash."""
    try:
        return bcrypt.checkpw(
            plain_password.encode("utf-8"),
            hashed_password.encode("utf-8"),
        )
    except ValueError:
        return False


def create_access_token(*, subject_user_id: UUID, expires_delta: timedelta | None = None) -> str:
    """Encode a signed JWT with ``sub`` = user id (UUID string)."""
    auth = get_auth_settings()
    expire = datetime.now(UTC) + (
        expires_delta
        if expires_delta is not None
        else timedelta(minutes=auth.access_token_expire_minutes)
    )
    to_encode: dict[str, Any] = {
        "sub": str(subject_user_id),
        "exp": expire,
        "iat": datetime.now(UTC),
    }
    return jwt.encode(to_encode, auth.jwt_secret_key, algorithm=auth.jwt_algorithm)


def decode_access_token(token: str) -> UUID | None:
    """Validate JWT and return user id from ``sub``; returns None on failure."""
    auth = get_auth_settings()
    try:
        payload = jwt.decode(
            token,
            auth.jwt_secret_key,
            algorithms=[auth.jwt_algorithm],
        )
        sub = payload.get("sub")
        if sub is None:
            return None
        return UUID(str(sub))
    except (JWTError, ValueError) as exc:
        logger.debug("JWT decode failed: {}", exc)
        return None
