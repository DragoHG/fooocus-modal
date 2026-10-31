# Cold start and FinOps

The Modal worker is inference-only: Fooocus `async_worker`, no Gradio server in the cloud.

## Cost traps (fixed / avoided)

| Trap | What happened | Mitigation |
|------|---------------|------------|
| CPU memory snapshot enter | `@enter(snap=True)` has **no GPU**; Fooocus import needs CUDA → `No CUDA GPUs are available`, retries, billed time | Snapshots hard-disabled in `modal_app/app.py` |
| `list_assets` on GPU class | Listing files woke an L4/A10 | `list_assets` is a **CPU** Modal function |
| Hung `generate` | Worker thread died (missing expansion tokenizer) but call stayed Running | Copy tokenizer sidecars; generation timeout; cancel stuck calls |
| Long idle window | GPU stayed warm after jobs | Default `SCALEDOWN_WINDOW=15`; use `modal app stop fooocus-modal` if a container stays live |

## Defaults

| Flag | Default | Effect |
|------|---------|--------|
| `ENABLE_MEMORY_SNAPSHOT` | `false` | Do not use (unsafe with Fooocus CUDA init) |
| `ENABLE_GPU_SNAPSHOT` | `false` | Leave off |
| `ENSURE_RUNTIME_ASSETS` | `true` | Copy/download tiny expansion + VAE-approx if missing |
| `SCALEDOWN_WINDOW` | `15` | Idle seconds before scale-to-zero |
| `GENERATE_TIMEOUT` | `600` | Max seconds for one generate |
| `ZERO_TELEMETRY` | `true` | Do not retain generation media on the Volume |

## Expected timings (ballpark)

1. `list_assets` (CPU): a few seconds
2. First `generate` after idle: container start + SDXL load + Lightning steps (often 1–3+ minutes on cold A10/L4)
3. After `SCALEDOWN_WINDOW` with no work: GPU billing stops

If a call is **Running** with no progress in the logs, **Cancel** it in the Modal UI. Do not leave zombie generates open.

## Auth once per machine

```bash
source .venv/bin/activate
modal token new
```
