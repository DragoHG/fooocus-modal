# User guide

How to run **fooocus-modal** as an end user: local studio UI, on-demand Modal GPU, presets, and inpaint/outpaint.

## What this product does

You work in a local Gradio app. When you click **Generate**, a Modal GPU worker runs Fooocus, returns images to your machine, then scales to zero after a short idle window.

By default (`ZERO_TELEMETRY=true`), generation media is not kept on the Modal Volume—only models live there.

## Install and first run

```bash
cp .env.example .env
cp models.txt.example models.txt

uv venv .venv && source .venv/bin/activate
uv pip install -r requirements-local.txt

modal token new
modal run modal_app/app.py --action sync
modal deploy modal_app/app.py
python local/ui.py
```

Open [http://127.0.0.1:7860](http://127.0.0.1:7860).

| Step | Expectation |
|------|-------------|
| First Generate after idle | ~1–2 minutes (cold start + model load) |
| Warm Lightning job | Much faster |
| Stuck **Running** with no logs | Cancel the Modal call and retry |

## Studio UI

- **Sticky Generate** — prompt and Generate stay at the top; jobs queue one after another.
- **Results** — session gallery with Prev/Next; click the selected image for fullscreen (Esc or click outside to close).
- **Mark / ZIP** — mark favorites and download them as a ZIP.
- **Reload persistence** — prompt, settings, marks, and gallery restore after refresh while files remain under `outputs/` (`outputs/.session_cache.json`).
- **Presets JSON** — download/upload settings only (no input images). A live copy is also written to `outputs/presets/last-session.json`.

### Input Image

Enable **Input Image**, then pick a tab:

| Tab | Use |
|-----|-----|
| Upscale or Variation | Vary / upscale a source image |
| Image Prompt | FaceSwap, ImagePrompt, PyraCanny, CPDS |
| Inpaint or Outpaint | Paint a mask or expand edges |
| Enhance | Extra enhance pass |

### Inpaint / Outpaint (Fooocus-style)

1. Upload an image into the editor.
2. Paint the region to change with the **white brush** (eraser removes paint).
3. Or use **Mask entire image** / **Invert brush mask** / **Clear brush mask**.
4. Choose **Method**:
   - **Inpaint or Outpaint (default)** — general edits + outpaint directions
   - **Improve Detail** — faces/hands/eyes; lower strength; additional prompt
   - **Modify Content** — stronger content change; additional prompt
5. Optional: **Enable advanced masking** to upload a separate mask, invert it, or erode/dilate.
6. Outpaint: tick Left / Right / Top / Bottom.

Toolbar buttons on the editor and result panel use dark backgrounds so they stay readable over bright images.

## Important environment flags

See `.env.example` for the full list. Common ones:

| Variable | Default | Meaning |
|----------|---------|---------|
| `ZERO_TELEMETRY` | `true` | Keep generation media off the Volume |
| `SCALEDOWN_WINDOW` | `15` | Seconds idle before the GPU stops |
| `GENERATE_TIMEOUT` | `600` | Max seconds for one generate |
| `ENABLE_MEMORY_SNAPSHOT` | `false` | Keep off with Fooocus |
| `MODAL_GPUS` | `L4,A10` | GPU preference order |
| `LOCAL_OUTPUT_DIR` | `./outputs` | Where images and session cache live |

## Models

Edit `models.txt` (from the example), then:

```bash
modal run modal_app/app.py --action sync
```

Do not commit private download URLs or tokens.

## Cost tips

- Prefer **Lightning** / shorter runs while testing.
- Keep `SCALEDOWN_WINDOW` short.
- Leave memory snapshots disabled.
- Stop hung Modal containers from the Modal dashboard if needed.

## More reading

- [Architecture overview](architecture/OVERVIEW.md)
- [Cold start / FinOps](architecture/COLD_START.md)
- [ZERO_TELEMETRY](architecture/ZERO_TELEMETRY.md)
- [Verification](architecture/VERIFICATION.md)
- [Changelog](audit/CHANGELOG.md)
- [Contributing](../CONTRIBUTING.md)
