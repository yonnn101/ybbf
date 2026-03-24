"""422 and other handlers that must not echo secrets back to clients."""

from __future__ import annotations

from typing import Any

from fastapi import Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

# Keys whose values are stripped from validation error payloads (request body echoes).
_SENSITIVE_KEYS = frozenset(
    name.lower()
    for name in (
        "password",
        "hashed_password",
        "new_password",
        "old_password",
        "secret",
        "client_secret",
        "access_token",
        "refresh_token",
        "authorization",
        "api_key",
        "apikey",
    )
)


def _redact_value(obj: Any) -> Any:
    if isinstance(obj, dict):
        return {
            k: "***REDACTED***" if str(k).lower() in _SENSITIVE_KEYS else _redact_value(v)
            for k, v in obj.items()
        }
    if isinstance(obj, list):
        return [_redact_value(x) for x in obj]
    return obj


def _redact_validation_errors(errors: list[Any]) -> list[Any]:
    out: list[Any] = []
    for err in errors:
        if not isinstance(err, dict):
            out.append(err)
            continue
        e = dict(err)
        for key in ("input", "ctx"):
            if key in e:
                e[key] = _redact_value(e[key])
        out.append(e)
    return out


async def request_validation_exception_handler(
    _request: Request,
    exc: RequestValidationError,
) -> JSONResponse:
    """422 responses must not repeat passwords or tokens from the rejected body."""
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": jsonable_encoder(_redact_validation_errors(exc.errors()))},
    )
