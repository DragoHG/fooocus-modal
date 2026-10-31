# Audit changelog

Newest entries first. Format enforced by skill `audit-trail`.

## [Unreleased]

### 2026-10-30 — Runtime worker, sync, and local UI

- **What:** Implemented shared path/manifest/params helpers, Modal `FooocusWorker` + `sync_models`, Fooocus headless task runner, and local Gradio UI calling `.remote()`.
- **Why:** Deliver on-demand FinOps generation path after phase-0 governance.
- **Paths:** `src/`, `modal_app/app.py`, `modal_app/bootstrap.py`, `local/ui.py`, `tests/test_manifest.py`, `README.md`, `models.txt.example`
- **Plans:** `.cursor/planx/20261030-2225-runtime-implementation.md`

### 2026-10-30 — Executive public copy and Website attribution

- **What:** Rewrote public-facing README/CONTRIBUTING/SECURITY/AUTHORS with executive tone; labeled the personal site as Website (not curriculum); aligned architecture/governance wording and Volume name in diagrams.
- **Why:** Clearer product narrative for GitHub visitors while keeping agent docs operational.
- **Paths:** `README.md`, `AUTHORS.md`, `CONTRIBUTING.md`, `SECURITY.md`, `docs/architecture/OVERVIEW.md`, `docs/architecture/ZERO_TELEMETRY.md`, `docs/governance/POLICY.md`, `AGENTS.md`

### 2026-10-30 — Align author and canonical GitHub remote

- **What:** Set project author to Fabio "Drago" Monreal (email + LinkedIn), renamed identity to `fooocus-modal`, pointed canonical remote to `https://github.com/DragoHG/fooocus-modal`.
- **Why:** Match the published empty GitHub repository and public attribution requested by the maintainer.
- **Paths:** `README.md`, `LICENSE`, `.env.example`, `AGENTS.md`, `CONTRIBUTING.md`, `SECURITY.md`, `docs/`, `.cursor/rules/00-core.mdc`, `.cursor/skills/project-bootstrap/SKILL.md`, `.cursor/planx/20261030-2215-author-and-remote.md`
- **Plans:** `.cursor/planx/20261030-2215-author-and-remote.md`

### 2026-10-30 — GitHub open-source bootstrap (fooocus-on-modal)

- **What:** Renamed project identity to `fooocus-on-modal`, added MIT `LICENSE`, `SECURITY.md`, GitHub PR/issue templates, refreshed README/CONTRIBUTING for public OSS, and aligned Modal app/volume defaults.
- **Why:** Prepare the canonical public GitHub repository and first maintainer commit.
- **Paths:** `LICENSE`, `SECURITY.md`, `README.md`, `CONTRIBUTING.md`, `.env.example`, `AGENTS.md`, `docs/architecture/*`, `.github/`, `.cursor/planx/20261030-2210-github-oss-bootstrap.md`, `.cursor/rules/00-core.mdc`, `.cursor/skills/project-bootstrap/SKILL.md`
- **Plans:** `.cursor/planx/20261030-2210-github-oss-bootstrap.md`

### 2026-10-30 — Phase 0 governance and structural scaffold

- **What:** Created repository skeleton with architecture docs, lightweight governance policy, agent rules/skills, planx archive, env template using `ZERO_TELEMETRY`, gitignore, and package placeholders without runtime worker/UI code.
- **Why:** Establish FinOps-oriented architecture, contribution hygiene, auditability, and plan archival before implementing Modal/Fooocus runtime.
- **Paths:** `AGENTS.md`, `README.md`, `CONTRIBUTING.md`, `.env.example`, `.gitignore`, `models.txt.example`, `docs/`, `.cursor/rules/`, `.cursor/skills/`, `.cursor/planx/`, `src/README.md`, `modal_app/README.md`, `local/README.md`, `config/README.md`, `outputs/.gitkeep`
- **Plans:** `.cursor/planx/20261030-2158-fooocus-modal-worker.md`, `.cursor/planx/20261030-2200-phase0-governance-scaffold.md`

### 2026-10-30 — Rename I/O retention flag to ZERO_TELEMETRY

- **What:** Adopted `ZERO_TELEMETRY` as the env switch controlling whether generation inputs/outputs may be stored on the Modal Volume (default `true` = no media retention on Volume).
- **Why:** Clearer FinOps/privacy naming for ephemeral generation artifacts while keeping model weights durable on the Volume.
- **Paths:** `.env.example`, `docs/architecture/OVERVIEW.md`, `.cursor/rules/20-finops-modal.mdc`, `.cursor/planx/20261030-2158-fooocus-modal-worker.md`
