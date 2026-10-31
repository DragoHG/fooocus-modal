"""Container-side Fooocus bootstrap - lean serverless init (no Gradio)."""

from __future__ import annotations

import json
import os
import shutil
import sys
import threading
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

# Tokenizer / config sidecars ship in the Fooocus git tree; weights are synced separately.
_EXPANSION_SIDECARS = (
    "config.json",
    "tokenizer_config.json",
    "tokenizer.json",
    "vocab.json",
    "merges.txt",
    "special_tokens_map.json",
    "positive.txt",
)

_modules_ready = False
_worker_started = False


def _truthy(name: str, default: str = "true") -> bool:
    return os.environ.get(name, default).strip().lower() in {"1", "true", "yes", "on"}


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
    if _truthy("ZERO_TELEMETRY", "true"):
        argv.append("--disable-image-log")
        argv.append("--disable-metadata")
    sys.argv = argv


def _ensure_small_assets(config) -> None:
    """Fetch/copy tiny runtime assets missing from the Volume."""
    if not _truthy("ENSURE_RUNTIME_ASSETS", "true"):
        return
    from modules.model_loader import load_file_from_url

    for file_name, url in _VAE_APPROX:
        dest = Path(config.path_vae_approx) / file_name
        if dest.exists() and dest.stat().st_size > 0:
            continue
        load_file_from_url(url=url, model_dir=config.path_vae_approx, file_name=file_name)

    expansion_dir = Path(config.path_fooocus_expansion)
    expansion_dir.mkdir(parents=True, exist_ok=True)
    bundled = FOOOCUS_ROOT / "models" / "prompt_expansion" / "fooocus_expansion"
    for name in _EXPANSION_SIDECARS:
        dest = expansion_dir / name
        if dest.exists() and dest.stat().st_size > 0:
            continue
        src = bundled / name
        if src.exists():
            shutil.copy2(src, dest)

    weights = expansion_dir / "pytorch_model.bin"
    if not (weights.exists() and weights.stat().st_size > 0):
        load_file_from_url(
            url="https://huggingface.co/lllyasviel/misc/resolve/main/fooocus_expansion.bin",
            model_dir=str(expansion_dir),
            file_name="pytorch_model.bin",
        )

    if not (expansion_dir / "config.json").exists():
        raise FileNotFoundError(
            f"Fooocus expansion tokenizer missing under {expansion_dir} "
            "(need config.json + tokenizer files from the Fooocus tree)."
        )


def init_fooocus_modules() -> None:
    """Load Fooocus modules and config. Does NOT start the async worker thread."""
    global _modules_ready
    if _modules_ready:
        return

    write_fooocus_config()
    prepare_sys_argv()
    os.chdir(FOOOCUS_ROOT)
    if str(FOOOCUS_ROOT) not in sys.path:
        sys.path.insert(0, str(FOOOCUS_ROOT))

    os.environ.setdefault("PYTORCH_ENABLE_MPS_FALLBACK", "1")
    os.environ.setdefault("GRADIO_ANALYTICS_ENABLED", "False")
    os.environ.setdefault("HF_HUB_DISABLE_TELEMETRY", "1")
    os.environ.setdefault("TRANSFORMERS_OFFLINE", "0")

    import args_manager  # noqa: F401
    import modules.config as config

    os.environ["U2NET_HOME"] = config.path_inpaint
    os.environ["GRADIO_TEMP_DIR"] = config.temp_path

    _ensure_small_assets(config)
    config.update_files()

    import shared

    # Headless stub so Fooocus worker startup does not crash on shared.gradio_root.local_url.
    class _HeadlessApp:
        local_url = "http://127.0.0.1:0"
        server_name = "127.0.0.1"
        server_port = 0
        share = False
        share_url = None

    shared.gradio_root = _HeadlessApp()
    _modules_ready = True


def start_fooocus_worker() -> None:
    """Start Fooocus AsyncTask consumer thread (must run after snapshot restore)."""
    global _worker_started
    if _worker_started:
        return
    if not _modules_ready:
        init_fooocus_modules()

    import modules.async_worker as async_worker

    # If a previous import already started a live thread, reuse it.
    existing = getattr(async_worker, "worker_thread", None)
    if existing is not None and existing.is_alive():
        _worker_started = True
        return

    _orig_thread = threading.Thread
    held: dict[str, threading.Thread] = {}

    class _CaptureThread(_orig_thread):  # type: ignore[valid-type,misc]
        def start(self):  # type: ignore[no-untyped-def]
            held["worker"] = self
            return _orig_thread.start(self)

    # Importing async_worker executes Thread(...).start() at module bottom.
    # If already imported with a dead thread after snapshot restore, start a fresh one.
    threading.Thread = _CaptureThread  # type: ignore[misc]
    try:
        if "modules.async_worker" in sys.modules and getattr(
            async_worker, "worker_thread", None
        ) is not None:
            # Module already imported; start another consumer explicitly.
            t = _CaptureThread(target=async_worker.worker, daemon=True)
            t.start()
        else:
            import importlib

            if "modules.async_worker" in sys.modules:
                importlib.reload(async_worker)
            else:
                import modules.async_worker as async_worker  # noqa: F811
    finally:
        threading.Thread = _orig_thread  # type: ignore[misc]

    thread = held.get("worker") or getattr(async_worker, "worker_thread", None)
    if thread is None:
        # Last resort: start manually.
        thread = threading.Thread(target=async_worker.worker, daemon=True)
        thread.start()
    async_worker.worker_thread = thread
    if not thread.is_alive():
        raise RuntimeError("Fooocus worker thread failed to start")
    _worker_started = True


def init_fooocus() -> None:
    """Full init for non-snapshot mode: modules + worker thread."""
    init_fooocus_modules()
    start_fooocus_worker()
