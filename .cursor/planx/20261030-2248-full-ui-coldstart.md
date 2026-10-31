---
name: Full UI and lean cold start
overview: Fooocus-parity local image tools + Modal memory snapshot / lean worker; default light LoRA and support models in manifest.
updated: 2026-10-30T22:48:00-03:00
status: done
---

# Full UI + cold start

## Cold start

- Modal worker: no Gradio server; `async_worker` only
- `ENABLE_MEMORY_SNAPSHOT=true` with `@modal.enter(snap=True)`
- `ENABLE_GPU_SNAPSHOT=false` by default (SDXL VRAM snapshots are heavy)
- Checkpoints load lazily on first generate
- Tiny assets skipped if already on Volume

## UI

Input Image tabs: Upscale/Vary, Image Prompt (FaceSwap etc.), Inpaint/Outpaint, Enhance.

## Models

- Default checkpoint: juggernautXL_v8Rundiffusion
- Default light LoRA: sd_xl_offset_example-lora_1.0
- IP-Adapter / clip_vision / inpaint / upscale URLs in models.txt.example
