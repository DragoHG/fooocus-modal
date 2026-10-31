"""Preset JSON save/load helpers."""

from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from local.presets import (  # noqa: E402
    IMAGE_KEYS,
    SETTING_KEYS,
    parse_preset,
    preset_to_json,
    settings_to_updates,
)


def _sample_values(**overrides):
    values = {
        "prompt": "a lighthouse",
        "negative": "blur",
        "styles": ["Fooocus V2"],
        "performance": "Lightning",
        "aspect": "1024*1024",
        "image_number": 1,
        "seed": 7,
        "sharpness": 2.0,
        "guidance": 4.0,
        "base_model": "juggernautXL_v8Rundiffusion.safetensors",
        "refiner_model": "None",
        "refiner_switch": 0.5,
        "lora1": "None",
        "lora1_w": 1.0,
        "lora2": "None",
        "lora2_w": 1.0,
        "lora3": "None",
        "lora3_w": 1.0,
        "lora4": "None",
        "lora4_w": 1.0,
        "lora5": "None",
        "lora5_w": 1.0,
        "input_image_on": False,
        "uov_method": "Disabled",
        "ip1_type": "FaceSwap",
        "ip1_stop": 0.5,
        "ip1_weight": 0.75,
        "ip2_type": "ImagePrompt",
        "ip2_stop": 0.5,
        "ip2_weight": 0.6,
        "ip3_type": "ImagePrompt",
        "ip3_stop": 0.5,
        "ip3_weight": 0.6,
        "ip4_type": "ImagePrompt",
        "ip4_stop": 0.5,
        "ip4_weight": 0.6,
        "mix_ip_uov": False,
        "mix_ip_inpaint": False,
        "inpaint_prompt": "",
        "inpaint_strength": 1.0,
        "inpaint_field": 0.618,
        "inpaint_engine": "v2.6",
        "outpaint": [],
        "enhance_on": False,
        "enhance_uov": "Disabled",
        "output_format": "png",
        "read_wildcards": False,
        "black_out_nsfw": False,
        "sampler_name": "Default",
        "scheduler_name": "Default",
        "vae_name": "Default (model)",
        "clip_skip": 2,
        "adm_scaler_positive": 1.5,
        "adm_scaler_negative": 0.8,
        "adm_scaler_end": 0.5,
        "adaptive_cfg": 7.0,
        "save_local": True,
        "preset_name": "demo",
    }
    values.update(overrides)
    return values


class PresetTests(unittest.TestCase):
    def test_setting_keys_cover_sample(self) -> None:
        values = _sample_values()
        missing = [k for k in SETTING_KEYS if k not in values]
        self.assertEqual(missing, [])
        self.assertEqual(len(SETTING_KEYS), 58)
        self.assertEqual(len(IMAGE_KEYS), 6)

    def test_roundtrip_settings(self) -> None:
        values = _sample_values()
        raw = preset_to_json(values, include_images=False, name="demo")
        parsed = parse_preset(raw)
        flat = settings_to_updates(parsed)
        self.assertEqual(flat["prompt"], "a lighthouse")
        self.assertEqual(flat["performance"], "Lightning")
        self.assertEqual(parsed["name"], "demo")
        self.assertNotIn("uov_image", parsed.get("images") or {})

    def test_ui_ordered_zip_roundtrip(self) -> None:
        """Mirrors local/ui.py export: zip(SETTING_KEYS, vals) then reload."""
        values = _sample_values(
            prompt="ordered export",
            performance="Speed",
            styles=["Fooocus Enhance", "Fooocus Sharp"],
            seed=-1,
            adaptive_cfg=3.5,
        )
        ordered = [values[k] for k in SETTING_KEYS]
        rebuilt = {k: v for k, v in zip(SETTING_KEYS, ordered)}
        raw = preset_to_json(rebuilt, include_images=False, name="ordered")
        parsed = parse_preset(raw)
        flat = settings_to_updates(parsed)
        for key in SETTING_KEYS:
            self.assertIn(key, flat)
            if key == "preset_name":
                # Top-level JSON name wins on load (same as UI import).
                self.assertEqual(flat[key], "ordered")
            else:
                self.assertEqual(flat[key], values[key], msg=key)

    def test_include_images_roundtrip(self) -> None:
        img = Image.new("RGB", (8, 8), color=(12, 34, 56))
        values = _sample_values(uov_image=img, ip1_image=img)
        raw = preset_to_json(values, include_images=True, name="with-img")
        data = json.loads(raw)
        self.assertIn("uov_image", data["images"])
        parsed = parse_preset(raw)
        flat = settings_to_updates(parsed)
        self.assertIsInstance(flat["uov_image"], Image.Image)
        self.assertEqual(flat["uov_image"].size, (8, 8))

    def test_file_roundtrip_like_ui(self) -> None:
        values = _sample_values(prompt="file path load", guidance=5.5)
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "my-preset.json"
            path.write_text(
                preset_to_json(values, include_images=False, name="file-demo"),
                encoding="utf-8",
            )
            parsed = parse_preset(path.read_text(encoding="utf-8"))
            flat = settings_to_updates(parsed)
            self.assertEqual(flat["prompt"], "file path load")
            self.assertEqual(flat["guidance"], 5.5)
            self.assertEqual(flat["preset_name"], "file-demo")


if __name__ == "__main__":
    unittest.main()
