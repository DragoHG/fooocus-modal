"""Build Fooocus AsyncTask argument lists from GenerateParams."""

from __future__ import annotations

import random
import time
from pathlib import Path
from typing import Any

from .generate_params import GenerateParams, GenerateResult, LoraSpec


def _pad_loras(loras: list[LoraSpec], max_n: int) -> list[LoraSpec]:
    out = list(loras[:max_n])
    while len(out) < max_n:
        out.append(LoraSpec(enabled=True, name="None", weight=1.0))
    return out


def build_async_task_args(params: GenerateParams) -> list[Any]:
    """Match Fooocus webui ctrls order consumed by AsyncTask (after get_task pops State)."""
    import modules.config as cfg
    import modules.flags as flags

    seed = params.seed
    if seed is None or int(seed) < 0:
        seed = random.randint(0, 2**63 - 1)
    seed = int(seed)

    aspect = params.aspect_ratio
    labels = list(getattr(cfg, "available_aspect_ratios_labels", []) or [])
    ratios = list(getattr(cfg, "available_aspect_ratios", []) or [])
    if labels and aspect not in labels:
        raw = aspect.replace("×", "*")
        matched = None
        for i, ratio in enumerate(ratios):
            cand = str(ratio).replace("×", "*")
            if cand == raw or cand.startswith(raw) or raw.startswith(cand.split(" ")[0]):
                matched = i
                break
        if matched is not None and matched < len(labels):
            aspect = labels[matched]
        else:
            aspect = getattr(cfg, "default_aspect_ratio", aspect)

    max_loras = int(cfg.default_max_lora_number)
    loras = _pad_loras(params.loras, max_loras)

    args: list[Any] = [
        False,  # generate_image_grid
        params.prompt,
        params.negative_prompt,
        list(params.styles),
        params.performance,
        aspect,
        int(params.image_number),
        params.output_format,
        seed,
        bool(params.read_wildcards_in_order),
        float(params.sharpness),
        float(params.guidance_scale),
        params.base_model,
        params.refiner_model,
        float(params.refiner_switch),
    ]

    for lora in loras:
        args.extend([bool(lora.enabled), str(lora.name), float(lora.weight)])

    args.extend(
        [
            False,  # input_image_checkbox
            "uov",  # current_tab
            flags.disabled if hasattr(flags, "disabled") else "Disabled",
            None,  # uov_input_image
            [],  # outpaint_selections
            None,  # inpaint_input_image
            "",  # inpaint_additional_prompt
            None,  # inpaint_mask_image
            True,  # disable_preview
            False,  # disable_intermediate_results
            False,  # disable_seed_increment
            False,  # black_out_nsfw
            1.5,  # adm_scaler_positive
            0.8,  # adm_scaler_negative
            0.5,  # adm_scaler_end
            float(getattr(cfg, "default_cfg_tsnr", 7.0)),
            int(getattr(cfg, "default_clip_skip", 2)),
            getattr(cfg, "default_sampler", "dpmpp_2m_sde_gpu"),
            getattr(cfg, "default_scheduler", "karras"),
            getattr(cfg, "default_vae", "Default (model)"),
            int(getattr(cfg, "default_overwrite_step", -1)),
            int(getattr(cfg, "default_overwrite_switch", -1)),
            -1,  # overwrite_width
            -1,  # overwrite_height
            -1,  # overwrite_vary_strength
            float(getattr(cfg, "default_overwrite_upscale", -1)),
            False,  # mixing_image_prompt_and_vary_upscale
            False,  # mixing_image_prompt_and_inpaint
            False,  # debugging_cn_preprocessor
            False,  # skipping_cn_preprocessor
            64,  # canny_low_threshold
            128,  # canny_high_threshold
            "joint",  # refiner_swap_method
            0.25,  # controlnet_softness
            False,  # freeu_enabled
            1.01,
            1.02,
            0.99,
            0.95,
            False,  # debugging_inpaint_preprocessor
            False,  # inpaint_disable_initial_latent
            getattr(cfg, "default_inpaint_engine_version", "v2.6"),
            1.0,  # inpaint_strength
            0.618,  # inpaint_respective_field
            False,  # inpaint_advanced_masking_checkbox
            False,  # invert_mask_checkbox
            0,  # inpaint_erode_or_dilate
        ]
    )

    import args_manager

    if not args_manager.args.disable_image_log:
        args.append(False)  # save_final_enhanced_image_only
    if not args_manager.args.disable_metadata:
        scheme = flags.MetadataScheme.FOOOCUS
        args.extend([False, scheme.value if hasattr(scheme, "value") else scheme])

    cn_count = int(getattr(cfg, "default_controlnet_image_count", 4))
    default_ip = getattr(flags, "default_ip", None) or flags.ip_list[0]
    for _ in range(cn_count):
        args.extend([None, 0.5, 0.6, default_ip])

    args.extend(
        [
            False,  # debugging_dino
            0,  # dino_erode_or_dilate
            False,  # debugging_enhance_masks_checkbox
            None,  # enhance_input_image
            False,  # enhance_checkbox
            flags.disabled if hasattr(flags, "disabled") else "Disabled",
            getattr(cfg, "default_enhance_uov_processing_order", "Before First Enhancement"),
            getattr(cfg, "default_enhance_uov_prompt_type", "Original Prompt"),
        ]
    )

    enhance_tabs = int(getattr(cfg, "default_enhance_tabs", 3))
    for _ in range(enhance_tabs):
        args.extend(
            [
                False,  # enhance_enabled
                "",  # mask dino prompt
                "",  # enhance prompt
                "",  # enhance negative
                getattr(cfg, "default_enhance_inpaint_mask_model", "sam"),
                "full",  # cloth category
                "vit_b",  # sam model
                0.25,  # text threshold
                0.3,  # box threshold
                0,  # sam max detections
                False,  # disable initial latent
                getattr(cfg, "default_inpaint_engine_version", "v2.6"),
                1.0,
                0.618,
                0,
                False,  # mask invert
            ]
        )

    return args


