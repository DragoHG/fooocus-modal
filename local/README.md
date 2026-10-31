# Local UI

Gradio studio that talks to the deployed Modal `FooocusWorker`.

```bash
python local/ui.py
```

Open `http://127.0.0.1:7860`.

## Features

- Prompt, styles, performance, aspect, seed, sharpness, guidance
- Checkpoint, refiner, five LoRAs
- Sampling and guidance overrides
- Input Image: Upscale/Vary, Image Prompt (FaceSwap), Inpaint/Outpaint, Enhance
- **Presets**: download JSON settings; upload to restore (optional images)
- **Results**: mark favorites for ZIP download; click Selected for fullscreen; history/marks cache in the browser across reload

Results can be saved under `LOCAL_OUTPUT_DIR` (default `./outputs`). Presets land in `outputs/presets/`.
