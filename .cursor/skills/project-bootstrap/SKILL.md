---
name: project-bootstrap
description: Scaffold or extend fooocus-on-modal structural layers (docs, cursor rules/skills, env templates, package layout) before runtime code. Use when bootstrapping the repo, adding governance files, or when the user asks for structural/architectural setup first.
---

# Project bootstrap

## Order of work

1. Governance and agent surface (`.cursor/rules`, `.cursor/skills`, `AGENTS.md`)
2. Architecture docs (`docs/architecture/`)
3. Audit + planx seed
4. Env/templates (`.env.example`, `models.txt.example`, `.gitignore`)
5. Empty package placeholders (`src/`, `modal_app/`, `local/`, `config/`) with README stubs only
6. Runtime implementation (only when requested)

## Naming

- Ephemeral I/O flag: `ZERO_TELEMETRY`
- App name default: `fooocus-on-modal`
- Volume name default: `fooocus-on-modal-data`

## After bootstrap

Run skill `audit-trail` and archive any governing plan via `planx-archive`.
