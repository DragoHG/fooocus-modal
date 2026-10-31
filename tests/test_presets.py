"""Preset JSON save/load helpers."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from local.presets import parse_preset, preset_to_json, settings_to_updates  # noqa: E402


class PresetTests(unittest.TestCase):
    def test_roundtrip_settings(self) -> None:
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
        raw = preset_to_json(values, include_images=False, name="demo")
        parsed = parse_preset(raw)
        flat = settings_to_updates(parsed)
        self.assertEqual(flat["prompt"], "a lighthouse")
        self.assertEqual(flat["performance"], "Lightning")
        self.assertEqual(parsed["name"], "demo")
        self.assertNotIn("uov_image", parsed.get("images") or {})


if __name__ == "__main__":
    unittest.main()
