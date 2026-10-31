# fooocus-modal

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

**Fooocus on Modal, built for cost control.** Run a local interface, fire GPU jobs only when you generate, and shut the worker down when you stop—so idle time does not burn budget.

Models stay on a Modal Volume. Generation media does not have to. Defaults favor FinOps: scale to zero, short idle window, optional zero retention of inputs and outputs on disk.

> **Status:** Runtime ready — Fooocus-parity local UI, lean Modal worker, Volume sync. Requires Modal token once per machine.

## Author

**Fabio "Drago" Monreal**  
[Email](mailto:fabio.monreal@outlook.com) · [LinkedIn](https://www.linkedin.com/in/fabiomonreal/) · [Website](https://fabio-monreal.vercel.app/en) · [GitHub](https://github.com/DragoHG) · [Repository](https://github.com/DragoHG/fooocus-modal)

## Why this project

- Pay for GPU only while work is running
- Keep checkpoints and LoRAs durable; keep media ephemeral by default
- Operate from your laptop UI; leave heavy compute on Modal
- Stay configurable: GPU fallback list, idle window, retention flag

## Capabilities

- Local Fooocus-style UI → lean Modal GPU worker (no Gradio on Modal)
- Input Image: Upscale/Vary, Image Prompt (**FaceSwap**, Canny, CPDS), Inpaint/Outpaint, Enhance
- GPU preference `L4` → `A10`; memory snapshots for faster cold starts (`ENABLE_MEMORY_SNAPSHOT`)
- Custom models via private `models.txt` (default light LoRA + Juggernaut + IP-Adapter assets)
- `ZERO_TELEMETRY=true` by default — no generation I/O retained on the Volume
- Default performance **Lightning** for cheaper/faster generations

## Quick start

```bash
cp .env.example .env
cp models.txt.example models.txt   # or edit models.txt

# Prefer a venv (example with uv)
uv venv .venv && source .venv/bin/activate
uv pip install -r requirements-local.txt

# Auth once
modal token new

# 1) Download models into the Modal Volume (CPU)
modal run modal_app/app.py --action sync

# 2) Deploy the GPU worker (scales to zero when idle)
modal deploy modal_app/app.py

# 3) Local UI
python local/ui.py
```

Open `http://127.0.0.1:7860`. Enable **Input Image** for Fooocus image tools. The first Generate after idle may cold-start; after ~`SCALEDOWN_WINDOW` seconds idle, GPU billing stops.

| Variable | Default | Meaning |
|----------|---------|---------|
| `ZERO_TELEMETRY` | `true` | Do not store inputs/outputs on the Volume |
| `SCALEDOWN_WINDOW` | `60` | Idle seconds before GPU scale-down |
| `ENABLE_MEMORY_SNAPSHOT` | `true` | Faster cold restore of imports |
| `ENABLE_GPU_SNAPSHOT` | `false` | Experimental VRAM snapshot (usually off) |
| `MODAL_GPUS` | `L4,A10` | Ordered GPU fallback list |
| `MODAL_APP_NAME` | `fooocus-modal` | Modal app name |

## Documentation

- [Architecture overview](docs/architecture/OVERVIEW.md)
- [Cold start](docs/architecture/COLD_START.md)
- [Directory map](docs/architecture/DIRECTORY.md)
- [ZERO_TELEMETRY](docs/architecture/ZERO_TELEMETRY.md)
- [Governance](docs/governance/POLICY.md)
- [Audit changelog](docs/audit/CHANGELOG.md)
- [Contributing](CONTRIBUTING.md)
- [Security](SECURITY.md)

## License

MIT — see [LICENSE](LICENSE).

## Acknowledgements

- [Fooocus](https://github.com/lllyasviel/Fooocus) by lllyasviel
- [Modal](https://modal.com) for serverless GPUs
