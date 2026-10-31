# ZERO_TELEMETRY

Environment flag controlling retention of **generation media** (inputs/outputs) on the Modal Volume.

| Value | Behavior |
|-------|----------|
| `true` (default) | Worker uses ephemeral paths; returns image bytes to the local UI; does not keep inputs/outputs on the Volume. |
| `false` | Worker may write inputs/outputs under Volume directories (durable, increases storage). |

## Unaffected

- Model weights (checkpoints, LoRAs, VAE, etc.) remain on the Volume in both modes.
- Local saves under `./outputs` on the workstation are independent of this flag.

## Logging

When `true`, avoid logging prompts or image payloads on the worker beyond what is required to serve the request.
