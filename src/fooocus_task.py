"""Build Fooocus AsyncTask argument lists from GenerateParams."""

from __future__ import annotations

import base64
import random
import time
from io import BytesIO
from pathlib import Path
from typing import Any

import numpy as np
from PIL import Image

from .generate_params import GenerateParams, GenerateResult, ImagePromptSlot, LoraSpec


def _pad_loras(loras: list[LoraSpec], max_n: int) -> list[LoraSpec]:
    out = list(loras[:max_n])
    while len(out) < max_n:
        out.append(LoraSpec(enabled=True, name="None", weight=1.0))
    return out


def _b64_to_numpy(image_b64: str | None) -> np.ndarray | None:
    if not image_b64:
        return None
    raw = base64.b64decode(image_b64)
    img = Image.open(BytesIO(raw)).convert("RGB")
    return np.array(img)


def _inpaint_payload(image_b64: str | None, mask_b64: str | None) -> dict | None:
    """Fooocus expects mask as HWC (it indexes mask[:, :, 0])."""
    image = _b64_to_numpy(image_b64)
    if image is None:
        return None
    h, w = image.shape[:2]
    if mask_b64:
        mask = _b64_to_numpy(mask_b64)
        if mask is None:
            mask = np.zeros((h, w), dtype=np.uint8)
        elif mask.ndim == 3:
            mask = mask[:, :, 0]
        if mask.shape[:2] != (h, w):
            mask_img = Image.fromarray(mask.astype(np.uint8), mode="L").resize(
                (w, h), Image.Resampling.NEAREST
            )
            mask = np.array(mask_img)
    else:
        mask = np.zeros((h, w), dtype=np.uint8)
    # AsyncTask.apply_image_input does mask[:, :, 0] — keep 3 channels.
    if mask.ndim == 2:
        mask = np.stack([mask, mask, mask], axis=-1)
    return {"image": image, "mask": mask}


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

    disabled = flags.disabled if hasattr(flags, "disabled") else "Disabled"
    uov_method = params.uov_method or disabled
    if str(uov_method).lower() in {"disabled", "none", ""}:
        uov_method = disabled

    enhance_uov = params.enhance_uov_method or disabled
    if str(enhance_uov).lower() in {"disabled", "none", ""}:
        enhance_uov = disabled

    input_on = bool(params.input_image_checkbox)
    current_tab = params.current_tab or "uov"
    if input_on and params.image_prompts and any(s.image_b64 for s in params.image_prompts):
        if current_tab not in {"ip", "uov", "inpaint", "enhance"}:
            current_tab = "ip"

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
            input_on,
            current_tab,
            uov_method,
            _b64_to_numpy(params.uov_image_b64),
            list(params.outpaint_selections or []),
            _inpaint_payload(params.inpaint_image_b64, params.inpaint_mask_b64),
            params.inpaint_additional_prompt or "",
            _b64_to_numpy(params.inpaint_mask_b64),
            True,  # disable_preview (lean serverless)
            False,  # disable_intermediate_results
            False,  # disable_seed_increment
            bool(params.black_out_nsfw),
            float(params.adm_scaler_positive),
            float(params.adm_scaler_negative),
            float(params.adm_scaler_end),
            float(
                params.adaptive_cfg
                if params.adaptive_cfg is not None
                else getattr(cfg, "default_cfg_tsnr", 7.0)
            ),
            int(
                params.clip_skip
                if params.clip_skip is not None
                else getattr(cfg, "default_clip_skip", 2)
            ),
            params.sampler_name or getattr(cfg, "default_sampler", "dpmpp_2m_sde_gpu"),
            params.scheduler_name or getattr(cfg, "default_scheduler", "karras"),
            params.vae_name or getattr(cfg, "default_vae", "Default (model)"),
            int(getattr(cfg, "default_overwrite_step", -1)),
            int(getattr(cfg, "default_overwrite_switch", -1)),
            -1,
            -1,
            -1,
            float(getattr(cfg, "default_overwrite_upscale", -1)),
            bool(params.mixing_image_prompt_and_vary_upscale),
            bool(params.mixing_image_prompt_and_inpaint),
            False,
            False,
            64,
            128,
            "joint",
            0.25,
            False,
            1.01,
            1.02,
            0.99,
            0.95,
            False,  # debugging_inpaint_preprocessor
            bool(params.inpaint_disable_initial_latent),
            params.inpaint_engine or getattr(cfg, "default_inpaint_engine_version", "v2.6"),
            float(params.inpaint_strength),
            float(params.inpaint_respective_field),
            bool(params.inpaint_advanced_masking),
            bool(params.invert_mask),
            int(params.inpaint_erode_or_dilate or 0),
        ]
    )

    import args_manager

    if not args_manager.args.disable_image_log:
        args.append(False)
    if not args_manager.args.disable_metadata:
        scheme = flags.MetadataScheme.FOOOCUS
        args.extend([False, scheme.value if hasattr(scheme, "value") else scheme])

    cn_count = int(getattr(cfg, "default_controlnet_image_count", 4))
    default_ip = getattr(flags, "default_ip", None) or flags.ip_list[0]
    slots = list(params.image_prompts or [])
    while len(slots) < cn_count:
        slots.append(ImagePromptSlot())
    for slot in slots[:cn_count]:
        ip_type = slot.type or default_ip
        if ip_type not in getattr(flags, "ip_list", [ip_type]):
            ip_type = default_ip
        args.extend(
            [
                _b64_to_numpy(slot.image_b64),
                float(slot.stop),
                float(slot.weight),
                ip_type,
            ]
        )

    args.extend(
        [
            False,
            0,
            False,
            _b64_to_numpy(params.enhance_image_b64),
            bool(params.enhance_checkbox),
            enhance_uov,
            getattr(cfg, "default_enhance_uov_processing_order", "Before First Enhancement"),
            getattr(cfg, "default_enhance_uov_prompt_type", "Original Prompt"),
        ]
    )

    enhance_tabs = int(getattr(cfg, "default_enhance_tabs", 3))
    for _ in range(enhance_tabs):
        args.extend(
            [
                False,
                "",
                "",
                "",
                getattr(cfg, "default_enhance_inpaint_mask_model", "sam"),
                "full",
                "vit_b",
                0.25,
                0.3,
                0,
                False,
                getattr(cfg, "default_inpaint_engine_version", "v2.6"),
                1.0,
                0.618,
                0,
                False,
            ]
        )

    return args


