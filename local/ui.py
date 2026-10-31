"""Local Gradio UI - Fooocus-style controls to Modal FooocusWorker."""

from __future__ import annotations

import base64
import json
import os
import sys
import time
import zipfile
from io import BytesIO
from pathlib import Path

import gradio as gr
from dotenv import load_dotenv
from PIL import Image, ImageChops, ImageOps

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
# Survives page reload (Gradio State does not). Paths must still exist on disk.
SESSION_CACHE_PATH = OUTPUT_DIR / ".session_cache.json"

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
INPAINT_ENGINES = ["None", "v1", "v2.5", "v2.6"]
INPAINT_METHODS = [
    "Inpaint or Outpaint (default)",
    "Improve Detail (face, hand, eyes, etc.)",
    "Modify Content (add objects, change background, etc.)",
]
INPAINT_QUICK_PROMPTS = [
    "highly detailed face",
    "detailed hand",
    "detailed eyes",
    "beautiful eyes",
    "detailed fingers",
]

MAX_HISTORY = 48

UI_CSS = """
#action-bar {
  position: sticky;
  top: 0;
  z-index: 1000;
  background: var(--body-background-fill, #0b1220);
  padding: 8px 12px;
  border-bottom: 1px solid var(--border-color-primary, #333);
  margin-bottom: 8px;
}
#action-bar .generate-btn button {
  min-width: 140px;
  font-weight: 700;
}
#results-panel {
  position: sticky;
  top: 70px;
  align-self: flex-start;
}
#result-thumbs {
  max-height: 160px !important;
}
#result-viewer {
  cursor: zoom-in;
}
#result-controls {
  position: relative;
  z-index: 5;
  background: var(--body-background-fill, #0b1220);
  padding: 8px 0 4px;
  border-top: 1px solid var(--border-color-primary, #333);
}
#result-controls button {
  background: #1a2332 !important;
  color: #f3f6fb !important;
  border: 1px solid #4b5568 !important;
}
#result-controls button:hover {
  background: #243044 !important;
}
#inpaint-editor {
  min-height: 420px;
}
#inpaint-editor button,
#inpaint-editor .toolbar button,
#inpaint-editor [class*="icon"] {
  background: #111827 !important;
  color: #f9fafb !important;
  border: 1px solid #6b7280 !important;
  opacity: 1 !important;
}
#inpaint-mask-tools button {
  background: #1f2937 !important;
  color: #f9fafb !important;
  border: 1px solid #6b7280 !important;
}
/* Only style when Gradio shows the panel. Never force display with !important. */
#fm-fullscreen:not(.hide):not([hidden]) {
  position: fixed !important;
  inset: 0 !important;
  z-index: 100000 !important;
  background: rgba(0, 0, 0, 0.92) !important;
  flex-direction: column !important;
  align-items: center !important;
  justify-content: flex-start !important;
  padding: 16px !important;
  box-sizing: border-box !important;
  cursor: zoom-out;
  overflow: auto !important;
}
#fm-fullscreen .fm-fs-inner {
  cursor: default;
  max-width: min(96vw, 1400px);
  width: 100%;
  display: flex;
  flex-direction: column;
  gap: 10px;
}
#fm-fullscreen .fm-fs-toolbar {
  position: sticky;
  top: 0;
  z-index: 2;
  background: rgba(10, 14, 22, 0.96);
  border: 1px solid #4b5568;
  border-radius: 8px;
  padding: 8px 10px;
}
#fm-fullscreen .fm-fs-toolbar button {
  background: #1f2937 !important;
  color: #f9fafb !important;
  border: 1px solid #9ca3af !important;
}
#fm-fullscreen .fm-fs-toolbar button:hover {
  background: #374151 !important;
}
#fm-fullscreen img,
#fm-fullscreen .image-container,
#fm-fullscreen .image-frame {
  max-height: 72vh !important;
  object-fit: contain !important;
}
@media (max-width: 960px) {
  #main-row { flex-direction: column !important; }
  #results-panel { position: static !important; width: 100% !important; }
  #action-bar .generate-btn button { width: 100%; }
}
"""

UI_JS = """
() => {
  const bindFsClose = () => {
    const root = document.getElementById("fm-fullscreen");
    if (!root || root.dataset.fmBound === "1") return;
    root.dataset.fmBound = "1";
    root.addEventListener("click", (e) => {
      if (e.target === root) {
        document.querySelector("#fm-fs-close button")?.click();
      }
    });
  };

  const bindViewerZoom = () => {
    const root = document.querySelector("#result-viewer");
    if (!root || root.dataset.clickBound === "1") return;
    root.dataset.clickBound = "1";
    root.addEventListener("click", (e) => {
      if (e.target.closest("a, button, .download, label")) return;
      document.querySelector("#fm-fs-open button")?.click();
    });
  };

  const boot = () => {
    bindFsClose();
    bindViewerZoom();
  };

  const obs = new MutationObserver(boot);
  obs.observe(document.body, { childList: true, subtree: true });
  document.addEventListener("keydown", (e) => {
    if (e.key !== "Escape") return;
    const root = document.getElementById("fm-fullscreen");
    if (!root || root.classList.contains("hide") || root.style.display === "none") return;
    document.querySelector("#fm-fs-close button")?.click();
  });
  setTimeout(boot, 400);
  setTimeout(boot, 1200);
}
"""


