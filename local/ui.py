"""Local Gradio UI that calls the Modal FooocusWorker on demand."""

from __future__ import annotations

import base64
import os
import time
from io import BytesIO
from pathlib import Path

import gradio as gr
from dotenv import load_dotenv
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
load_dotenv(ROOT / ".env")

APP_NAME = os.environ.get("MODAL_APP_NAME", "fooocus-modal")
HOST = os.environ.get("LOCAL_UI_HOST", "127.0.0.1")
PORT = int(os.environ.get("LOCAL_UI_PORT", "7860"))
OUTPUT_DIR = Path(os.environ.get("LOCAL_OUTPUT_DIR", ROOT / "outputs"))

ASPECT_CHOICES = [
    "704*1408",
    "704*1344",
    "768*1344",
    "768*1280",
    "832*1216",
    "832*1152",
    "896*1152",
    "896*1088",
    "960*1088",
    "960*1024",
    "1024*1024",
    "1024*960",
    "1088*960",
    "1088*896",
    "1152*896",
    "1152*832",
    "1216*832",
    "1280*768",
    "1344*768",
    "1344*704",
    "1408*704",
    "1472*704",
    "1536*640",
    "1600*640",
    "1664*576",
    "1728*576",
]

PERF_CHOICES = ["Quality", "Speed", "Extreme Speed", "Lightning", "Hyper-SD"]
STYLE_DEFAULT = ["Fooocus V2", "Fooocus Enhance", "Fooocus Sharp"]


def _worker():
    import modal

    return modal.Cls.from_name(APP_NAME, "FooocusWorker")()


def list_remote_assets() -> tuple[list[str], list[str]]:
    try:
        assets = _worker().list_assets.remote()
        checkpoints = assets.get("checkpoints") or [
            "juggernautXL_v8Rundiffusion.safetensors"
        ]
        loras = ["None"] + (assets.get("loras") or [])
        return checkpoints, loras
    except Exception as exc:  # noqa: BLE001
        print(f"[warn] list_assets failed: {exc}")
        return ["juggernautXL_v8Rundiffusion.safetensors"], ["None"]


def generate(
    prompt: str,
    negative: str,
    styles: list[str],
    performance: str,
    aspect: str,
    image_number: int,
    seed: int,
    sharpness: float,
    guidance: float,
    base_model: str,
    refiner_model: str,
    refiner_switch: float,
    lora1: str,
    lora1_w: float,
    lora2: str,
    lora2_w: float,
    save_local: bool,
    progress=gr.Progress(track_tqdm=False),
):
    if not prompt or not prompt.strip():
        raise gr.Error("Prompt is required.")

    progress(0.05, desc="Contacting Modal worker (cold start possible)...")
    started = time.perf_counter()

    loras = []
    for name, weight in ((lora1, lora1_w), (lora2, lora2_w)):
        if name and name != "None":
            loras.append({"enabled": True, "name": name, "weight": float(weight)})

    payload = {
        "prompt": prompt,
        "negative_prompt": negative or "",
        "styles": styles or STYLE_DEFAULT,
        "performance": performance,
        "aspect_ratio": aspect,
        "image_number": int(image_number),
        "seed": int(seed),
        "sharpness": float(sharpness),
        "guidance_scale": float(guidance),
        "base_model": base_model,
        "refiner_model": refiner_model or "None",
        "refiner_switch": float(refiner_switch),
        "loras": loras,
        "output_format": "png",
    }

    progress(0.15, desc="Generating on Modal GPU...")
    result = _worker().generate.remote(payload)
    images_b64 = result.get("images_b64") or []
    if not images_b64:
        raise gr.Error("Worker returned no images.")

    images: list[Image.Image] = []
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    for idx, b64 in enumerate(images_b64):
        raw = base64.b64decode(b64)
        img = Image.open(BytesIO(raw)).convert("RGB")
        images.append(img)
        if save_local:
            stamp = int(time.time())
            path = OUTPUT_DIR / f"{stamp}_{result.get('seed', 0)}_{idx}.png"
            path.write_bytes(raw)

    elapsed = time.perf_counter() - started
    info = (
        f"seed={result.get('seed')} · "
        f"gpu={result.get('gpu_name') or 'n/a'} · "
        f"worker={result.get('elapsed_sec', 0):.1f}s · "
        f"roundtrip={elapsed:.1f}s"
    )
    progress(1.0, desc="Done")
    return images, info