def _to_png_bytes(item: Any) -> bytes:
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


def run_generation(params: GenerateParams, timeout_sec: float = 900.0) -> GenerateResult:
    import modules.async_worker as worker

    started = time.perf_counter()
    args = build_async_task_args(params)
    task = worker.AsyncTask(args=args)
    seed = int(task.seed)
    worker.async_tasks.append(task)

    finished = False
    product: list[Any] = []
    last_progress = time.perf_counter()
    while not finished:
        if time.perf_counter() - started > timeout_sec:
            raise TimeoutError(
                f"Generation timed out after {timeout_sec:.0f}s "
                "(cancel the Modal call to stop GPU billing)."
            )
        # If the Fooocus worker thread died (e.g. missing expansion tokenizer),
        # AsyncTask never yields "finish" and would burn the GPU forever.
        thread = getattr(worker, "worker_thread", None) or getattr(worker, "thread", None)
        if thread is not None and hasattr(thread, "is_alive") and not thread.is_alive():
            raise RuntimeError(
                "Fooocus worker thread exited before finishing "
                "(check Modal logs; often missing prompt-expansion tokenizer files)."
            )
        time.sleep(0.05)
        if not task.yields:
            # Soft stall signal: no yields for a long stretch after model load can hang.
            if time.perf_counter() - last_progress > 600:
                raise TimeoutError("Generation stalled with no worker progress for 600s.")
            continue
        last_progress = time.perf_counter()
        flag, payload = task.yields.pop(0)
        if flag == "finish":
            product = payload or task.results or []
            finished = True
        elif flag == "error":
            raise RuntimeError(f"Fooocus worker error: {payload}")

    images = [_to_png_bytes(x) for x in product]
    paths = [x for x in product if isinstance(x, str)]

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
        meta={
            "prompt": params.prompt,
            "base_model": params.base_model,
            "performance": params.performance,
            "tab": params.current_tab if params.input_image_checkbox else "txt2img",
        },
    )
