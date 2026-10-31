"""Container-side Fooocus bootstrap — lean serverless init (no Gradio)."""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

FOOOCUS_ROOT = Path(os.environ.get("FOOOCUS_ROOT", "/opt/Fooocus"))

_VAE_APPROX = [
    ("xlvaeapp.pth", "https://huggingface.co/lllyasviel/misc/resolve/main/xlvaeapp.pth"),
    ("vaeapp_sd15.pth", "https://huggingface.co/lllyasviel/misc/resolve/main/vaeapp_sd15.pt"),
    (
        "xl-to-v1_interposer-v4.0.safetensors",
        "https://huggingface.co/mashb1t/misc/resolve/main/xl-to-v1_interposer-v4.0.safetensors",
    ),
]


def _truthy(name: str, default: str = "true") -> bool:
    return os.environ.get(name, default).strip().lower() in {"1", "true", "yes", "on"}


def write_fooocus_config() -> Path:
    from src.paths import ensure_layout, fooocus_config_dict

    ensure_layout()
    config_path = FOOOCUS_ROOT / "config.txt"
    config_path.write_text(json.dumps(fooocus_config_dict(), indent=2), encoding="utf-8")
    return config_path


def prepare_sys_argv() -> None:
    # Minimal flags: headless worker only — no browser, analytics, or preset pulls.
    argv = [
        "launch.py",
        "--disable-analytics",
        "--disable-in-browser",
        "--disable-preset-download",
        "--always-high-vram",
    ]
    if _truthy("ZERO_TELEMETRY", "true"):
        argv.append("--disable-image-log")
        argv.append("--disable-metadata")
    sys.argv = argv


def _ensure_small_assets(config) -> None:
    """Only fetch tiny runtime assets missing from the Volume (skip if present)."""
    if not _truthy("ENSURE_RUNTIME_ASSETS", "true"):
        return
    from modules.model_loader import load_file_from_url

    for file_name, url in _VAE_APPROX:
        dest = Path(config.path_vae_approx) / file_name
        if dest.exists() and dest.stat().st_size > 0:
            continue
        load_file_from_url(url=url, model_dir=config.path_vae_approx, file_name=file_name)

    expansion = Path(config.path_fooocus_expansion) / "pytorch_model.bin"
    if not (expansion.exists() and expansion.stat().st_size > 0):
        load_file_from_url(
            url="https://huggingface.co/lllyasviel/misc/resolve/main/fooocus_expansion.bin",
            model_dir=config.path_fooocus_expansion,
            file_name="pytorch_model.bin",
        )


def init_fooocus() -> None:
    """Wire Fooocus modules without starting Gradio (never import launch.py)."""
    write_fooocus_config()
    prepare_sys_argv()
    os.chdir(FOOOCUS_ROOT)
    if str(FOOOCUS_ROOT) not in sys.path:
        sys.path.insert(0, str(FOOOCUS_ROOT))

    os.environ.setdefault("PYTORCH_ENABLE_MPS_FALLBACK", "1")
    os.environ.setdefault("GRADIO_ANALYTICS_ENABLED", "False")
    # Keep HF/torch quieter and avoid extra hub chatter on cold start.
    os.environ.setdefault("HF_HUB_DISABLE_TELEMETRY", "1")
    os.environ.setdefault("TRANSFORMERS_OFFLINE", "0")

    import args_manager  # noqa: F401
    import modules.config as config

    os.environ["U2NET_HOME"] = config.path_inpaint
    os.environ["GRADIO_TEMP_DIR"] = config.temp_path

    _ensure_small_assets(config)
    config.update_files()

    import shared

    shared.gradio_root = None

    # Starts the daemon worker thread only — no Gradio, no web server.
    import modules.async_worker  # noqa: F401