def _alive_paths(paths: list | None) -> list[str]:
    out: list[str] = []
    for p in paths or []:
        if not p:
            continue
        path = Path(str(p))
        if path.is_file():
            out.append(str(path.resolve()))
    return out


def _nav_label(index: int, total: int) -> str:
    if total <= 0:
        return "0 / 0"
    return f"{index + 1} / {total}"


def _pick_choices(history: list[str]) -> list[tuple[str, str]]:
    choices: list[tuple[str, str]] = []
    for i, path in enumerate(history):
        choices.append((f"{i + 1}. {Path(path).name}", path))
    return choices


def _jsonable_setting(value):
    """Coerce control values into JSON-safe forms (never images)."""
    if value is None or isinstance(value, (bool, int, float, str)):
        return value
    if isinstance(value, (list, tuple)):
        return [_jsonable_setting(v) for v in value]
    if isinstance(value, dict):
        # ImageEditor / rare nested blobs — skip
        return None
    try:
        if isinstance(value, Image.Image):
            return None
    except Exception:
        pass
    return str(value)


def _settings_from_values(values: dict | None) -> dict:
    out: dict = {}
    for key in SETTING_KEYS:
        if values and key in values:
            coerced = _jsonable_setting(values[key])
            if coerced is not None or values[key] is None:
                out[key] = coerced
    return out


def _read_session_raw() -> dict:
    try:
        if SESSION_CACHE_PATH.is_file():
            data = json.loads(SESSION_CACHE_PATH.read_text(encoding="utf-8"))
            if isinstance(data, dict):
                return data
    except (OSError, json.JSONDecodeError):
        pass
    return {}


def _parse_cache(raw: str | None) -> tuple[list[str], int, list[str], dict]:
    if not raw or not str(raw).strip():
        return [], 0, [], {}
    try:
        data = json.loads(raw)
    except Exception:
        return [], 0, [], {}
    if not isinstance(data, dict):
        return [], 0, [], {}
    history = _alive_paths(data.get("history") or [])
    picked = [p for p in _alive_paths(data.get("picked") or []) if p in set(history)]
    index = int(data.get("index") or 0)
    if history:
        index = max(0, min(index, len(history) - 1))
    else:
        index = 0
    settings = _settings_from_values(data.get("settings") or {})
    return history, index, picked, settings


def _persist_session(
    history: list[str],
    index: int,
    picked: list[str],
    settings: dict | None = None,
) -> str:
    """Write gallery + marks + settings (no images) for page reload."""
    prev = _read_session_raw()
    history = _alive_paths(history)
    picked = [p for p in _alive_paths(picked) if p in set(history)]
    index = int(index or 0)
    if history:
        index = max(0, min(index, len(history) - 1))
    else:
        index = 0
    if settings is None:
        merged_settings = _settings_from_values(prev.get("settings") or {})
    else:
        merged_settings = _settings_from_values(settings)
    payload_obj = {
        "version": 2,
        "history": history,
        "index": index,
        "picked": picked,
        "settings": merged_settings,
    }
    payload = json.dumps(payload_obj, ensure_ascii=True, indent=2)
    try:
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        SESSION_CACHE_PATH.write_text(payload, encoding="utf-8")
        # Mirror settings-only JSON (no images) for easy backup / preset reuse.
        if merged_settings:
            PRESET_DIR.mkdir(parents=True, exist_ok=True)
            last = PRESET_DIR / "last-session.json"
            last.write_text(
                preset_to_json(merged_settings, include_images=False, name="last-session"),
                encoding="utf-8",
            )
    except OSError:
        pass
    return payload


def _load_session_cache() -> tuple[list[str], int, list[str], dict]:
    data = _read_session_raw()
    if not data:
        return [], 0, [], {}
    history = _alive_paths(data.get("history") or [])
    picked = [p for p in _alive_paths(data.get("picked") or []) if p in set(history)]
    index = int(data.get("index") or 0)
    if history:
        index = max(0, min(index, len(history) - 1))
    else:
        index = 0
    settings = _settings_from_values(data.get("settings") or {})
    return history, index, picked, settings


