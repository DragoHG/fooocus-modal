"""Shared generation request/response schema."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass
class LoraSpec:
    enabled: bool = True
    name: str = "None"
    weight: float = 1.0


@dataclass
class GenerateParams:
    prompt: str
    negative_prompt: str = ""
    styles: list[str] = field(
        default_factory=lambda: ["Fooocus V2", "Fooocus Enhance", "Fooocus Sharp"]
    )
    performance: str = "Speed"
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

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        return data

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "GenerateParams":
        raw_loras = data.get("loras") or []
        loras = [
            LoraSpec(**lora) if isinstance(lora, dict) else LoraSpec(*lora)
            for lora in raw_loras
        ]
        payload = dict(data)
        payload["loras"] = loras
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
