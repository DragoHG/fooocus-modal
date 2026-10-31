# ZERO_TELEMETRY

Controls whether **generation media** (inputs/outputs) is retained on the Modal Volume. Model weights are always durable on the Volume.

| Value | Behavior |
|-------|----------|
| `true` (default) | Ephemeral worker paths; image bytes returned to the local UI; no inputs/outputs kept on the Volume |
| `false` | Inputs/outputs may be written under Volume directories (durable; increases storage) |

## Unaffected

- Checkpoints, LoRAs, VAE, and related weights stay on the Volume in both modes
- Local saves under `./outputs` on the workstation are independent of this flag

## Logging

When `true`, do not log prompts or image payloads on the worker beyond what is required to serve the request.