def _setting_updates(settings: dict) -> list:
    updates = []
    for key in SETTING_KEYS:
        if key in settings:
            updates.append(gr.update(value=settings[key]))
        else:
            updates.append(gr.update())
    return updates


def _viewer_bundle(history: list[str], index: int, picked: list[str] | None = None):
    history = _alive_paths(history)
    picked = [p for p in _alive_paths(picked) if p in set(history)]
    if not history:
        _persist_session([], 0, [])
        return (
            [],
            0,
            gr.update(value=None),
            None,
            None,
            "0 / 0",
            gr.update(interactive=False),
            gr.update(interactive=False),
            [],
            gr.update(choices=[], value=[]),
            "Marked: 0",
        )
    index = max(0, min(int(index), len(history) - 1))
    selected = history[index]
    cols = 1 if len(history) == 1 else (2 if len(history) <= 6 else 3)
    marked = selected in set(picked)
    _persist_session(history, index, picked)
    return (
        history,
        index,
        gr.update(value=history, columns=cols),
        selected,
        selected,
        _nav_label(index, len(history)),
        gr.update(interactive=len(history) > 1),
        gr.update(interactive=len(history) > 1),
        picked,
        gr.update(choices=_pick_choices(history), value=picked),
        f"Marked: {len(picked)}" + (" · current marked" if marked else ""),
    )


def _zip_picked(picked: list[str]) -> str:
    paths = _alive_paths(picked)
    if not paths:
        raise gr.Error("Mark at least one image before downloading the selection.")
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    zip_path = OUTPUT_DIR / f"selection_{int(time.time())}.zip"
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for path in paths:
            zf.write(path, arcname=Path(path).name)
    return str(zip_path)


def _pil_to_b64(img: Image.Image | None) -> str | None:
    if img is None:
        return None
    if not isinstance(img, Image.Image):
        try:
            img = Image.fromarray(img)
        except Exception:
            return None
    buf = BytesIO()
    img.convert("RGB").save(buf, format="PNG")
    return base64.b64encode(buf.getvalue()).decode("ascii")


def _as_pil(img) -> Image.Image | None:
    if img is None:
        return None
    if isinstance(img, Image.Image):
        return img
    try:
        return Image.fromarray(img)
    except Exception:
        return None


def _mask_from_layer(layer: Image.Image | None) -> Image.Image | None:
    """Build an RGB mask (white = edit) from a brush layer."""
    layer = _as_pil(layer)
    if layer is None:
        return None
    if layer.mode == "RGBA":
        alpha = layer.split()[-1]
        rgb = layer.convert("RGB")
        # Prefer alpha strokes; fall back to bright paint on transparent canvas.
        a = alpha.point(lambda p: 255 if p > 16 else 0)
        # Brightness of RGB also counts (white brush on transparent).
        gray = rgb.convert("L")
        bright = gray.point(lambda p: 255 if p > 32 else 0)
        combined = ImageChops.lighter(a, bright)
        return Image.merge("RGB", (combined, combined, combined))
    gray = layer.convert("L")
    bw = gray.point(lambda p: 255 if p > 32 else 0)
    return Image.merge("RGB", (bw, bw, bw))


def _editor_to_image_and_mask(editor_value, extra_mask=None) -> tuple[Image.Image | None, Image.Image | None]:
    """Parse Gradio ImageEditor / upload into background + mask (Fooocus-style)."""
    bg = None
    mask = None
    if isinstance(editor_value, dict):
        bg = _as_pil(editor_value.get("background") or editor_value.get("image"))
        layers = editor_value.get("layers") or []
        if layers:
            mask = _mask_from_layer(_as_pil(layers[0]))
        if mask is None:
            composite = _as_pil(editor_value.get("composite"))
            if bg is not None and composite is not None and composite.size == bg.size:
                diff = ImageChops.difference(composite.convert("RGB"), bg.convert("RGB"))
                gray = diff.convert("L").point(lambda p: 255 if p > 12 else 0)
                if gray.getextrema()[1] > 0:
                    mask = Image.merge("RGB", (gray, gray, gray))
    else:
        bg = _as_pil(editor_value)

    extra = _as_pil(extra_mask)
    if extra is not None:
        extra_rgb = _mask_from_layer(extra) or extra.convert("RGB")
        if mask is None:
            mask = extra_rgb
        elif bg is not None:
            if extra_rgb.size != mask.size:
                extra_rgb = extra_rgb.resize(mask.size, Image.Resampling.NEAREST)
            mask = ImageChops.lighter(mask, extra_rgb)
    return bg, mask