def build_ui() -> gr.Blocks:
    checkpoints, loras = list_remote_assets()
    with gr.Blocks(title="fooocus-modal") as demo:
        gr.Markdown(
            "# fooocus-modal\n"
            "Local UI → on-demand Modal GPU. Idle worker scales to zero."
        )
        with gr.Row():
            with gr.Column(scale=3):
                prompt = gr.Textbox(label="Prompt", lines=3)
                negative = gr.Textbox(label="Negative prompt", lines=2)
                styles = gr.Dropdown(
                    choices=STYLE_DEFAULT
                    + [
                        "Fooocus Masterpiece",
                        "Fooocus Photograph",
                        "Fooocus Cinematic",
                        "SAI Photographic",
                    ],
                    value=STYLE_DEFAULT,
                    multiselect=True,
                    label="Styles",
                )
                with gr.Row():
                    performance = gr.Dropdown(
                        PERF_CHOICES, value="Speed", label="Performance"
                    )
                    aspect = gr.Dropdown(
                        ASPECT_CHOICES, value="1152*896", label="Aspect ratio"
                    )
                    image_number = gr.Slider(1, 4, value=1, step=1, label="Images")
                with gr.Row():
                    seed = gr.Number(value=-1, precision=0, label="Seed (-1 random)")
                    sharpness = gr.Slider(0, 30, value=2.0, step=0.1, label="Sharpness")
                    guidance = gr.Slider(1, 30, value=4.0, step=0.1, label="Guidance")
                with gr.Row():
                    base_model = gr.Dropdown(
                        checkpoints, value=checkpoints[0], label="Checkpoint"
                    )
                    refiner_model = gr.Dropdown(
                        ["None"] + checkpoints, value="None", label="Refiner"
                    )
                    refiner_switch = gr.Slider(
                        0.1, 1.0, value=0.5, step=0.01, label="Refiner switch"
                    )
                with gr.Row():
                    lora1 = gr.Dropdown(loras, value="None", label="LoRA 1")
                    lora1_w = gr.Slider(-2, 2, value=1.0, step=0.05, label="LoRA 1 weight")
                with gr.Row():
                    lora2 = gr.Dropdown(loras, value="None", label="LoRA 2")
                    lora2_w = gr.Slider(-2, 2, value=1.0, step=0.05, label="LoRA 2 weight")
                save_local = gr.Checkbox(value=True, label=f"Save to {OUTPUT_DIR}")
                refresh = gr.Button("Refresh models from Volume")
                go = gr.Button("Generate", variant="primary")
            with gr.Column(scale=2):
                gallery = gr.Gallery(label="Results", columns=2, height=640)
                status = gr.Textbox(label="Status", interactive=False)

        def _refresh():
            ckpts, lora_names = list_remote_assets()
            return (
                gr.update(choices=ckpts, value=ckpts[0]),
                gr.update(choices=["None"] + ckpts, value="None"),
                gr.update(choices=lora_names, value="None"),
                gr.update(choices=lora_names, value="None"),
            )

        refresh.click(
            _refresh,
            outputs=[base_model, refiner_model, lora1, lora2],
        )
        go.click(
            generate,
            inputs=[
                prompt,
                negative,
                styles,
                performance,
                aspect,
                image_number,
                seed,
                sharpness,
                guidance,
                base_model,
                refiner_model,
                refiner_switch,
                lora1,
                lora1_w,
                lora2,
                lora2_w,
                save_local,
            ],
            outputs=[gallery, status],
        )
    return demo


def main() -> None:
    demo = build_ui()
    demo.queue().launch(server_name=HOST, server_port=PORT, share=False)


if __name__ == "__main__":
    main()
