"""Shared generation request/response schema (Fooocus-parity controls)."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass
class LoraSpec:
    enabled: bool = True
    name: str = "None"
    weight: float = 1.0


@dataclass
class ImagePromptSlot:
    """One Image Prompt / FaceSwap / Canny / CPDS slot."""

    image_b64: str | None = None
    stop: float = 0.5
    weight: float = 0.6
    type: str = "ImagePrompt"  # ImagePrompt | FaceSwap | PyraCanny | CPDS


@dataclass
class GenerateParams:
    prompt: str
    negative_prompt: str = ""
    styles: list[str] = field(
        default_factory=lambda: ["Fooocus V2", "Fooocus Enhance", "Fooocus Sharp"]
    )
    performance: str = "Lightning"
    aspect_ratio: str = "1152*896"
    image_number: int = 1
    output_format: str = "png"
    seed: int = -1
    sharpness: float = 2.0
    guidance_scale: float = 4.0
    base_model: str = "juggernautXL_v8Rundiffusion.safetensors"
    refiner_model: str = "None"
    refiner_switch: float = 0.5
    loras: list[LoraSpec] = field(default_factory=list)
    read_wildcards_in_order: bool = False

    # Input Image panel
    input_image_checkbox: bool = False
    current_tab: str = "uov"  # uov | ip | inpaint | enhance

    # Upscale or Variation (i2i vary/upscale)
    uov_method: str = "Disabled"
    uov_image_b64: str | None = None

    # Outpaint / Inpaint
    outpaint_selections: list[str] = field(default_factory=list)
    inpaint_image_b64: str | None = None
    inpaint_mask_b64: str | None = None
    inpaint_additional_prompt: str = ""
    inpaint_strength: float = 1.0
    inpaint_respective_field: float = 0.618
    inpaint_engine: str = "v2.6"

    # Image Prompt slots (FaceSwap, ImagePrompt, PyraCanny, CPDS)
    image_prompts: list[ImagePromptSlot] = field(default_factory=list)
    mixing_image_prompt_and_vary_upscale: bool = False
    mixing_image_prompt_and_inpaint: bool = False

    # Enhance (simplified entry)
    enhance_checkbox: bool = False
    enhance_image_b64: str | None = None
    enhance_uov_method: str = "Disabled"

    # Advanced sampling overrides
    sampler_name: str | None = None
    scheduler_name: str | None = None
    vae_name: str | None = None
    clip_skip: int | None = None
    adm_scaler_positive: float = 1.5
    adm_scaler_negative: float = 0.8
    adm_scaler_end: float = 0.5
    adaptive_cfg: float | None = None
    black_out_nsfw: bool = False

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "GenerateParams":
        payload = dict(data)
        raw_loras = payload.get("loras") or []
        payload["loras"] = [
            LoraSpec(**lora) if isinstance(lora, dict) else LoraSpec(*lora)
            for lora in raw_loras
        ]
        raw_ips = payload.get("image_prompts") or []
        payload["image_prompts"] = [
            ImagePromptSlot(**ip) if isinstance(ip, dict) else ImagePromptSlot(*ip)
            for ip in raw_ips
        ]
        known = {f.name for f in cls.__dataclass_fields__.values()}  # type: ignore[attr-defined]
        return cls(**{k: v for k, v in payload.items() if k in known})


@dataclass
class GenerateResult:
    images: list[bytes]
    seed: int
    elapsed_sec: float
    gpu_name: str = ""
    paths: list[str] = field(default_factory=list)
    meta: dict[str, Any] = field(default_factory=dict)
