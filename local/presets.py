"""Save / load UI presets as JSON (settings only by default; optional images)."""

from __future__ import annotations

import base64
import json
from io import BytesIO
from typing import Any

from PIL import Image

PRESET_VERSION = 1

# Keys stored in the preset JSON (no heavy images unless include_images=True).
SETTING_KEYS = [
    "prompt",
    "negative",
    "styles",
    "performance",
    "aspect",
    "image_number",
    "seed",
    "sharpness",
    "guidance",
    "base_model",
    "refiner_model",
    "refiner_switch",
    "lora1",
    "lora1_w",
    "lora2",
    "lora2_w",
    "lora3",
    "lora3_w",
    "lora4",
    "lora4_w",
    "lora5",
    "lora5_w",
    "input_image_on",
    "uov_method",
    "ip1_type",
    "ip1_stop",
    "ip1_weight",
    "ip2_type",
    "ip2_stop",
    "ip2_weight",
    "ip3_type",
    "ip3_stop",
    "ip3_weight",
    "ip4_type",
    "ip4_stop",
    "ip4_weight",
    "mix_ip_uov",
    "mix_ip_inpaint",
    "inpaint_method",
    "inpaint_prompt",
    "inpaint_strength",
    "inpaint_field",
    "inpaint_engine",
    "inpaint_advanced_masking",
    "invert_mask",
    "inpaint_erode_or_dilate",
    "outpaint",
    "enhance_on",
    "enhance_uov",
    "output_format",
    "read_wildcards",
    "black_out_nsfw",
    "sampler_name",
    "scheduler_name",
    "vae_name",
    "clip_skip",
    "adm_scaler_positive",
    "adm_scaler_negative",
    "adm_scaler_end",
    "adaptive_cfg",
    "save_local",
    "preset_name",
]

IMAGE_KEYS = [
    "uov_image",
    "ip1_image",
    "ip2_image",
    "ip3_image",
    "ip4_image",
    "enhance_image",
]


def _pil_to_b64(img: Image.Image | None) -> str | None:
    if img is None:
        return None
    if not isinstance(img, Image.Image):
        try:
            img = Image.fromarray(img)
        except Exception:
            return None
    buf = BytesIO()
    img.convert("RGB").save(buf, format="PNG")
    return base64.b64encode(buf.getvalue()).decode("ascii")


def _b64_to_pil(data: str | None) -> Image.Image | None:
    if not data:
        return None
    raw = base64.b64decode(data)
    return Image.open(BytesIO(raw)).convert("RGB")


def build_preset(
    values: dict[str, Any],
    *,
    include_images: bool = False,
    name: str = "preset",
) -> dict[str, Any]:
    body: dict[str, Any] = {
        "version": PRESET_VERSION,
        "name": name or values.get("preset_name") or "preset",
        "settings": {},
    }
    settings = body["settings"]
    for key in SETTING_KEYS:
        if key in values:
            settings[key] = values[key]
    if include_images:
        images: dict[str, str] = {}
        for key in IMAGE_KEYS:
            b64 = _pil_to_b64(values.get(key))
            if b64:
                images[key] = b64
        # ImageEditor may be dict-like; skip raw editor state.
        if images:
            body["images"] = images
    return body


def preset_to_json(
    values: dict[str, Any],
    *,
    include_images: bool = False,
    name: str = "preset",
) -> str:
    return json.dumps(
        build_preset(values, include_images=include_images, name=name),
        indent=2,
        ensure_ascii=True,
    )


def parse_preset(raw: str | bytes) -> dict[str, Any]:
    if isinstance(raw, bytes):
        raw = raw.decode("utf-8")
    data = json.loads(raw)
    if not isinstance(data, dict):
        raise ValueError("Preset must be a JSON object")
    settings = data.get("settings")
    if settings is None and "prompt" in data:
        # Flat legacy-style object.
        settings = {k: data[k] for k in SETTING_KEYS if k in data}
        images = {k: data[k] for k in IMAGE_KEYS if k in data}
    else:
        settings = dict(settings or {})
        images = dict(data.get("images") or {})
    return {"name": data.get("name") or settings.get("preset_name") or "preset", "settings": settings, "images": images}


def settings_to_updates(parsed: dict[str, Any]) -> dict[str, Any]:
    """Map parsed preset to control values (including optional images)."""
    out = dict(parsed.get("settings") or {})
    if "name" in parsed and parsed["name"]:
        out["preset_name"] = parsed["name"]
    for key, b64 in (parsed.get("images") or {}).items():
        out[key] = _b64_to_pil(b64)
    return out
