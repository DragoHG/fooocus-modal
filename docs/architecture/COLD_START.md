# Cold start (FinOps)

The Modal worker is inference-only: Fooocus `async_worker`, no Gradio server in the cloud.

## Defaults

| Flag | Default | Effect |
|------|---------|--------|
| `ENABLE_MEMORY_SNAPSHOT` | `true` | Snapshot Python/Fooocus imports for faster container restore |
| `ENABLE_GPU_SNAPSHOT` | `false` | Optional VRAM snapshot (heavy for SDXL; usually leave off) |
| `ENSURE_RUNTIME_ASSETS` | `true` | Download tiny VAE-approx/expansion only if missing on the Volume |
| `SCALEDOWN_WINDOW` | `60` | Idle seconds before scale-to-zero |
| `ZERO_TELEMETRY` | `true` | Do not retain generation media on the Volume |

## Behavior

1. First request after idle may cold-start the container (snapshot restore when enabled).
2. Checkpoint weights load lazily from the Volume on first generate.
3. After `SCALEDOWN_WINDOW` with no work, GPU billing stops.

## Auth once per machine

```bash
source .venv/bin/activate
modal token new
```

Complete the browser URL Modal prints, then `modal run` / `modal deploy`.
