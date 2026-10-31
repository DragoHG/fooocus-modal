"""Local Gradio UI - Fooocus-style controls to Modal FooocusWorker."""

from __future__ import annotations

import base64
import os
import sys
import time
from io import BytesIO
from pathlib import Path

import gradio as gr
from dotenv import load_dotenv
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from local.presets import IMAGE_KEYS, SETTING_KEYS, parse_preset, preset_to_json, settings_to_updates  # noqa: E402

load_dotenv(ROOT / ".env")

APP_NAME = os.environ.get("MODAL_APP_NAME", "fooocus-modal")
HOST = os.environ.get("LOCAL_UI_HOST", "127.0.0.1")
PORT = int(os.environ.get("LOCAL_UI_PORT", "7860"))
OUTPUT_DIR = Path(os.environ.get("LOCAL_OUTPUT_DIR", ROOT / "outputs"))
PRESET_DIR = OUTPUT_DIR / "presets"

DEFAULT_CHECKPOINT = "juggernautXL_v8Rundiffusion.safetensors"
DEFAULT_LORA = "sd_xl_offset_example-lora_1.0.safetensors"

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
STYLE_CHOICES = [
    "Fooocus V2",
    "Fooocus Enhance",
    "Fooocus Sharp",
    "Fooocus Masterpiece",
    "Fooocus Photograph",
    "Fooocus Negative",
    "Fooocus Cinematic",
    "SAI Photographic",
    "SAI Digital Art",
    "SAI Enhance",
    "SAI Comic Book",
    "SAI Line Art",
    "SAI Anime",
    "Ads Fashion Editorial",
    "Artstyle Impressionist",
    "Misc Fantasy",
]
STYLE_DEFAULT = ["Fooocus V2", "Fooocus Enhance", "Fooocus Sharp"]
UOV_METHODS = [
    "Disabled",
    "Vary (Subtle)",
    "Vary (Strong)",
    "Upscale (1.5x)",
    "Upscale (2x)",
    "Upscale (Fast 2x)",
]
IP_TYPES = ["ImagePrompt", "FaceSwap", "PyraCanny", "CPDS"]
OUTPAINT_OPTS = ["Left", "Right", "Top", "Bottom"]
OUTPUT_FORMATS = ["png", "jpeg", "webp"]
SAMPLER_CHOICES = [
    "Default",
    "dpmpp_2m_sde_gpu",
    "dpmpp_2m_sde",
    "dpmpp_3m_sde_gpu",
    "dpmpp_2m",
    "dpmpp_sde_gpu",
    "euler",
    "euler_ancestral",
    "ddim",
    "uni_pc",
]
SCHEDULER_CHOICES = ["Default", "karras", "exponential", "sgm_uniform", "simple", "ddim_uniform", "normal"]
VAE_CHOICES = ["Default (model)"]
INPAINT_ENGINES = ["v2.6", "v1"]


def _pil_to_b64(img: Image.Image | None) -> str | None:
    if img is None:
        return None
    if not isinstance(img, Image.Image):
        img = Image.fromarray(img)
    buf = BytesIO()
    img.convert("RGB").save(buf, format="PNG")
    return base64.b64encode(buf.getvalue()).decode("ascii")


def _modal_ready() -> bool:
    try:
        import modal

        cfg = modal.config.Config()
        return bool(cfg.get("token_id") and cfg.get("token_secret"))
    except Exception:
        return False


def _worker():
    import modal

    return modal.Cls.from_name(APP_NAME, "FooocusWorker")()


def list_remote_assets() -> tuple[list[str], list[str]]:
    if not _modal_ready():
        print("[info] Modal token not configured - using local defaults.")
        return [DEFAULT_CHECKPOINT], ["None", DEFAULT_LORA]
    try:
        import modal

        # CPU function on purpose: listing models must not wake a GPU worker.
        assets = modal.Function.from_name(APP_NAME, "list_assets").remote()
        checkpoints = assets.get("checkpoints") or [DEFAULT_CHECKPOINT]
        loras = ["None"] + (assets.get("loras") or [])
        if DEFAULT_LORA not in loras:
            loras.append(DEFAULT_LORA)
        return checkpoints, loras
    except Exception as exc:  # noqa: BLE001
        print(f"[warn] list_assets failed: {exc}")
        return [DEFAULT_CHECKPOINT], ["None", DEFAULT_LORA]