def _editor_value(bg: Image.Image | None, mask: Image.Image | None = None) -> dict | None:
    if bg is None:
        return None
    bg = bg.convert("RGBA")
    layers: list[Image.Image] = []
    if mask is not None:
        m = mask.convert("L")
        if m.size != bg.size:
            m = m.resize(bg.size, Image.Resampling.NEAREST)
        layer = Image.new("RGBA", bg.size, (0, 0, 0, 0))
        white = Image.new("RGBA", bg.size, (255, 255, 255, 255))
        layer.paste(white, (0, 0), m.point(lambda p: 255 if p > 32 else 0))
        layers = [layer]
    return {"background": bg.convert("RGB"), "layers": layers, "composite": None}


def _inpaint_mode_defaults(method: str, engine: str):
    """Match Fooocus webui `inpaint_mode_change` defaults."""
    detail = INPAINT_METHODS[1]
    modify = INPAINT_METHODS[2]
    if method == detail:
        return {
            "prompt_visible": True,
            "outpaint_visible": False,
            "outpaint_value": [],
            "disable_initial_latent": False,
            "engine": "None",
            "strength": 0.5,
            "field": 0.0,
        }
    if method == modify:
        eng = engine if engine and engine != "empty" else "v2.6"
        if eng == "None":
            eng = "v2.6"
        return {
            "prompt_visible": True,
            "outpaint_visible": False,
            "outpaint_value": [],
            "disable_initial_latent": True,
            "engine": eng,
            "strength": 1.0,
            "field": 0.0,
        }
    eng = engine if engine and engine != "empty" else "v2.6"
    if eng == "None":
        eng = "v2.6"
    return {
        "prompt_visible": False,
        "outpaint_visible": True,
        "outpaint_value": gr.update(),
        "disable_initial_latent": False,
        "engine": eng,
        "strength": 1.0,
        "field": 0.618,
    }


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
    inpaint_method,
    inpaint_prompt,
    inpaint_strength,
    inpaint_field,
    inpaint_engine,
    inpaint_advanced_masking,
    invert_mask,
    inpaint_erode_or_dilate,
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

    inpaint_img, inpaint_msk = _editor_to_image_and_mask(
        inpaint_image, inpaint_mask if inpaint_advanced_masking else None
    )
    mode = _inpaint_mode_defaults(inpaint_method or INPAINT_METHODS[0], inpaint_engine or "v2.6")
    # Apply Fooocus method defaults when the user left sliders at prior values is already
    # handled by the Method dropdown; still honor explicit disable_initial_latent from mode.
    engine = inpaint_engine or mode["engine"]
    if engine == "None" and (inpaint_method or "") == INPAINT_METHODS[0]:
        engine = "v2.6"

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
        "inpaint_engine": engine,
        "inpaint_method": inpaint_method or INPAINT_METHODS[0],
        "inpaint_disable_initial_latent": bool(mode["disable_initial_latent"]),
        "inpaint_advanced_masking": bool(inpaint_advanced_masking),
        "invert_mask": bool(invert_mask),
        "inpaint_erode_or_dilate": int(inpaint_erode_or_dilate or 0),
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

    paths: list[str] = []
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    stamp = int(time.time())
    ext = (output_format or "png").lower()
    if ext == "jpeg":
        ext = "jpg"
    for idx, b64 in enumerate(images_b64):
        raw = base64.b64decode(b64)
        path = OUTPUT_DIR / f"{stamp}_{result.get('seed', 0)}_{idx}.{ext}"
        # File paths keep the Gradio viewer light (no giant PIL blobs in State).
        path.write_bytes(raw)
        paths.append(str(path))

    elapsed = time.perf_counter() - started
    info = (
        f"seed={result.get('seed')} · gpu={result.get('gpu_name') or 'n/a'} · "
        f"worker={result.get('elapsed_sec', 0):.1f}s · roundtrip={elapsed:.1f}s · "
        f"mode={result.get('meta', {}).get('tab', 'txt2img')}"
    )
    return paths, info


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

    with gr.Blocks(title="fooocus-modal", css=UI_CSS, js=UI_JS) as demo:
        history_state = gr.State([])  # all result file paths this session
        index_state = gr.State(0)
        picked_state = gr.State([])  # marked paths for multi-download (persisted)

        with gr.Group(elem_id="action-bar"):
            gr.Markdown(
                "**fooocus-modal** · Prompt, settings, marks and gallery restore after reload "
                "(images stay out of JSON). Click Selected for fullscreen; Esc / outside closes it."
            )
            with gr.Row():
                prompt = gr.Textbox(
                    label="Prompt",
                    lines=2,
                    placeholder="Describe the image",
                    scale=5,
                )
                with gr.Column(scale=2, min_width=200, elem_classes=["generate-btn"]):
                    go = gr.Button("Generate", variant="primary", size="lg")
                    refresh = gr.Button("Refresh models", size="sm")
            queue_status = gr.Textbox(
                label="Queue / status",
                value="Idle - jobs queue one after another; history is kept.",
                interactive=False,
                lines=1,
            )

        with gr.Row(elem_id="main-row"):
            with gr.Column(scale=6):
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
                        gr.Markdown(
                            "Upload an image, then **paint the area to change** with the white brush "
                            "(same idea as Fooocus). Use Method for Detail / Modify Content. "
                            "Outpaint expands the canvas with Left/Right/Top/Bottom."
                        )
                        inpaint_method = gr.Dropdown(
                            INPAINT_METHODS,
                            value=INPAINT_METHODS[0],
                            label="Method",
                        )
                        inpaint_image = gr.ImageEditor(
                            label="Image and brush mask (paint white over the area to edit)",
                            elem_id="inpaint-editor",
                            type="pil",
                            height=480,
                            layers=True,
                            eraser=gr.Eraser(default_size=28),
                            brush=gr.Brush(
                                default_size=36,
                                colors=["#ffffff", "#ff0000"],
                                default_color="#ffffff",
                                color_mode="fixed",
                            ),
                            transforms=(),
                            sources=["upload", "clipboard"],
                        )
                        with gr.Row(elem_id="inpaint-mask-tools"):
                            mask_fill_btn = gr.Button("Mask entire image", size="sm")
                            mask_clear_btn = gr.Button("Clear brush mask", size="sm")
                            mask_invert_btn = gr.Button("Invert brush mask", size="sm")
                        inpaint_advanced_masking = gr.Checkbox(
                            label="Enable advanced masking (upload a separate mask)",
                            value=False,
                        )
                        with gr.Column(visible=False) as inpaint_mask_col:
                            inpaint_mask = gr.Image(
                                label="Uploaded mask (white = edit)",
                                type="pil",
                                height=220,
                            )
                            invert_mask = gr.Checkbox(
                                label="Invert mask when generating",
                                value=False,
                            )
                            inpaint_erode_or_dilate = gr.Slider(
                                -64,
                                64,
                                value=0,
                                step=1,
                                label="Erode (−) / dilate (+) mask",
                            )
                        inpaint_prompt = gr.Textbox(
                            label="Inpaint additional prompt",
                            visible=False,
                            placeholder="Describe what should appear in the masked area",
                        )
                        inpaint_quick = gr.Dropdown(
                            INPAINT_QUICK_PROMPTS,
                            label="Quick additional prompt",
                            value=None,
                            allow_custom_value=False,
                        )
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

                def _on_inpaint_method(method, engine):
                    mode = _inpaint_mode_defaults(method, engine or "v2.6")
                    outpaint_upd = (
                        gr.update(visible=False, value=[])
                        if not mode["outpaint_visible"]
                        else gr.update(visible=True)
                    )
                    return (
                        gr.update(visible=mode["prompt_visible"]),
                        outpaint_upd,
                        gr.update(value=mode["engine"]),
                        gr.update(value=mode["strength"]),
                        gr.update(value=mode["field"]),
                    )

                inpaint_method.change(
                    _on_inpaint_method,
                    inputs=[inpaint_method, inpaint_engine],
                    outputs=[
                        inpaint_prompt,
                        outpaint,
                        inpaint_engine,
                        inpaint_strength,
                        inpaint_field,
                    ],
                    queue=False,
                )
                inpaint_advanced_masking.change(
                    lambda on: gr.update(visible=on),
                    inputs=inpaint_advanced_masking,
                    outputs=inpaint_mask_col,
                    queue=False,
                )
                inpaint_quick.change(
                    lambda q: q or gr.update(),
                    inputs=inpaint_quick,
                    outputs=inpaint_prompt,
                    queue=False,
                )

                def _mask_fill(editor):
                    bg, _mask = _editor_to_image_and_mask(editor, None)
                    if bg is None:
                        raise gr.Error("Upload an image before creating a mask.")
                    full = Image.new("L", bg.size, 255)
                    return _editor_value(bg, full)

                def _mask_clear(editor):
                    bg, _mask = _editor_to_image_and_mask(editor, None)
                    if bg is None:
                        return gr.update()
                    return _editor_value(bg, None)

                def _mask_invert(editor):
                    bg, mask = _editor_to_image_and_mask(editor, None)
                    if bg is None:
                        raise gr.Error("Upload an image before inverting the mask.")
                    if mask is None:
                        full = Image.new("L", bg.size, 255)
                        return _editor_value(bg, full)
                    inv = ImageOps.invert(mask.convert("L"))
                    return _editor_value(bg, inv)

                mask_fill_btn.click(_mask_fill, inputs=inpaint_image, outputs=inpaint_image, queue=False)
                mask_clear_btn.click(_mask_clear, inputs=inpaint_image, outputs=inpaint_image, queue=False)
                mask_invert_btn.click(_mask_invert, inputs=inpaint_image, outputs=inpaint_image, queue=False)

                with gr.Accordion("Presets (save / load JSON)", open=False):
                    gr.Markdown(
                        "Download prompt + all settings as JSON (no input images). "
                        "Settings also auto-save on change and restore after reload. "
                        "A copy is kept at `outputs/presets/last-session.json`."
                    )
                    preset_name = gr.Textbox(value="my-preset", label="Preset name")
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

            with gr.Column(scale=5, elem_id="results-panel"):
                gr.Markdown("### Results")
                thumbs = gr.Gallery(
                    label="Session thumbnails (click to select)",
                    elem_id="result-thumbs",
                    columns=3,
                    height=150,
                    object_fit="cover",
                    preview=False,
                    allow_preview=False,
                    show_download_button=False,
                    show_share_button=False,
                )
                viewer = gr.Image(
                    label="Selected (click image to fullscreen)",
                    elem_id="result-viewer",
                    type="filepath",
                    height=380,
                    show_download_button=True,
                    interactive=False,
                )
                with gr.Column(elem_id="result-controls"):
                    with gr.Row():
                        prev_btn = gr.Button("← Prev", size="sm")
                        nav_label = gr.Textbox(
                            value="0 / 0",
                            label="Image",
                            interactive=False,
                            max_lines=1,
                            scale=1,
                        )
                        next_btn = gr.Button("Next →", size="sm")
                    with gr.Row():
                        fs_open = gr.Button("Fullscreen", size="sm", elem_id="fm-fs-open")
                        mark_btn = gr.Button("Mark / unmark", size="sm")
                        download_file = gr.File(label="Download current", interactive=False)
                        clear_result = gr.Button("Clear session", size="sm")
                pick_status = gr.Textbox(
                    value="Marked: 0",
                    label="Selection",
                    interactive=False,
                    max_lines=1,
                )
                pick_box = gr.CheckboxGroup(
                    label="Marked for ZIP download (survives nav / reload)",
                    choices=[],
                    value=[],
                )
                with gr.Row():
                    download_zip_btn = gr.Button("Download marked ZIP", variant="secondary")
                    clear_marks_btn = gr.Button("Clear marks", size="sm")
                zip_file = gr.File(label="Marked ZIP", interactive=False)
                status = gr.Textbox(label="Last job", interactive=False, lines=2)

        with gr.Column(visible=False, elem_id="fm-fullscreen") as fs_panel:
            with gr.Column(elem_classes=["fm-fs-inner"]):
                with gr.Row(elem_classes=["fm-fs-toolbar"]):
                    fs_prev = gr.Button("← Prev", size="sm")
                    fs_nav = gr.Textbox(value="0 / 0", interactive=False, max_lines=1)
                    fs_next = gr.Button("Next →", size="sm")
                    fs_close = gr.Button("Close (Esc / click outside)", elem_id="fm-fs-close")
                fs_image = gr.Image(
                    label="Fullscreen",
                    type="filepath",
                    height=680,
                    show_download_button=True,
                    interactive=False,
                )

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
            inpaint_method,
            inpaint_prompt,
            inpaint_strength,
            inpaint_field,
            inpaint_engine,
            inpaint_advanced_masking,
            invert_mask,
            inpaint_erode_or_dilate,
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

        generate_inputs = [
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
            inpaint_method,
            inpaint_prompt,
            inpaint_strength,
            inpaint_field,
            inpaint_engine,
            inpaint_advanced_masking,
            invert_mask,
            inpaint_erode_or_dilate,
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
        ]

        def _export_preset(name, *vals):
            values = {k: v for k, v in zip(SETTING_KEYS, vals)}
            # Always settings-only (no images in JSON).
            hist, idx, marks, _ = _load_session_cache()
            _persist_session(hist, idx, marks, values)
            PRESET_DIR.mkdir(parents=True, exist_ok=True)
            safe = "".join(c if c.isalnum() or c in "-_" else "_" for c in (name or "preset"))
            path = PRESET_DIR / f"{safe}.json"
            path.write_text(
                preset_to_json(values, include_images=False, name=name or "preset"),
                encoding="utf-8",
            )
            return path, f"Saved {path.name} (settings only, no images)"

        def _import_preset(file_obj):
            empty = [gr.update() for _ in setting_controls] + [
                gr.update(visible=False),
                "No file",
            ]
            if file_obj is None:
                return empty
            path = file_obj if isinstance(file_obj, str) else getattr(file_obj, "name", None)
            if not path:
                return empty
            try:
                parsed = parse_preset(Path(path).read_text(encoding="utf-8"))
            except Exception as exc:  # noqa: BLE001
                return [gr.update() for _ in setting_controls] + [
                    gr.update(visible=False),
                    f"Load failed: {exc}",
                ]

            flat = settings_to_updates(parsed)
            # Drop any legacy embedded images — session restore is settings-only.
            settings = {k: flat[k] for k in SETTING_KEYS if k in flat}
            hist, idx, marks, _ = _load_session_cache()
            _persist_session(hist, idx, marks, settings)
            updates = _setting_updates(settings)
            input_on = bool(settings.get("input_image_on", False))
            updates.append(gr.update(visible=input_on))
            updates.append(f"Loaded preset '{parsed.get('name')}' (settings only)")
            return updates

        save_preset_btn.click(
            _export_preset,
            inputs=[preset_name, *setting_controls],
            outputs=[preset_file_out, preset_status],
        )
        load_preset_file.change(
            _import_preset,
            inputs=[load_preset_file],
            outputs=[*setting_controls, image_panel, preset_status],
        )

        def _autosave_settings(*vals):
            values = {k: v for k, v in zip(SETTING_KEYS, vals)}
            hist, idx, marks, _ = _load_session_cache()
            _persist_session(hist, idx, marks, values)

        for _ctrl in setting_controls:
            _ctrl.change(
                _autosave_settings,
                inputs=setting_controls,
                queue=False,
                show_progress="hidden",
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

        def _hold():
            """No-op updates while a job is queued/running (preserve thumbs + marks)."""
            return (
                gr.update(),  # history
                gr.update(),  # index
                gr.update(),  # thumbs
                gr.update(),  # viewer
                gr.update(),  # download
                gr.update(),  # nav
                gr.update(),  # prev
                gr.update(),  # next
                gr.update(),  # picked
                gr.update(),  # pick_box
                gr.update(),  # pick_status
            )

        def _empty_viewer():
            bundle = _viewer_bundle([], 0, [])
            return (
                *bundle,
                "Cleared.",
                "Idle.",
                gr.update(visible=False),
                None,
                "0 / 0",
            )

        def _run_job(history, index, picked, *args):
            """Keep every queued Generate; append results to session history."""
            tip = (args[0] or "").strip().replace("\n", " ") if args else ""
            if len(tip) > 80:
                tip = tip[:77] + "..."
            hist = _alive_paths(history)
            marks = list(picked or [])
            yield (
                *_hold(),
                gr.update(),  # status
                f"In queue / running: {tip or '(image tools)'} · kept {len(hist)} image(s)",
                gr.update(),
                gr.update(),
                gr.update(),
            )
            try:
                paths, info = generate(*args)
            except Exception as exc:  # noqa: BLE001
                bundle = _viewer_bundle(hist, index, marks)
                yield (
                    *bundle,
                    f"Failed: {exc}",
                    f"Failed · history still has {len(hist)} image(s).",
                    gr.update(),
                    gr.update(),
                    gr.update(),
                )
                return

            new_paths = _alive_paths(list(paths or []))
            if not new_paths:
                bundle = _viewer_bundle(hist, index, marks)
                yield (
                    *bundle,
                    "Worker returned no files.",
                    "Failed · empty result.",
                    gr.update(),
                    gr.update(),
                    gr.update(),
                )
                return

            merged = (hist + new_paths)[-MAX_HISTORY:]
            # Drop marks that fell off the MAX_HISTORY window.
            alive = set(merged)
            marks = [p for p in marks if p in alive]
            new_index = max(0, len(merged) - len(new_paths))
            bundle = _viewer_bundle(merged, new_index, marks)
            yield (
                *bundle,
                info,
                f"Done · +{len(new_paths)} · session {len(merged)} image(s). {info}",
                gr.update(),
                bundle[3],
                bundle[5],
            )

        def _step(history, index, picked, delta: int):
            hist = _alive_paths(history)
            if not hist:
                return _viewer_bundle([], 0, [])
            idx = (int(index) + delta) % len(hist)
            return _viewer_bundle(hist, idx, picked)

        def _pick(evt: gr.SelectData, history, index, picked):
            hist = _alive_paths(history)
            if not hist:
                return _viewer_bundle([], 0, [])
            raw = evt.index
            if isinstance(raw, (list, tuple)) and raw:
                raw = raw[0]
            try:
                idx = int(raw)
            except Exception:
                idx = int(index or 0)
            return _viewer_bundle(hist, idx, picked)

        def _toggle_mark(history, index, picked):
            hist = _alive_paths(history)
            if not hist:
                return _viewer_bundle([], 0, [])
            idx = max(0, min(int(index or 0), len(hist) - 1))
            selected = hist[idx]
            marks = [p for p in _alive_paths(picked) if p in set(hist)]
            if selected in marks:
                marks = [p for p in marks if p != selected]
            else:
                marks.append(selected)
            return _viewer_bundle(hist, idx, marks)

        def _sync_marks(chosen, history, index):
            hist = _alive_paths(history)
            marks = [p for p in (chosen or []) if p in set(hist)]
            return _viewer_bundle(hist, index, marks)

        def _clear_marks(history, index):
            return _viewer_bundle(_alive_paths(history), index, [])

        def _download_marks(picked):
            try:
                return _zip_picked(picked)
            except Exception as exc:  # noqa: BLE001
                raise gr.Error(str(exc)) from exc

        def _restore_session():
            hist, idx, marks, settings = _load_session_cache()
            bundle = _viewer_bundle(hist, idx, marks)
            updates = _setting_updates(settings)
            input_on = bool(settings.get("input_image_on", False))
            updates.append(gr.update(visible=input_on))
            return (*bundle, *updates)

        def _open_fs(history, index):
            hist = _alive_paths(history)
            if not hist:
                return gr.update(visible=False), None, "0 / 0"
            idx = max(0, min(int(index or 0), len(hist) - 1))
            return gr.update(visible=True), hist[idx], _nav_label(idx, len(hist))

        def _close_fs():
            return gr.update(visible=False)

        def _fs_step(history, index, picked, delta: int):
            hist = _alive_paths(history)
            if not hist:
                empty = _viewer_bundle([], 0, [])
                return (*empty, gr.update(visible=True), None, "0 / 0")
            idx = (int(index) + delta) % len(hist)
            bundle = _viewer_bundle(hist, idx, picked)
            return (*bundle, gr.update(visible=True), hist[idx], bundle[5])

        viewer_outs = [
            history_state,
            index_state,
            thumbs,
            viewer,
            download_file,
            nav_label,
            prev_btn,
            next_btn,
            picked_state,
            pick_box,
            pick_status,
        ]

        # Flush settings before/with Generate so reload keeps the last prompt even
        # if Textbox change had not fired yet.
        go.click(
            _autosave_settings,
            inputs=setting_controls,
            queue=False,
            show_progress="hidden",
        )
        go.click(
            _run_job,
            inputs=[history_state, index_state, picked_state, *generate_inputs],
            outputs=[
                *viewer_outs,
                status,
                queue_status,
                fs_panel,
                fs_image,
                fs_nav,
            ],
            concurrency_limit=1,
            concurrency_id="generate-queue",
            trigger_mode="multiple",
            queue=True,
            show_progress="full",
        )

        clear_result.click(
            _empty_viewer,
            outputs=[*viewer_outs, status, queue_status, fs_panel, fs_image, fs_nav],
            queue=False,
        )
        prev_btn.click(
            lambda h, i, p: _step(h, i, p, -1),
            inputs=[history_state, index_state, picked_state],
            outputs=viewer_outs,
            queue=False,
        )
        next_btn.click(
            lambda h, i, p: _step(h, i, p, 1),
            inputs=[history_state, index_state, picked_state],
            outputs=viewer_outs,
            queue=False,
        )
        thumbs.select(
            _pick,
            inputs=[history_state, index_state, picked_state],
            outputs=viewer_outs,
            queue=False,
        )
        mark_btn.click(
            _toggle_mark,
            inputs=[history_state, index_state, picked_state],
            outputs=viewer_outs,
            queue=False,
        )
        pick_box.change(
            _sync_marks,
            inputs=[pick_box, history_state, index_state],
            outputs=viewer_outs,
            queue=False,
        )
        clear_marks_btn.click(
            _clear_marks,
            inputs=[history_state, index_state],
            outputs=viewer_outs,
            queue=False,
        )
        download_zip_btn.click(
            _download_marks,
            inputs=[picked_state],
            outputs=[zip_file],
            queue=False,
        )
        demo.load(
            _restore_session,
            outputs=[*viewer_outs, *setting_controls, image_panel],
            queue=False,
        )
        fs_open.click(
            _open_fs,
            inputs=[history_state, index_state],
            outputs=[fs_panel, fs_image, fs_nav],
            queue=False,
        )
        fs_close.click(_close_fs, outputs=[fs_panel], queue=False)
        fs_prev.click(
            lambda h, i, p: _fs_step(h, i, p, -1),
            inputs=[history_state, index_state, picked_state],
            outputs=[*viewer_outs, fs_panel, fs_image, fs_nav],
            queue=False,
        )
        fs_next.click(
            lambda h, i, p: _fs_step(h, i, p, 1),
            inputs=[history_state, index_state, picked_state],
            outputs=[*viewer_outs, fs_panel, fs_image, fs_nav],
            queue=False,
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
    # max_size keeps many queued Generate clicks; concurrency on the event is 1.
    demo.queue(api_open=False, default_concurrency_limit=8, max_size=32).launch(
        server_name=HOST,
        server_port=PORT,
        share=False,
        show_api=False,
        inbrowser=False,
    )


if __name__ == "__main__":
    main()
