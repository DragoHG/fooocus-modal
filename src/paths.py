"""Volume layout and ZERO_TELEMETRY path selection."""

from __future__ import annotations

import os
from pathlib import Path

def vol_root() -> Path:
    return Path(os.environ.get("FOOOCUS_VOL_ROOT", "/vol"))


def ephemeral_root() -> Path:
    return Path(os.environ.get("FOOOCUS_EPHEMERAL_ROOT", "/tmp/fooocus_io"))


MODEL_SUBDIRS = {
    "checkpoint": "models/checkpoints",
    "lora": "models/loras",
    "vae": "models/vae",
    "embedding": "models/embeddings",
    "vae_approx": "models/vae_approx",
    "upscale": "models/upscale_models",
    "inpaint": "models/inpaint",
    "controlnet": "models/controlnet",
    "clip_vision": "models/clip_vision",
    "expansion": "models/prompt_expansion/fooocus_expansion",
    "safety_checker": "models/safety_checker",
    "sam": "models/sam",
}


def zero_telemetry_enabled() -> bool:
    return os.environ.get("ZERO_TELEMETRY", "true").strip().lower() in {
        "1",
        "true",
        "yes",
        "on",
    }


def models_root() -> Path:
    return vol_root() / "models"


def model_dir(kind: str) -> Path:
    if kind not in MODEL_SUBDIRS:
        raise ValueError(f"Unknown model kind: {kind}")
    return vol_root() / MODEL_SUBDIRS[kind]


def io_root() -> Path:
    return ephemeral_root() if zero_telemetry_enabled() else vol_root()


def outputs_dir() -> Path:
    return io_root() / "outputs"


def inputs_dir() -> Path:
    return io_root() / "inputs"


def ensure_layout() -> None:
    for kind in MODEL_SUBDIRS:
        model_dir(kind).mkdir(parents=True, exist_ok=True)
    outputs_dir().mkdir(parents=True, exist_ok=True)
    inputs_dir().mkdir(parents=True, exist_ok=True)
    ephemeral_root().mkdir(parents=True, exist_ok=True)


def fooocus_config_dict() -> dict:
    """Paths written into Fooocus config.txt."""
    out = str(outputs_dir()) + "/"
    return {
        "path_checkpoints": [str(model_dir("checkpoint")) + "/"],
        "path_loras": [str(model_dir("lora")) + "/"],
        "path_embeddings": str(model_dir("embedding")) + "/",
        "path_vae_approx": str(model_dir("vae_approx")) + "/",
        "path_vae": str(model_dir("vae")) + "/",
        "path_upscale_models": str(model_dir("upscale")) + "/",
        "path_inpaint": str(model_dir("inpaint")) + "/",
        "path_controlnet": str(model_dir("controlnet")) + "/",
        "path_clip_vision": str(model_dir("clip_vision")) + "/",
        "path_fooocus_expansion": str(model_dir("expansion")),
        "path_safety_checker": str(model_dir("safety_checker")) + "/",
        "path_sam": str(model_dir("sam")) + "/",
        "path_outputs": out,
        "default_overwrite_backup": False,
    }
