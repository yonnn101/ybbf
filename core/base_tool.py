"""Infrastructure: abstract wrapper for subprocess/Docker tool execution (spec section 2)."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any

from loguru import logger


@dataclass
class ToolResult:
    """Normalized stdout/stderr/exit status from an external recon tool."""

    exit_code: int
    stdout: str
    stderr: str
    command: list[str]


class BaseTool(ABC):
    """Base class for Nuclei, Subfinder, httpx, etc.: logging and error handling hooks."""

    name: str = "base_tool"

    @abstractmethod
    async def run(self, *args: Any, **kwargs: Any) -> ToolResult:
        """Execute the tool (subprocess or Docker); implementations must catch OSError."""

    def log_result(self, result: ToolResult) -> None:
        """Emit structured logs for debugging (truncate very large stdout)."""
        preview = (result.stdout or "")[:2000]
        logger.info(
            "Tool {name} finished exit={code} stdout_preview={preview!r}",
            name=self.name,
            code=result.exit_code,
            preview=preview,
        )
        if result.stderr:
            logger.warning("Tool {name} stderr: {err}", name=self.name, err=result.stderr[:2000])
