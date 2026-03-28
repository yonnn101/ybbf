"""Unit tests for SubfinderTask JSON parsing (no subprocess)."""

from __future__ import annotations

import json
import unittest
from pathlib import Path

from workers.tasks.discovery import SubfinderTask


class TestSubfinderTaskParseOutput(unittest.TestCase):
    def setUp(self) -> None:
        self.tool = SubfinderTask(binary_path=Path("/bin/true"))

    def test_ndjson_hosts(self) -> None:
        raw = '{"host":"a.example.com"}\n{"host":"b.example.com"}\n'
        rows = self.tool.parse_output(raw)
        self.assertEqual(
            [r.get("host") for r in rows],
            ["a.example.com", "b.example.com"],
        )

    def test_json_array(self) -> None:
        raw = json.dumps([{"host": "x.example.com"}, "y.example.com"])
        rows = self.tool.parse_output(raw)
        hosts = [_row_host(r) for r in rows]
        self.assertEqual(hosts, ["x.example.com", "y.example.com"])

    def test_plain_lines(self) -> None:
        rows = self.tool.parse_output("api.example.com\n")
        self.assertEqual(rows, [{"host": "api.example.com"}])


def _row_host(row: dict) -> str:
    return row.get("host") or ""


if __name__ == "__main__":
    unittest.main()
