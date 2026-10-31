"""Container-side Fooocus bootstrap (runs inside Modal)."""

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


def write_fooocus_config() -> Path:
    from src.paths import ensure_layout, fooocus_config_dict

    ensure_layout()
    config_path = FOOOCUS_ROOT / "config.txt"
    config_path.write_text(json.dumps(fooocus_config_dict(), indent=2), encoding="utf-8")
    return config_path


def prepare_sys_argv() -> None:
    argv = [
        "launch.py",
        "--disable-analytics",
        "--disable-in-browser",
        "--disable-preset-download",
        "--always-high-vram",
    ]
    if os.environ.get("ZERO_TELEMETRY", "true").strip().lower() in {
        "1",
        "true",
        "yes",
        "on",
    }:
        argv.append("--disable-image-log")
        argv.append("--disable-metadata")
    sys.argv = argv


def _ensure_small_assets(config) -> None:
    from modules.model_loader import load_file_from_url

    for file_name, url in _VAE_APPROX:
        load_file_from_url(url=url, model_dir=config.path_vae_approx, file_name=file_name)
    load_file_from_url(
        url="https://huggingface.co/lllyasviel/misc/resolve/main/fooocus_expansion.bin",
        model_dir=config.path_fooocus_expansion,
        file_name="pytorch_model.bin",
    )


def init_fooocus() -> None:
    """Wire Fooocus modules without starting Gradio (do not import launch.py)."""
    write_fooocus_config()
    prepare_sys_argv()
    os.chdir(FOOOCUS_ROOT)
    if str(FOOOCUS_ROOT) not in sys.path:
        sys.path.insert(0, str(FOOOCUS_ROOT))

    os.environ.setdefault("PYTORCH_ENABLE_MPS_FALLBACK", "1")
    os.environ.setdefault("GRADIO_ANALYTICS_ENABLED", "False")

    import args_manager  # noqa: F401  # parses sys.argv
    import modules.config as config

    os.environ["U2NET_HOME"] = config.path_inpaint
    os.environ["GRADIO_TEMP_DIR"] = config.temp_path

    _ensure_small_assets(config)
    config.update_files()

    import shared

    shared.gradio_root = None

    import modules.async_worker  # noqa: F401  # starts daemon worker thread
