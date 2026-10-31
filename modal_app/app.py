"""Modal app: lean FinOps Fooocus worker + model sync."""

from __future__ import annotations

import base64
import os
from pathlib import Path

import modal

ROOT = Path(__file__).resolve().parent.parent

try:
    from dotenv import load_dotenv

    load_dotenv(ROOT / ".env")
except Exception:
    pass


def _truthy(name: str, default: str = "false") -> bool:
    return os.environ.get(name, default).strip().lower() in {"1", "true", "yes", "on"}


APP_NAME = os.environ.get("MODAL_APP_NAME", "fooocus-modal")
VOLUME_NAME = os.environ.get("VOLUME_NAME", "fooocus-modal-data")
FOOOCUS_REPO = os.environ.get("FOOOCUS_REPO", "https://github.com/lllyasviel/Fooocus.git")
FOOOCUS_REF = os.environ.get("FOOOCUS_REF", "main")
SCALEDOWN_WINDOW = int(os.environ.get("SCALEDOWN_WINDOW", "60"))
MODAL_GPUS = [
    g.strip() for g in os.environ.get("MODAL_GPUS", "L4,A10").split(",") if g.strip()
]
ZERO_TELEMETRY = os.environ.get("ZERO_TELEMETRY", "true")
ENABLE_MEMORY_SNAPSHOT = _truthy("ENABLE_MEMORY_SNAPSHOT", "true")
ENABLE_GPU_SNAPSHOT = _truthy("ENSURE_GPU_SNAPSHOT", "false") or _truthy(
    "ENABLE_GPU_SNAPSHOT", "false"
)
ENSURE_RUNTIME_ASSETS = os.environ.get("ENSURE_RUNTIME_ASSETS", "true")

app = modal.App(APP_NAME)
volume = modal.Volume.from_name(VOLUME_NAME, create_if_missing=True)

# Lean GPU image: Fooocus + torch only. No Gradio server process on Modal.
fooocus_image = (
    modal.Image.from_registry(
        "nvidia/cuda:12.1.1-cudnn8-runtime-ubuntu22.04",
        add_python="3.10",
    )
    .apt_install(
        "git",
        "git-lfs",
        "wget",
        "curl",
        "aria2",
        "libgl1",
        "libglib2.0-0",
        "libsm6",
        "libxext6",
        "libxrender1",
    )
    .run_commands(
        f"git clone --depth 1 --branch {FOOOCUS_REF} {FOOOCUS_REPO} /opt/Fooocus",
        "pip install -r /opt/Fooocus/requirements_versions.txt",
    )
    .env(
        {
            "FOOOCUS_ROOT": "/opt/Fooocus",
            "PYTHONPATH": "/app",
            "ZERO_TELEMETRY": ZERO_TELEMETRY,
            "FOOOCUS_VOL_ROOT": "/vol",
            "ENSURE_RUNTIME_ASSETS": ENSURE_RUNTIME_ASSETS,
            "HF_HUB_DISABLE_TELEMETRY": "1",
            "GRADIO_ANALYTICS_ENABLED": "False",
        }
    )
    .add_local_dir(str(ROOT / "src"), remote_path="/app/src")
    .add_local_dir(str(ROOT / "modal_app"), remote_path="/app/modal_app")
)

cpu_image = (
    modal.Image.debian_slim(python_version="3.10")
    .apt_install("aria2", "curl", "ca-certificates")
    .pip_install("python-dotenv")
    .env(
        {
            "PYTHONPATH": "/app",
            "ZERO_TELEMETRY": ZERO_TELEMETRY,
            "FOOOCUS_VOL_ROOT": "/vol",
        }
    )
    .add_local_dir(str(ROOT / "src"), remote_path="/app/src")
)


@app.function(
    image=cpu_image,
    volumes={"/vol": volume},
    timeout=60 * 60,
)
def sync_models(manifest_text: str) -> list[dict]:
    from src.manifest import parse_manifest, sync_entries

    entries = parse_manifest(manifest_text)
    report = sync_entries(entries)
    volume.commit()
    return report


_cls_kwargs: dict = {
    "image": fooocus_image,
    "gpu": MODAL_GPUS or ["L4", "A10"],
    "volumes": {"/vol": volume},
    "timeout": 60 * 20,
    "scaledown_window": SCALEDOWN_WINDOW,
    "memory": 32768,
    "enable_memory_snapshot": ENABLE_MEMORY_SNAPSHOT,
}
if ENABLE_GPU_SNAPSHOT:
    # Experimental: large SDXL snapshots - off by default; enable via .env if desired.
    _cls_kwargs["experimental_options"] = {"enable_gpu_snapshot": True}


@app.cls(**_cls_kwargs)
class FooocusWorker:
    @modal.enter(snap=ENABLE_MEMORY_SNAPSHOT)
    def setup(self) -> None:
        # When snapshots are on, capture the Fooocus import graph for faster restores.
        # Checkpoints stay on Volume and load lazily on first generate (lean cold path).
        from modal_app.bootstrap import init_fooocus

        init_fooocus()

    @modal.method()
    def list_assets(self) -> dict:
        from src.paths import model_dir

        def _list(kind: str) -> list[str]:
            root = model_dir(kind)
            if not root.exists():
                return []
            names: list[str] = []
            for path in sorted(root.rglob("*")):
                if path.is_file() and path.suffix.lower() in {
                    ".safetensors",
                    ".ckpt",
                    ".pt",
                    ".pth",
                    ".bin",
                }:
                    names.append(str(path.relative_to(root)))
            return names

        return {
            "checkpoints": _list("checkpoint"),
            "loras": _list("lora"),
            "vae": _list("vae"),
            "controlnet": _list("controlnet"),
            "clip_vision": _list("clip_vision"),
            "inpaint": _list("inpaint"),
            "upscale": _list("upscale"),
        }

    @modal.method()
    def generate(self, params: dict) -> dict:
        from src.fooocus_task import run_generation
        from src.generate_params import GenerateParams
        from src.paths import zero_telemetry_enabled

        request = GenerateParams.from_dict(params)
        result = run_generation(request)
        if not zero_telemetry_enabled():
            volume.commit()
        return {
            "images_b64": [base64.b64encode(img).decode("ascii") for img in result.images],
            "seed": result.seed,
            "elapsed_sec": result.elapsed_sec,
            "gpu_name": result.gpu_name,
            "paths": result.paths if not zero_telemetry_enabled() else [],
            "meta": result.meta,
        }


@app.local_entrypoint()
def main(action: str = "sync") -> None:
    if action == "sync":
        manifest = ROOT / "models.txt"
        if not manifest.exists():
            raise SystemExit(
                "models.txt not found. Copy models.txt.example to models.txt and add URLs."
            )
        report = sync_models.remote(manifest.read_text(encoding="utf-8"))
        for row in report:
            print(f"{row['status']:10} {row['kind']:12} {row['path']} ({row['bytes']} bytes)")
        return
    if action == "list":
        print(FooocusWorker().list_assets.remote())
        return
    raise SystemExit(f"Unknown action: {action}")
