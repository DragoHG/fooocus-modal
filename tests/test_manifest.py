"""Lightweight tests for models.txt parsing (no Modal required)."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.manifest import parse_manifest  # noqa: E402


class ManifestTests(unittest.TestCase):
    def test_parse_tab_line(self) -> None:
        text = (
            "# comment\n"
            "checkpoint\tmodel.safetensors\thttps://example.com/model.safetensors\n"
        )
        entries = parse_manifest(text)
        self.assertEqual(len(entries), 1)
        self.assertEqual(entries[0].kind, "checkpoint")
        self.assertEqual(entries[0].relative_name, "model.safetensors")

    def test_rejects_path_escape(self) -> None:
        text = "lora\t../evil.safetensors\thttps://example.com/x\n"
        with self.assertRaises(ValueError):
            parse_manifest(text)

    def test_rejects_bad_scheme(self) -> None:
        text = "lora\ta.safetensors\tfile:///tmp/a\n"
        with self.assertRaises(ValueError):
            parse_manifest(text)


if __name__ == "__main__":
    unittest.main()
