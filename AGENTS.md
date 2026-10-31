# Agent guide — fooocus-modal

This repository (`fooocus-modal`, https://github.com/DragoHG/fooocus-modal) runs Fooocus inference on Modal (serverless GPU) with a local Gradio UI.
Agents working here must follow project rules under `.cursor/rules/` and skills under `.cursor/skills/`.

**Project author:** Fabio "Drago" Monreal · fabio.monreal@outlook.com · https://www.linkedin.com/in/fabiomonreal/ · https://fabio-monreal.vercel.app/en (public website)

## Mission

Deliver a FinOps-first Fooocus worker: local UI triggers on-demand GPU work; idle scales to zero; models live on a Modal Volume; optional ephemeral I/O via `ZERO_TELEMETRY`.

## Read first

1. [docs/architecture/OVERVIEW.md](docs/architecture/OVERVIEW.md)
2. [docs/governance/POLICY.md](docs/governance/POLICY.md)
3. [docs/audit/CHANGELOG.md](docs/audit/CHANGELOG.md)
4. Active plan archive: [`.cursor/planx/`](.cursor/planx/)

## Non-negotiables

- Do not implement runtime application code until the structural/governance layer for that slice is in place.
- Do not `git push` unless the maintainer explicitly requests it.
- Commits must attribute to `DragoHG <fabio.monreal@outlook.com>` only.
- Keep source, commits, and docs free of IDE/assistant/tooling provenance noise.
- After meaningful changes, append an entry to `docs/audit/CHANGELOG.md`.
- When a plan is created or revised, archive a copy under `.cursor/planx/`.

## Layout (target)

| Path | Role |
|------|------|
| `local/` | CPU Gradio UI |
| `modal_app/` | Modal Image, Volume, worker class |
| `src/` | Shared helpers (manifest, paths, params) |
| `config/` | Fooocus path templates |
| `docs/` | Architecture, governance, audit trail |
| `.cursor/rules/` | Persistent agent rules |
| `.cursor/skills/` | Repeatable workflows |
| `.cursor/planx/` | Archived plans |

## Config surface

See `.env.example`. Key flag: `ZERO_TELEMETRY` (default `true`) — when enabled, do not persist generation inputs/outputs on the Modal Volume.
