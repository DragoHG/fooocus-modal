# fooocus-modal

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

**Fooocus quality. Modal economics.** Generate from a local app; the GPU wakes for the job and sleeps when you stop. Idle time does not keep a bill running.

Models stay on cloud storage. Your images stay on your machine by default.

## Author

**Fabio "Drago" Monreal**  
[Email](mailto:fabio.monreal@outlook.com) · [LinkedIn](https://www.linkedin.com/in/fabiomonreal/) · [Website](https://fabio-monreal.vercel.app/en) · [GitHub](https://github.com/DragoHG) · [Repository](https://github.com/DragoHG/fooocus-modal)

## What you get

- Local studio UI with Fooocus-style controls (text, styles, LoRAs, FaceSwap, inpaint, outpaint, enhance)
- Advanced sampling knobs when you want them (sampler, scheduler, CLIP skip, ADM, adaptive CFG)
- **Preset JSON**: download your setup, upload it later to restore the same look
- On-demand GPU (`L4` then `A10`) with scale-to-zero
- Optional zero retention of generation media in the cloud (`ZERO_TELEMETRY`)

## Quick start

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

Open `http://127.0.0.1:7860`. Use **Presets** in the UI to download or upload a JSON settings file.

| Variable | Default | Meaning |
|----------|---------|---------|
| `ZERO_TELEMETRY` | `true` | Keep generation media off the Volume |
| `SCALEDOWN_WINDOW` | `60` | Seconds idle before the GPU stops |
| `ENABLE_MEMORY_SNAPSHOT` | `true` | Faster cold start |
| `MODAL_GPUS` | `L4,A10` | GPU preference order |
| `MODAL_APP_NAME` | `fooocus-modal` | Modal app name |

## Documentation

- [Architecture](docs/architecture/OVERVIEW.md)
- [Cold start](docs/architecture/COLD_START.md)
- [Directory map](docs/architecture/DIRECTORY.md)
- [ZERO_TELEMETRY](docs/architecture/ZERO_TELEMETRY.md)
- [Product principles](docs/governance/POLICY.md)
- [Changelog](docs/audit/CHANGELOG.md)
- [Contributing](CONTRIBUTING.md)
- [Security](SECURITY.md)

## License

MIT - see [LICENSE](LICENSE).

## Acknowledgements

- [Fooocus](https://github.com/lllyasviel/Fooocus) by lllyasviel
- [Modal](https://modal.com) for serverless GPUs
