# fooocus-modal

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

**Fooocus on Modal, built for cost control.** Run a local interface, fire GPU jobs only when you generate, and shut the worker down when you stop—so idle time does not burn budget.

Models stay on a Modal Volume. Generation media does not have to. Defaults favor FinOps: scale to zero, short idle window, optional zero retention of inputs and outputs on disk.

> **Status:** Runtime scaffold ready — sync models, deploy worker, run local UI. First GPU generation requires Modal auth + `models.txt`.

## Author

**Fabio "Drago" Monreal**  
[Email](mailto:fabio.monreal@outlook.com) · [LinkedIn](https://www.linkedin.com/in/fabiomonreal/) · [Website](https://fabio-monreal.vercel.app/en) · [GitHub](https://github.com/DragoHG) · [Repository](https://github.com/DragoHG/fooocus-modal)

## Why this project

- Pay for GPU only while work is running
- Keep checkpoints and LoRAs durable; keep media ephemeral by default
- Operate from your laptop UI; leave heavy compute on Modal
- Stay configurable: GPU fallback list, idle window, retention flag

## Capabilities

- Local Gradio UI calling an on-demand Modal worker
- GPU preference `L4` → `A10` (24GB class), overridable
- Custom model set via private `models.txt` (not committed)
- `ZERO_TELEMETRY=true` by default — no generation I/O retained on the Volume

## Quick start

```bash
cp .env.example .env
cp models.txt.example models.txt
# uncomment / add checkpoint + LoRA URLs in models.txt

pip install -r requirements-local.txt
modal setup   # once per machine

# 1) Download models into the Modal Volume (CPU)
modal run modal_app/app.py --action sync

# 2) Deploy the GPU worker (scales to zero when idle)
modal deploy modal_app/app.py

# 3) Local UI
python local/ui.py
```

Open `http://127.0.0.1:7860`, enter a prompt, click **Generate**. The first call may cold-start the GPU; after ~`SCALEDOWN_WINDOW` seconds idle, the worker stops billing compute.

| Variable | Default | Meaning |
|----------|---------|---------|
| `ZERO_TELEMETRY` | `true` | Do not store inputs/outputs on the Volume |
| `SCALEDOWN_WINDOW` | `60` | Idle seconds before GPU scale-down |
| `MODAL_GPUS` | `L4,A10` | Ordered GPU fallback list |
| `MODAL_APP_NAME` | `fooocus-modal` | Modal app name |

## Documentation

- [Architecture overview](docs/architecture/OVERVIEW.md)
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
