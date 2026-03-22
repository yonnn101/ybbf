"""Validation layer: auth payloads (register, token response, user read)."""

from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserCreate(BaseModel):
    """Register a new user."""

    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)
    full_name: str | None = Field(default=None, max_length=255)


class UserRead(BaseModel):
    """User returned to clients (no password)."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    email: str
    full_name: str | None
    is_active: bool
    is_superuser: bool
    created_at: datetime
    updated_at: datetime


class Token(BaseModel):
    """OAuth2-style access token payload."""

    access_token: str
    token_type: str = "bearer"
