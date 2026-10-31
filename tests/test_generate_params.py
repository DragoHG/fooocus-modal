"""Unit tests for GenerateParams schema (no Modal / Fooocus required)."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.generate_params import (  # noqa: E402
    GenerateParams,
    GenerateResult,
    ImagePromptSlot,
    LoraSpec,
)


class GenerateParamsTests(unittest.TestCase):
    def test_defaults_finops_friendly(self) -> None:
        p = GenerateParams(prompt="a cat")
        self.assertEqual(p.performance, "Lightning")
        self.assertEqual(p.base_model, "juggernautXL_v8Rundiffusion.safetensors")
        self.assertFalse(p.input_image_checkbox)
        self.assertEqual(p.current_tab, "uov")

    def test_roundtrip_txt2img(self) -> None:
        p = GenerateParams(
            prompt="portrait",
            negative_prompt="blur",
            performance="Lightning",
            aspect_ratio="1024*1024",
            image_number=1,
            seed=42,
            loras=[LoraSpec(True, "sd_xl_offset_example-lora_1.0.safetensors", 0.1)],
        )
        restored = GenerateParams.from_dict(p.to_dict())
        self.assertEqual(restored.prompt, "portrait")
        self.assertEqual(restored.seed, 42)
        self.assertEqual(len(restored.loras), 1)
        self.assertEqual(restored.loras[0].weight, 0.1)

    def test_roundtrip_image_prompt_faceswap(self) -> None:
        p = GenerateParams(
            prompt="",
            input_image_checkbox=True,
            current_tab="ip",
            image_prompts=[
                ImagePromptSlot(image_b64="AAAA", stop=0.9, weight=0.85, type="FaceSwap"),
                ImagePromptSlot(type="ImagePrompt"),
            ],
        )
        restored = GenerateParams.from_dict(p.to_dict())
        self.assertTrue(restored.input_image_checkbox)
        self.assertEqual(restored.current_tab, "ip")
        self.assertEqual(restored.image_prompts[0].type, "FaceSwap")
        self.assertEqual(restored.image_prompts[0].image_b64, "AAAA")

    def test_roundtrip_uov_and_inpaint(self) -> None:
        p = GenerateParams(
            prompt="fix",
            input_image_checkbox=True,
            current_tab="inpaint",
            uov_method="Vary (Subtle)",
            uov_image_b64="BBB",
            inpaint_image_b64="CCC",
            inpaint_mask_b64="DDD",
            outpaint_selections=["Left", "Right"],
            inpaint_strength=0.8,
            enhance_checkbox=True,
            enhance_image_b64="EEE",
            enhance_uov_method="Upscale (Fast 2x)",
        )
        restored = GenerateParams.from_dict(p.to_dict())
        self.assertEqual(restored.uov_method, "Vary (Subtle)")
        self.assertEqual(restored.outpaint_selections, ["Left", "Right"])
        self.assertEqual(restored.inpaint_strength, 0.8)
        self.assertTrue(restored.enhance_checkbox)
        self.assertEqual(restored.enhance_uov_method, "Upscale (Fast 2x)")

    def test_from_dict_ignores_unknown_keys(self) -> None:
        p = GenerateParams.from_dict({"prompt": "x", "not_a_field": 123})
        self.assertEqual(p.prompt, "x")

    def test_generate_result_shape(self) -> None:
        r = GenerateResult(images=[b"PNG"], seed=1, elapsed_sec=0.5, gpu_name="L4")
        self.assertEqual(len(r.images), 1)
        self.assertEqual(r.gpu_name, "L4")


if __name__ == "__main__":
    unittest.main()