def generate(
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
    lora3,
    lora3_w,
    lora4,
    lora4_w,
    lora5,
    lora5_w,
    input_image_on,
    uov_method,
    uov_image,
    ip1_image,
    ip1_type,
    ip1_stop,
    ip1_weight,
    ip2_image,
    ip2_type,
    ip2_stop,
    ip2_weight,
    ip3_image,
    ip3_type,
    ip3_stop,
    ip3_weight,
    ip4_image,
    ip4_type,
    ip4_stop,
    ip4_weight,
    mix_ip_uov,
    mix_ip_inpaint,
    inpaint_image,
    inpaint_mask,
    inpaint_prompt,
    inpaint_strength,
    inpaint_field,
    inpaint_engine,
    outpaint,
    enhance_on,
    enhance_image,
    enhance_uov,
    output_format,
    read_wildcards,
    black_out_nsfw,
    sampler_name,
    scheduler_name,
    vae_name,
    clip_skip,
    adm_scaler_positive,
    adm_scaler_negative,
    adm_scaler_end,
    adaptive_cfg,
    save_local,
):
    if not prompt or not str(prompt).strip():
        if not input_image_on:
            raise gr.Error("Prompt is required for text-to-image.")

    started = time.perf_counter()
    lora_pairs = [
        (lora1, lora1_w),
        (lora2, lora2_w),
        (lora3, lora3_w),
        (lora4, lora4_w),
        (lora5, lora5_w),
    ]
    loras = []
    for name, weight in lora_pairs:
        if name and name != "None":
            loras.append({"enabled": True, "name": name, "weight": float(weight)})

    image_prompts = []
    for img, typ, stop, weight in (
        (ip1_image, ip1_type, ip1_stop, ip1_weight),
        (ip2_image, ip2_type, ip2_stop, ip2_weight),
        (ip3_image, ip3_type, ip3_stop, ip3_weight),
        (ip4_image, ip4_type, ip4_stop, ip4_weight),
    ):
        b64 = _pil_to_b64(img)
        if b64:
            image_prompts.append(
                {
                    "image_b64": b64,
                    "type": typ,
                    "stop": float(stop),
                    "weight": float(weight),
                }
            )

    current_tab = "uov"
    if image_prompts:
        current_tab = "ip"
    elif inpaint_image is not None or (outpaint and len(outpaint) > 0):
        current_tab = "inpaint"
    elif enhance_on:
        current_tab = "enhance"

    inpaint_img = inpaint_image
    inpaint_msk = None
    if isinstance(inpaint_image, dict):
        inpaint_img = inpaint_image.get("background") or inpaint_image.get("image")
        inpaint_msk = inpaint_image.get("layers")
        if isinstance(inpaint_msk, list) and inpaint_msk:
            inpaint_msk = inpaint_msk[0]
    if inpaint_mask is not None and inpaint_msk is None:
        inpaint_msk = inpaint_mask

    sampler = None if not sampler_name or sampler_name == "Default" else sampler_name
    scheduler = None if not scheduler_name or scheduler_name == "Default" else scheduler_name
    vae = None if not vae_name or vae_name.startswith("Default") else vae_name

    payload = {
        "prompt": prompt or "",
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
        "output_format": output_format or "png",
        "read_wildcards_in_order": bool(read_wildcards),
        "black_out_nsfw": bool(black_out_nsfw),
        "sampler_name": sampler,
        "scheduler_name": scheduler,
        "vae_name": vae,
        "clip_skip": int(clip_skip),
        "adm_scaler_positive": float(adm_scaler_positive),
        "adm_scaler_negative": float(adm_scaler_negative),
        "adm_scaler_end": float(adm_scaler_end),
        "adaptive_cfg": float(adaptive_cfg),
        "input_image_checkbox": bool(input_image_on),
        "current_tab": current_tab,
        "uov_method": uov_method,
        "uov_image_b64": _pil_to_b64(uov_image),
        "outpaint_selections": list(outpaint or []),
        "inpaint_image_b64": _pil_to_b64(inpaint_img) if inpaint_img is not None else None,
        "inpaint_mask_b64": _pil_to_b64(inpaint_msk) if inpaint_msk is not None else None,
        "inpaint_additional_prompt": inpaint_prompt or "",
        "inpaint_strength": float(inpaint_strength),
        "inpaint_respective_field": float(inpaint_field),
        "inpaint_engine": inpaint_engine or "v2.6",
        "image_prompts": image_prompts,
        "mixing_image_prompt_and_vary_upscale": bool(mix_ip_uov),
        "mixing_image_prompt_and_inpaint": bool(mix_ip_inpaint),
        "enhance_checkbox": bool(enhance_on),
        "enhance_image_b64": _pil_to_b64(enhance_image),
        "enhance_uov_method": enhance_uov,
    }

    try:
        result = _worker().generate.remote(payload)
    except Exception as exc:  # noqa: BLE001
        raise gr.Error(f"Generation failed: {exc}") from exc

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
            ext = (output_format or "png").lower()
            if ext == "jpeg":
                ext = "jpg"
            (OUTPUT_DIR / f"{stamp}_{result.get('seed', 0)}_{idx}.{ext}").write_bytes(raw)

    elapsed = time.perf_counter() - started
    info = (
        f"seed={result.get('seed')} · gpu={result.get('gpu_name') or 'n/a'} · "
        f"worker={result.get('elapsed_sec', 0):.1f}s · roundtrip={elapsed:.1f}s · "
        f"mode={result.get('meta', {}).get('tab', 'txt2img')}"
    )
    return images, info


