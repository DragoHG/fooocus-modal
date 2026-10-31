# fooocus-modal

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

Local Gradio UI for Fooocus-style image generation, backed by a **Modal** serverless GPU worker. Models live on a Modal Volume; the worker **scales to zero** when idle so you only pay for active compute.

> **Status:** Phase 0 — structural and governance scaffold. Runtime worker/UI code is not implemented yet.

## Author

**Fabio "Drago" Monreal**  
Email: [fabio.monreal@outlook.com](mailto:fabio.monreal@outlook.com)  
LinkedIn: [linkedin.com/in/fabiomonreal](https://www.linkedin.com/in/fabiomonreal/)  
GitHub: [DragoHG](https://github.com/DragoHG) · [fooocus-modal](https://github.com/DragoHG/fooocus-modal)

## Features (planned)

- Local CPU UI → on-demand Modal GPU inference
- FinOps defaults: `min_containers=0`, short `SCALEDOWN_WINDOW`
- GPU preference `L4` → `A10` (24GB class), configurable
- Custom checkpoints / LoRAs via gitignored `models.txt`
- `ZERO_TELEMETRY=true` by default (no generation media retained on the Volume)

## Docs

- [Architecture overview](docs/architecture/OVERVIEW.md)
- [Directory map](docs/architecture/DIRECTORY.md)
- [ZERO_TELEMETRY](docs/architecture/ZERO_TELEMETRY.md)
- [Governance](docs/governance/POLICY.md)
- [Audit changelog](docs/audit/CHANGELOG.md)
- [Contributing](CONTRIBUTING.md)
- [Security](SECURITY.md)
- [Agent guide](AGENTS.md)

## Quick start (after runtime lands)

```bash
cp .env.example .env
cp models.txt.example models.txt
# edit models.txt with your download URLs
pip install -r requirements-local.txt
# modal setup && modal deploy ... && python local/ui.py
```

Config highlights from `.env.example`:

| Variable | Default | Meaning |
|----------|---------|---------|
| `ZERO_TELEMETRY` | `true` | Do not store inputs/outputs on the Volume |
| `SCALEDOWN_WINDOW` | `60` | Idle seconds before GPU scale-down |
| `MODAL_GPUS` | `L4,A10` | Ordered GPU fallback list |
| `MODAL_APP_NAME` | `fooocus-modal` | Modal app name |

## Layout

See [docs/architecture/DIRECTORY.md](docs/architecture/DIRECTORY.md).

## License

MIT — see [LICENSE](LICENSE).

## Acknowledgements

- [Fooocus](https://github.com/lllyasviel/Fooocus) by lllyasviel
- [Modal](https://modal.com) for serverless GPUs
