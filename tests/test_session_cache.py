"""Session gallery + settings cache (reload persistence)."""

from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import local.ui as ui  # noqa: E402
from local.presets import SETTING_KEYS  # noqa: E402


class SessionCacheTests(unittest.TestCase):
    def test_persist_and_load_filters_missing(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp)
            alive = out / "a.png"
            alive.write_bytes(b"x")
            missing = out / "gone.png"
            with mock.patch.object(ui, "OUTPUT_DIR", out), mock.patch.object(
                ui, "SESSION_CACHE_PATH", out / ".session_cache.json"
            ), mock.patch.object(ui, "PRESET_DIR", out / "presets"):
                ui._persist_session(
                    [str(alive), str(missing)],
                    1,
                    [str(missing), str(alive)],
                    {"prompt": "hello", "performance": "Lightning", "seed": 3},
                )
                hist, idx, picked, settings = ui._load_session_cache()
            self.assertEqual(hist, [str(alive)])
            self.assertEqual(idx, 0)
            self.assertEqual(picked, [str(alive)])
            self.assertEqual(settings["prompt"], "hello")
            self.assertEqual(settings["performance"], "Lightning")
            self.assertEqual(settings["seed"], 3)

    def test_viewer_persist_keeps_settings(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp)
            alive = out / "b.png"
            alive.write_bytes(b"y")
            with mock.patch.object(ui, "OUTPUT_DIR", out), mock.patch.object(
                ui, "SESSION_CACHE_PATH", out / ".session_cache.json"
            ), mock.patch.object(ui, "PRESET_DIR", out / "presets"):
                ui._persist_session([], 0, [], {"prompt": "keep-me", "guidance": 4.5})
                ui._persist_session([str(alive)], 0, [])
                _h, _i, _p, settings = ui._load_session_cache()
            self.assertEqual(settings["prompt"], "keep-me")
            self.assertEqual(settings["guidance"], 4.5)

    def test_last_session_json_has_no_images(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp)
            presets = out / "presets"
            with mock.patch.object(ui, "OUTPUT_DIR", out), mock.patch.object(
                ui, "SESSION_CACHE_PATH", out / ".session_cache.json"
            ), mock.patch.object(ui, "PRESET_DIR", presets):
                ui._persist_session(
                    [],
                    0,
                    [],
                    {"prompt": "x", "preset_name": "t", "styles": ["Fooocus V2"]},
                )
                raw = (presets / "last-session.json").read_text(encoding="utf-8")
            data = json.loads(raw)
            self.assertNotIn("images", data)
            self.assertEqual(data["settings"]["prompt"], "x")
            self.assertTrue(set(data["settings"]).issubset(set(SETTING_KEYS)))


if __name__ == "__main__":
    unittest.main()
