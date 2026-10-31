# Local UI

Gradio studio that talks to the deployed Modal `FooocusWorker`.

```bash
python local/ui.py
```

Open `http://127.0.0.1:7860`.

End-user details: [docs/USER_GUIDE.md](../docs/USER_GUIDE.md).

## Features

- Prompt, styles, performance, aspect, seed, sharpness, guidance
- Checkpoint, refiner, five LoRAs
- Sampling and guidance overrides
- Input Image: Upscale/Vary, Image Prompt (FaceSwap), Inpaint/Outpaint (brush mask + Method), Enhance
- Presets: download/upload JSON for prompt + settings (never embeds input images); `outputs/presets/last-session.json`
- Results: mark favorites for ZIP; fullscreen with sticky controls; gallery + settings restore via `outputs/.session_cache.json`

Results save under `LOCAL_OUTPUT_DIR` (default `./outputs`).
