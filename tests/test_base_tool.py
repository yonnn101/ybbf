"""Tests for core.base_tool.AsyncBaseTool (stdlib asyncio + unittest only)."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any

from core.base_tool import AsyncBaseTool, ToolResult


class _EchoLinesTool(AsyncBaseTool):
    """Minimal concrete tool for tests."""

    tool_name = "echo_lines"

    def parse_output(self, output_string: str) -> list[dict[str, Any]]:
        return [{"line": line} for line in output_string.splitlines() if line.strip()]


class TestAsyncBaseTool(unittest.IsolatedAsyncioTestCase):
    async def test_run_subprocess_success(self) -> None:
        with TemporaryDirectory() as tmp:
            raw = Path(tmp) / "raw"
            tool = _EchoLinesTool(binary_path=sys.executable, output_directory=raw)
            result = await tool.run_subprocess(["-c", "print('hello-world')"])
            self.assertIsInstance(result, ToolResult)
            self.assertEqual(result.exit_code, 0)
            self.assertFalse(result.timed_out)
            self.assertIn("hello-world", result.stdout)

    async def test_run_subprocess_nonzero_exit(self) -> None:
        tool = _EchoLinesTool(binary_path=sys.executable, output_directory=Path(sys.executable).parent)
        result = await tool.run_subprocess(
            ["-c", "import sys; sys.stderr.write('oops'); sys.exit(7)"],
        )
        self.assertEqual(result.exit_code, 7)
        self.assertIn("oops", result.stderr)

    async def test_timeout_kills_process(self) -> None:
        tool = _EchoLinesTool(
            binary_path=sys.executable,
            timeout_seconds=0.3,
        )
        result = await tool.run_subprocess(["-c", "import time; time.sleep(30)"])
        self.assertTrue(result.timed_out)
        self.assertEqual(result.exit_code, -1)

    def test_save_raw_output(self) -> None:
        with TemporaryDirectory() as tmp:
            raw = Path(tmp) / "raw"
            tool = _EchoLinesTool(binary_path=sys.executable, output_directory=raw)
            path = tool.save_raw_output("payload-bytes-ok", "test_out.txt")
            self.assertTrue(path.is_file())
            self.assertEqual(path.read_text(encoding="utf-8"), "payload-bytes-ok")

    def test_save_raw_output_rejects_invalid_filename(self) -> None:
        tool = _EchoLinesTool(binary_path=sys.executable)
        with self.assertRaises(ValueError):
            tool.save_raw_output("x", "..")
        # Path segments stripped to basename; "passwd" is valid under output_directory
        with self.assertRaises(ValueError):
            tool.save_raw_output("x", "")

    async def test_run_and_parse(self) -> None:
        with TemporaryDirectory() as tmp:
            raw = Path(tmp) / "raw"
            tool = _EchoLinesTool(binary_path=sys.executable, output_directory=raw)
            result, rows = await tool.run_and_parse(
                ["-c", "print('a'); print('b')"],
                save_raw_filename="run.txt",
            )
            self.assertEqual(result.exit_code, 0)
            self.assertEqual(len(rows), 2)
            self.assertEqual(rows[0]["line"], "a")
            self.assertTrue((raw / "run.txt").is_file())

    async def test_run_and_parse_empty_on_failure(self) -> None:
        tool = _EchoLinesTool(binary_path=sys.executable)
        result, rows = await tool.run_and_parse(["-c", "import sys; sys.exit(1)"])
        self.assertEqual(result.exit_code, 1)
        self.assertEqual(rows, [])


if __name__ == "__main__":
    unittest.main()