def _ip_block(idx: int):
    with gr.Row():
        image = gr.Image(label=f"Image {idx}", type="pil", height=220)
        with gr.Column():
            typ = gr.Dropdown(
                IP_TYPES, value="ImagePrompt" if idx > 1 else "FaceSwap", label="Type"
            )
            stop = gr.Slider(0, 1, value=0.5, step=0.01, label="Stop At")
            weight = gr.Slider(0, 2, value=0.6 if idx > 1 else 0.75, step=0.01, label="Weight")
    return image, typ, stop, weight


def build_ui() -> gr.Blocks:
    checkpoints, loras = list_remote_assets()
    default_lora = DEFAULT_LORA if DEFAULT_LORA in loras else "None"

    with gr.Blocks(title="fooocus-modal") as demo:
        gr.Markdown(
            "# fooocus-modal\n"
            "Create images from your machine. GPUs run on demand and shut down when idle, "
            "so you pay for work, not waiting. Save your setup as JSON and load it next time."
        )
        with gr.Row():
            with gr.Column(scale=3):
                prompt = gr.Textbox(label="Prompt", lines=3, placeholder="Describe the image")
                negative = gr.Textbox(label="Negative prompt", lines=2)
                styles = gr.Dropdown(
                    STYLE_CHOICES, value=STYLE_DEFAULT, multiselect=True, label="Styles"
                )
                with gr.Row():
                    performance = gr.Dropdown(
                        PERF_CHOICES, value="Lightning", label="Performance"
                    )
                    aspect = gr.Dropdown(ASPECT_CHOICES, value="1152*896", label="Aspect ratio")
                    image_number = gr.Slider(1, 8, value=1, step=1, label="Image count")
                    output_format = gr.Dropdown(
                        OUTPUT_FORMATS, value="png", label="Output format"
                    )
                with gr.Row():
                    seed = gr.Number(value=-1, precision=0, label="Seed (-1 = random)")
                    sharpness = gr.Slider(0, 30, value=2.0, step=0.1, label="Sharpness")
                    guidance = gr.Slider(1, 30, value=4.0, step=0.1, label="Guidance scale")

                with gr.Accordion("Models and LoRAs", open=True):
                    with gr.Row():
                        base_model = gr.Dropdown(
                            checkpoints, value=checkpoints[0], label="Base model"
                        )
                        refiner_model = gr.Dropdown(
                            ["None"] + checkpoints, value="None", label="Refiner"
                        )
                        refiner_switch = gr.Slider(
                            0.1, 1.0, value=0.5, step=0.01, label="Refiner switch"
                        )
                    lora_ctrls = []
                    for i in range(1, 6):
                        with gr.Row():
                            default = default_lora if i == 1 else "None"
                            weight_default = 0.1 if i == 1 and default != "None" else 1.0
                            dd = gr.Dropdown(loras, value=default, label=f"LoRA {i}")
                            ww = gr.Slider(
                                -2, 2, value=weight_default, step=0.05, label=f"Weight {i}"
                            )
                            lora_ctrls.extend([dd, ww])

                with gr.Accordion("Sampling and guidance", open=False):
                    with gr.Row():
                        sampler_name = gr.Dropdown(
                            SAMPLER_CHOICES, value="Default", label="Sampler"
                        )
                        scheduler_name = gr.Dropdown(
                            SCHEDULER_CHOICES, value="Default", label="Scheduler"
                        )
                        vae_name = gr.Dropdown(VAE_CHOICES, value="Default (model)", label="VAE")
                    with gr.Row():
                        clip_skip = gr.Slider(1, 12, value=2, step=1, label="CLIP skip")
                        adaptive_cfg = gr.Slider(
                            0.0, 30.0, value=7.0, step=0.1, label="Adaptive CFG"
                        )
                    with gr.Row():
                        adm_scaler_positive = gr.Slider(
                            0.0, 3.0, value=1.5, step=0.01, label="ADM positive"
                        )
                        adm_scaler_negative = gr.Slider(
                            0.0, 3.0, value=0.8, step=0.01, label="ADM negative"
                        )
                        adm_scaler_end = gr.Slider(
                            0.0, 1.0, value=0.5, step=0.01, label="ADM end"
                        )
                    with gr.Row():
                        read_wildcards = gr.Checkbox(
                            label="Read wildcards in order", value=False
                        )
                        black_out_nsfw = gr.Checkbox(label="Black out NSFW", value=False)

                input_image_on = gr.Checkbox(label="Input Image", value=False)
                with gr.Column(visible=False) as image_panel:
                    with gr.Tab("Upscale or Variation"):
                        uov_method = gr.Dropdown(
                            UOV_METHODS, value="Disabled", label="Method"
                        )
                        uov_image = gr.Image(label="Source image", type="pil", height=320)
                    with gr.Tab("Image Prompt"):
                        gr.Markdown(
                            "Blend reference images: ImagePrompt, FaceSwap, PyraCanny, or CPDS."
                        )
                        ip1_image, ip1_type, ip1_stop, ip1_weight = _ip_block(1)
                        ip2_image, ip2_type, ip2_stop, ip2_weight = _ip_block(2)
                        ip3_image, ip3_type, ip3_stop, ip3_weight = _ip_block(3)
                        ip4_image, ip4_type, ip4_stop, ip4_weight = _ip_block(4)
                        with gr.Row():
                            mix_ip_uov = gr.Checkbox(
                                label="Mix with Upscale / Vary", value=False
                            )
                            mix_ip_inpaint = gr.Checkbox(
                                label="Mix with Inpaint", value=False
                            )
                    with gr.Tab("Inpaint or Outpaint"):
                        inpaint_image = gr.ImageEditor(
                            label="Image and mask", type="pil", height=360
                        )
                        inpaint_mask = gr.Image(
                            label="Extra mask (optional)", type="pil", height=200
                        )
                        inpaint_prompt = gr.Textbox(label="Inpaint additional prompt")
                        with gr.Row():
                            inpaint_strength = gr.Slider(
                                0, 1, value=1.0, step=0.001, label="Inpaint strength"
                            )
                            inpaint_field = gr.Slider(
                                0, 1, value=0.618, step=0.001, label="Respective field"
                            )
                            inpaint_engine = gr.Dropdown(
                                INPAINT_ENGINES, value="v2.6", label="Inpaint engine"
                            )
                        outpaint = gr.CheckboxGroup(
                            OUTPAINT_OPTS, label="Outpaint directions"
                        )
                    with gr.Tab("Enhance"):
                        enhance_on = gr.Checkbox(label="Enable enhance", value=False)
                        enhance_image = gr.Image(
                            label="Enhance image", type="pil", height=320
                        )
                        enhance_uov = gr.Dropdown(
                            UOV_METHODS, value="Disabled", label="Enhance Upscale / Vary"
                        )

                input_image_on.change(
                    lambda on: gr.update(visible=on),
                    inputs=input_image_on,
                    outputs=image_panel,
                )

                with gr.Accordion("Presets (save / load JSON)", open=True):
                    gr.Markdown(
                        "Download your current settings as JSON. Upload the file later to "
                        "restore them. Images are optional (makes the file larger)."
                    )
                    with gr.Row():
                        preset_name = gr.Textbox(value="my-preset", label="Preset name")
                        include_images = gr.Checkbox(
                            label="Include images in JSON", value=False
                        )
                    with gr.Row():
                        save_preset_btn = gr.Button("Download preset JSON")
                        load_preset_file = gr.File(
                            label="Upload preset JSON",
                            file_types=[".json"],
                            type="filepath",
                        )
                    preset_file_out = gr.File(label="Preset download", visible=True)
                    preset_status = gr.Textbox(label="Preset status", interactive=False)

                save_local = gr.Checkbox(value=True, label=f"Save results to {OUTPUT_DIR}")
                with gr.Row():
                    refresh = gr.Button("Refresh models")
                    go = gr.Button("Generate", variant="primary")

            with gr.Column(scale=2):
                gallery = gr.Gallery(label="Results", columns=2, height=720)
                status = gr.Textbox(label="Status", interactive=False)

        # Ordered list of setting controls for preset export/import (must match SETTING_KEYS).
        setting_controls = [
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
            lora_ctrls[0],
            lora_ctrls[1],
            lora_ctrls[2],
            lora_ctrls[3],
            lora_ctrls[4],
            lora_ctrls[5],
            lora_ctrls[6],
            lora_ctrls[7],
            lora_ctrls[8],
            lora_ctrls[9],
            input_image_on,
            uov_method,
            ip1_type,
            ip1_stop,
            ip1_weight,
            ip2_type,
            ip2_stop,
            ip2_weight,
            ip3_type,
            ip3_stop,
            ip3_weight,
            ip4_type,
            ip4_stop,
            ip4_weight,
            mix_ip_uov,
            mix_ip_inpaint,
            inpaint_prompt,
            inpaint_strength,
            inpaint_field,
            inpaint_engine,
            outpaint,
            enhance_on,
            enhance_uov,
            output_format,
            read_wildcards,
            black_out_nsfw,
            sampler_name,
            scheduler_name,
            vae_name,
            clip_skip,
            adm_scaler_positive,
            adm_scaler_negative,
            adm_scaler_end,
            adaptive_cfg,
            save_local,
            preset_name,
        ]
        assert len(setting_controls) == len(SETTING_KEYS)

        image_controls = [
            uov_image,
            ip1_image,
            ip2_image,
            ip3_image,
            ip4_image,
            enhance_image,
        ]
        assert len(image_controls) == len(IMAGE_KEYS)

        def _export_preset(include_imgs, name, *vals):
            values = {k: v for k, v in zip(SETTING_KEYS, vals[: len(SETTING_KEYS)])}
            img_vals = vals[len(SETTING_KEYS) :]
            for k, v in zip(IMAGE_KEYS, img_vals):
                values[k] = v
            PRESET_DIR.mkdir(parents=True, exist_ok=True)
            safe = "".join(c if c.isalnum() or c in "-_" else "_" for c in (name or "preset"))
            path = PRESET_DIR / f"{safe}.json"
            path.write_text(
                preset_to_json(values, include_images=bool(include_imgs), name=name or "preset"),
                encoding="utf-8",
            )
            return path, f"Saved {path.name}"

        def _import_preset(file_obj):
            empty = [gr.update() for _ in setting_controls] + [
                gr.update() for _ in image_controls
            ] + [gr.update(visible=False), "No file"]
            if file_obj is None:
                return empty
            path = file_obj if isinstance(file_obj, str) else getattr(file_obj, "name", None)
            if not path:
                return empty
            try:
                parsed = parse_preset(Path(path).read_text(encoding="utf-8"))
            except Exception as exc:  # noqa: BLE001
                return [gr.update() for _ in setting_controls] + [
                    gr.update() for _ in image_controls
                ] + [gr.update(visible=False), f"Load failed: {exc}"]

            settings = parsed.get("settings") or {}
            images = parsed.get("images") or {}
            flat = settings_to_updates(parsed)
            updates = []
            for key in SETTING_KEYS:
                if key in flat:
                    updates.append(gr.update(value=flat[key]))
                else:
                    updates.append(gr.update())
            for key in IMAGE_KEYS:
                if key in flat and flat[key] is not None:
                    updates.append(gr.update(value=flat[key]))
                else:
                    updates.append(gr.update())
            input_on = bool(flat.get("input_image_on", False))
            updates.append(gr.update(visible=input_on))
            updates.append(f"Loaded preset '{parsed.get('name')}'")
            return updates

        save_preset_btn.click(
            _export_preset,
            inputs=[include_images, preset_name, *setting_controls, *image_controls],
            outputs=[preset_file_out, preset_status],
        )
        load_preset_file.change(
            _import_preset,
            inputs=[load_preset_file],
            outputs=[*setting_controls, *image_controls, image_panel, preset_status],
        )

        def _refresh():
            ckpts, lora_names = list_remote_assets()
            updates = [
                gr.update(choices=ckpts, value=ckpts[0]),
                gr.update(choices=["None"] + ckpts, value="None"),
            ]
            for i in range(5):
                default = DEFAULT_LORA if i == 0 and DEFAULT_LORA in lora_names else "None"
                updates.append(gr.update(choices=lora_names, value=default))
            return updates

        refresh.click(
            _refresh,
            outputs=[
                base_model,
                refiner_model,
                lora_ctrls[0],
                lora_ctrls[2],
                lora_ctrls[4],
                lora_ctrls[6],
                lora_ctrls[8],
            ],
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
                *lora_ctrls,
                input_image_on,
                uov_method,
                uov_image,
                ip1_image,
                ip1_type,
                ip1_stop,
                ip1_weight,
                ip2_image,
                ip2_type,
                ip2_stop,
                ip2_weight,
                ip3_image,
                ip3_type,
                ip3_stop,
                ip3_weight,
                ip4_image,
                ip4_type,
                ip4_stop,
                ip4_weight,
                mix_ip_uov,
                mix_ip_inpaint,
                inpaint_image,
                inpaint_mask,
                inpaint_prompt,
                inpaint_strength,
                inpaint_field,
                inpaint_engine,
                outpaint,
                enhance_on,
                enhance_image,
                enhance_uov,
                output_format,
                read_wildcards,
                black_out_nsfw,
                sampler_name,
                scheduler_name,
                vae_name,
                clip_skip,
                adm_scaler_positive,
                adm_scaler_negative,
                adm_scaler_end,
                adaptive_cfg,
                save_local,
            ],
            outputs=[gallery, status],
        )
    return demo


def _patch_gradio_quirks() -> None:
    try:
        import gradio.networking as networking

        networking.url_ok = lambda _url: True  # type: ignore[assignment]
    except Exception:
        pass
    try:
        import gradio_client.utils as client_utils

        original = client_utils._json_schema_to_python_type

        def _safe_schema(schema, defs):  # type: ignore[no-untyped-def]
            if isinstance(schema, bool):
                return "Any"
            return original(schema, defs)

        client_utils._json_schema_to_python_type = _safe_schema
    except Exception:
        pass


def main() -> None:
    _patch_gradio_quirks()
    demo = build_ui()
    demo.queue(api_open=False).launch(
        server_name=HOST,
        server_port=PORT,
        share=False,
        show_api=False,
        inbrowser=False,
    )


if __name__ == "__main__":
    main()
