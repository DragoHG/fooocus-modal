# Architecture overview

High-level design for **fooocus-modal**: local Gradio UI + Modal serverless GPU worker for Fooocus, optimized for FinOps.

**Author:** Fabio "Drago" Monreal ([LinkedIn](https://www.linkedin.com/in/fabiomonreal/), fabio.monreal@outlook.com).

## Goals

- On-demand GPU: cost accrues only while a container runs.
- Persistent models on a Modal Volume; media retention optional.
- Maintainer-controlled model set via local `models.txt` (not committed).
- Clear separation between local CPU UX and remote inference.

## Context diagram

```mermaid
flowchart LR
  subgraph workstation [Workstation]
    UI[local Gradio]
    Manifest[models.txt]
    EnvFile[.env]
  end
  subgraph modalPlatform [Modal]
    Worker[FooocusWorker]
    Vol[Volume fooocus-data]
  end
  UI -->|generate remote| Worker
  Manifest -->|sync_models| Vol
  Worker --> Vol
  Worker -->|image bytes| UI
  EnvFile -.->|config| UI
  EnvFile -.->|config| Worker
```

## Runtime lifecycle

1. User clicks **Generate** in the local UI.
2. Client calls the deployed Modal class method (cold start if idle).
3. Worker reads checkpoints/LoRAs from the Volume, runs Fooocus headless, returns bytes.
4. After `SCALEDOWN_WINDOW` with no work, containers scale to zero — GPU billing stops.
5. Volume storage for models remains; with `ZERO_TELEMETRY=true`, generation media is not kept on the Volume.

## Components (planned)

| Component | Responsibility |
|-----------|----------------|
| `local/ui.py` | Gradio controls; Modal client; local preview/save |
| `modal_app/app.py` | Image build, Volume mount, worker class, `sync_models` |
| `src/manifest.py` | Parse/download model manifest into Volume folders |
| `src/paths.py` | Volume layout + `ZERO_TELEMETRY` path selection |
| `src/generate_params.py` | Shared request/response schema |
| `config/` | Fooocus path configuration templates |

## Configuration

See `.env.example`. Notable keys:

- `MODAL_GPUS` — ordered fallback list (default `L4,A10`)
- `SCALEDOWN_WINDOW` — idle seconds before scale-down (default `60`)
- `ZERO_TELEMETRY` — when `true`, do not persist inputs/outputs on the Volume
- `VOLUME_NAME` / `MODAL_APP_NAME` — Modal resource names

## Non-goals (phase 0)

- Always-on Gradio hosted on GPU
- Baking multi-GB weights into the container image
- Multi-tenant auth/billing portals
