"""Unit tests for Volume path helpers."""

from __future__ import annotations

import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.paths import (  # noqa: E402
    MODEL_SUBDIRS,
    ensure_layout,
    model_dir,
    outputs_dir,
    zero_telemetry_enabled,
)


class PathsTests(unittest.TestCase):
    def test_model_kinds_cover_fooocus_assets(self) -> None:
        for kind in (
            "checkpoint",
            "lora",
            "vae",
            "controlnet",
            "clip_vision",
            "inpaint",
            "upscale",
            "expansion",
            "vae_approx",
        ):
            self.assertIn(kind, MODEL_SUBDIRS)

    def test_zero_telemetry_default_true(self) -> None:
        env = {k: v for k, v in os.environ.items() if k != "ZERO_TELEMETRY"}
        with mock.patch.dict(os.environ, env, clear=True):
            self.assertTrue(zero_telemetry_enabled())

    def test_zero_telemetry_false(self) -> None:
        with mock.patch.dict(os.environ, {"ZERO_TELEMETRY": "false"}):
            self.assertFalse(zero_telemetry_enabled())

    def test_ensure_layout_creates_dirs(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            with mock.patch.dict(os.environ, {"FOOOCUS_VOL_ROOT": tmp}):
                ensure_layout()
                self.assertTrue(model_dir("checkpoint").is_dir())
                self.assertTrue(outputs_dir().is_dir() or zero_telemetry_enabled())


if __name__ == "__main__":
    unittest.main()
