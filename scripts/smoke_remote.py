#!/usr/bin/env python3
"""Remote smoke tests against the deployed FooocusWorker (costs GPU time).

Runs list_assets plus one generation per major Input Image mode:
  txt2img, uov/vary, image prompt (FaceSwap), inpaint, outpaint, enhance.

Usage (from repo root, with Modal token + deployed app):

  .venv/bin/python scripts/smoke_remote.py
"""

from __future__ import annotations

import base64
import os
import sys
import time
from io import BytesIO
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from dotenv import load_dotenv
from PIL import Image, ImageDraw

load_dotenv(ROOT / ".env")

APP_NAME = os.environ.get("MODAL_APP_NAME", "fooocus-modal")
OUT = ROOT / "outputs" / "smoke"
CKPT = "juggernautXL_v8Rundiffusion.safetensors"
LORA = "sd_xl_offset_example-lora_1.0.safetensors"


def _tiny_png_b64(color: tuple[int, int, int] = (180, 140, 120), size: int = 512) -> str:
    img = Image.new("RGB", (size, size), color)
    draw = ImageDraw.Draw(img)
    draw.ellipse((size // 4, size // 5, 3 * size // 4, 3 * size // 5), fill=(220, 190, 170))
    draw.ellipse((size // 3, size // 3, size // 3 + 30, size // 3 + 30), fill=(40, 40, 40))
    draw.ellipse((2 * size // 3 - 30, size // 3, 2 * size // 3, size // 3 + 30), fill=(40, 40, 40))
    buf = BytesIO()
    img.save(buf, format="PNG")
    return base64.b64encode(buf.getvalue()).decode("ascii")


def _mask_b64(size: int = 512) -> str:
    mask = Image.new("RGB", (size, size), (0, 0, 0))
    draw = ImageDraw.Draw(mask)
    draw.rectangle((size // 4, size // 4, 3 * size // 4, 3 * size // 4), fill=(255, 255, 255))
    buf = BytesIO()
    mask.save(buf, format="PNG")
    return base64.b64encode(buf.getvalue()).decode("ascii")


def _base_params(**overrides) -> dict:
    data = {
        "prompt": "a simple studio photo of a ceramic mug, soft light",
        "negative_prompt": "blurry, low quality",
        "styles": ["Fooocus V2"],
        "performance": "Lightning",
        "aspect_ratio": "1024*1024",
        "image_number": 1,
        "output_format": "png",
        "seed": 12345,
        "sharpness": 2.0,
        "guidance_scale": 4.0,
        "base_model": CKPT,
        "refiner_model": "None",
        "loras": [{"enabled": True, "name": LORA, "weight": 0.1}],
        "input_image_checkbox": False,
        "current_tab": "uov",
    }
    data.update(overrides)
    return data


def _save_images(case: str, payload: dict) -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    images = payload.get("images_b64") or []
    for i, b64 in enumerate(images):
        path = OUT / f"{case}_{i}.png"
        path.write_bytes(base64.b64decode(b64))
    return len(images)


def main() -> int:
    import modal

    worker = modal.Cls.from_name(APP_NAME, "FooocusWorker")()
    report: list[tuple[str, str, float]] = []

    print("== list_assets (CPU) ==", flush=True)
    t0 = time.perf_counter()
    assets = modal.Function.from_name(APP_NAME, "list_assets").remote()
    elapsed = time.perf_counter() - t0
    ckpts = assets.get("checkpoints") or []
    print(
        f"checkpoints={len(ckpts)} loras={len(assets.get('loras') or [])} "
        f"controlnet={len(assets.get('controlnet') or [])} ({elapsed:.1f}s)",
        flush=True,
    )
    if CKPT not in ckpts:
        print(f"FAIL: missing checkpoint {CKPT} on Volume; run sync first", flush=True)
        return 1
    report.append(("list_assets", "ok", elapsed))

    cases: list[tuple[str, dict]] = [
        (
            "txt2img",
            _base_params(),
        ),
        (
            "uov_vary",
            _base_params(
                prompt="same scene, subtle variation",
                input_image_checkbox=True,
                current_tab="uov",
                uov_method="Vary (Subtle)",
                uov_image_b64=_tiny_png_b64(),
            ),
        ),
        (
            "ip_faceswap",
            _base_params(
                prompt="professional headshot, soft light",
                input_image_checkbox=True,
                current_tab="ip",
                image_prompts=[
                    {
                        "image_b64": _tiny_png_b64((200, 160, 140)),
                        "stop": 0.9,
                        "weight": 0.85,
                        "type": "FaceSwap",
                    }
                ],
            ),
        ),
        (
            "inpaint",
            _base_params(
                prompt="a red apple on the table",
                input_image_checkbox=True,
                current_tab="inpaint",
                inpaint_image_b64=_tiny_png_b64((90, 90, 90)),
                inpaint_mask_b64=_mask_b64(),
                inpaint_additional_prompt="red apple",
                inpaint_strength=1.0,
            ),
        ),
        (
            "outpaint",
            _base_params(
                prompt="wider scene, soft daylight",
                input_image_checkbox=True,
                current_tab="inpaint",
                inpaint_image_b64=_tiny_png_b64((110, 130, 150)),
                outpaint_selections=["Left", "Right"],
            ),
        ),
        (
            "enhance",
            _base_params(
                prompt="enhance detail",
                input_image_checkbox=True,
                current_tab="enhance",
                enhance_checkbox=True,
                enhance_image_b64=_tiny_png_b64((150, 150, 160)),
                enhance_uov_method="Upscale (Fast 2x)",
            ),
        ),
    ]

    failed = 0
    for name, params in cases:
        print(f"== generate:{name} ==")
        t0 = time.perf_counter()
        try:
            result = worker.generate.remote(params)
            elapsed = time.perf_counter() - t0
            n = _save_images(name, result)
            meta = result.get("meta") or {}
            gpu = result.get("gpu_name") or "?"
            seed = result.get("seed")
            if n < 1:
                print(f"FAIL {name}: no images (gpu={gpu} seed={seed})")
                failed += 1
                report.append((name, "no_images", elapsed))
            else:
                print(
                    f"OK {name}: images={n} seed={seed} gpu={gpu} "
                    f"elapsed={elapsed:.1f}s meta_tab={meta.get('tab')}"
                )
                report.append((name, "ok", elapsed))
        except Exception as exc:  # noqa: BLE001
            elapsed = time.perf_counter() - t0
            print(f"FAIL {name}: {exc}")
            failed += 1
            report.append((name, f"error:{type(exc).__name__}", elapsed))

    print("\n== summary ==")
    for name, status, elapsed in report:
        print(f"{status:12} {name:12} {elapsed:7.1f}s")
    print(f"artifacts: {OUT}")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