def _to_png_bytes(item: Any) -> bytes:
    from io import BytesIO

    from PIL import Image
    import numpy as np

    if isinstance(item, (bytes, bytearray)):
        return bytes(item)
    if isinstance(item, str) and Path(item).exists():
        return Path(item).read_bytes()
    if isinstance(item, Image.Image):
        buf = BytesIO()
        item.save(buf, format="PNG")
        return buf.getvalue()
    if isinstance(item, np.ndarray):
        img = Image.fromarray(item.astype("uint8"))
        buf = BytesIO()
        img.save(buf, format="PNG")
        return buf.getvalue()
    if isinstance(item, dict):
        for key in ("name", "path", "image"):
            if key in item:
                return _to_png_bytes(item[key])
    raise TypeError(f"Unsupported image result type: {type(item)!r}")


def run_generation(params: GenerateParams) -> GenerateResult:
    import modules.async_worker as worker

    started = time.perf_counter()
    args = build_async_task_args(params)
    task = worker.AsyncTask(args=args)
    seed = int(task.seed)
    worker.async_tasks.append(task)

    finished = False
    product: list[Any] = []
    while not finished:
        time.sleep(0.05)
        if not task.yields:
            continue
        flag, payload = task.yields.pop(0)
        if flag == "finish":
            product = payload or task.results or []
            finished = True

    images = [_to_png_bytes(x) for x in product]
    paths: list[str] = []
    for x in product:
        if isinstance(x, str):
            paths.append(x)

    gpu_name = ""
    try:
        import subprocess

        gpu_name = subprocess.check_output(
            ["nvidia-smi", "--query-gpu=name", "--format=csv,noheader"],
            text=True,
        ).strip().splitlines()[0]
    except Exception:
        gpu_name = ""

    return GenerateResult(
        images=images,
        seed=seed,
        elapsed_sec=time.perf_counter() - started,
        gpu_name=gpu_name,
        paths=paths,
        meta={"prompt": params.prompt, "base_model": params.base_model},
    )
