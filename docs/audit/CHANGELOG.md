# Audit changelog

Newest entries first. Format enforced by skill `audit-trail`.

## [Unreleased]

### 2026-10-30 - Stop GPU burn from snapshots and list_assets

- **What:** Hard-disabled memory snapshots (Fooocus CUDA init fails in CPU snap enter and retries); moved `list_assets` to a CPU Modal function; shortened scale-down; headless Gradio stub; documented cost traps and verification (one Lightning generate OK).
- **Why:** Logs showed `No CUDA GPUs are available` on snap enter plus GPU wakes just to list files, leaving expensive Running containers.
- **Paths:** `modal_app/app.py`, `modal_app/bootstrap.py`, `local/ui.py`, `.env.example`, `docs/architecture/COLD_START.md`, `docs/architecture/VERIFICATION.md`, `README.md`
- **Plans:** `.cursor/planx/20261030-2343-finops-cuda-fix.md`

### 2026-10-30 - Fix prompt-expansion tokenizer on Volume

- **What:** Worker bootstrap now copies Fooocus expansion tokenizer/config sidecars into the Volume path (weights alone were not enough); generation aborts if the Fooocus worker thread dies or times out instead of hanging forever.
- **Why:** Missing `config.json` crashed the worker mid-generate while the Modal call stayed Running and kept the GPU billed.
- **Paths:** `modal_app/bootstrap.py`, `src/fooocus_task.py`, `models.txt.example`

### 2026-10-30 - Studio presets and public product copy

- **What:** Expanded local UI with sampling/guidance controls and JSON preset download/upload; rewrote README, CONTRIBUTING, and governance docs for end-user product language (removed public maintainer-process jargon); added preset unit tests; made Volume path helpers read env at call time.
- **Why:** Users need fuller creative controls and portable settings, with public docs that read as a product, not an internal ops handbook.
- **Paths:** `local/ui.py`, `local/presets.py`, `tests/test_presets.py`, `tests/test_paths.py`, `src/paths.py`, `README.md`, `CONTRIBUTING.md`, `docs/governance/`, `docs/architecture/OVERVIEW.md`
- **Plans:** `.cursor/planx/20261030-2325-ui-presets-product-copy.md`

### 2026-10-30 - Drop em dashes from repo copy

- **What:** Replaced em/en dashes and curly ellipsis in tracked docs, comments, and UI strings with ASCII `-` / `...`; noted the preference in core rules and contribution hygiene; authorship check now rejects those glyphs in commit messages.
- **Why:** Keep public copy free of that punctuation habit.
- **Paths:** `README.md`, `docs/`, `AGENTS.md`, `local/ui.py`, `modal_app/`, `.env.example`, `models.txt.example`, `.cursor/`, `.githooks/pre-push`, `scripts/check_git_authorship.sh`

### 2026-10-30 - Authorship push gate

- **What:** Added `scripts/check_git_authorship.sh` and versioned `.githooks` (`prepare-commit-msg`, `commit-msg`, `pre-push`) that strip/reject tooling co-author trailers and block pushes unless author/committer is `DragoHG <fabio.monreal@outlook.com>`; tightened the authorship rule, release-hygiene skill, and CONTRIBUTING.
- **Why:** Canonical history and the GitHub contributor surface must never publish non-maintainer tooling attribution.
- **Paths:** `scripts/check_git_authorship.sh`, `.githooks/`, `.cursor/rules/10-git-authorship.mdc`, `.cursor/skills/release-hygiene/SKILL.md`, `CONTRIBUTING.md`
- **Plans:** `.cursor/planx/20261030-2317-authorship-push-gate.md`

### 2026-10-30 - Sole-maintainer commit history hygiene

- **What:** Rewrote published `main` commit messages to remove unintended co-author trailers; tightened the authorship rule to require a clean message body before push.
- **Why:** Public history must attribute only `DragoHG <fabio.monreal@outlook.com>`.
- **Paths:** `.cursor/rules/10-git-authorship.mdc`

### 2026-10-30 - Docs for cold start and auth quickstart

- **What:** Added cold-start architecture note; refreshed README quickstart (venv, `modal token new`, snapshot env vars).
- **Why:** Document FinOps cold-start knobs and first-time Modal auth before sync/deploy.
- **Paths:** `README.md`, `docs/architecture/COLD_START.md`, `.env.example`

### 2026-10-30 - Full Fooocus image tools + lean cold start

- **What:** Expanded local UI (Upscale/Vary, Image Prompt/FaceSwap, Inpaint/Outpaint, Enhance, 5 LoRAs); wired image params through the worker; enabled memory snapshots and lean Modal bootstrap; refreshed model manifests with default checkpoint + light LoRA and IP-Adapter assets.
- **Why:** Match Fooocus feature surface while keeping Modal cold starts focused on inference-only backend.
- **Paths:** `local/ui.py`, `src/generate_params.py`, `src/fooocus_task.py`, `modal_app/app.py`, `modal_app/bootstrap.py`, `models.txt.example`, `.env.example`
- **Plans:** `.cursor/planx/20261030-2248-full-ui-coldstart.md`

### 2026-10-30 - Runtime worker, sync, and local UI

- **What:** Implemented shared path/manifest/params helpers, Modal `FooocusWorker` + `sync_models`, Fooocus headless task runner, and local Gradio UI calling `.remote()`.
- **Why:** Deliver on-demand FinOps generation path after phase-0 governance.
- **Paths:** `src/`, `modal_app/app.py`, `modal_app/bootstrap.py`, `local/ui.py`, `tests/test_manifest.py`, `README.md`, `models.txt.example`
- **Plans:** `.cursor/planx/20261030-2225-runtime-implementation.md`

### 2026-10-30 - Executive public copy and Website attribution

- **What:** Rewrote public-facing README/CONTRIBUTING/SECURITY/AUTHORS with executive tone; labeled the personal site as Website (not curriculum); aligned architecture/governance wording and Volume name in diagrams.
- **Why:** Clearer product narrative for GitHub visitors while keeping agent docs operational.
- **Paths:** `README.md`, `AUTHORS.md`, `CONTRIBUTING.md`, `SECURITY.md`, `docs/architecture/OVERVIEW.md`, `docs/architecture/ZERO_TELEMETRY.md`, `docs/governance/POLICY.md`, `AGENTS.md`

### 2026-10-30 - Align author and canonical GitHub remote

- **What:** Set project author to Fabio "Drago" Monreal (email + LinkedIn), renamed identity to `fooocus-modal`, pointed canonical remote to `https://github.com/DragoHG/fooocus-modal`.
- **Why:** Match the published empty GitHub repository and public attribution requested by the maintainer.
- **Paths:** `README.md`, `LICENSE`, `.env.example`, `AGENTS.md`, `CONTRIBUTING.md`, `SECURITY.md`, `docs/`, `.cursor/rules/00-core.mdc`, `.cursor/skills/project-bootstrap/SKILL.md`, `.cursor/planx/20261030-2215-author-and-remote.md`
- **Plans:** `.cursor/planx/20261030-2215-author-and-remote.md`

### 2026-10-30 - GitHub open-source bootstrap (fooocus-on-modal)

- **What:** Renamed project identity to `fooocus-on-modal`, added MIT `LICENSE`, `SECURITY.md`, GitHub PR/issue templates, refreshed README/CONTRIBUTING for public OSS, and aligned Modal app/volume defaults.
- **Why:** Prepare the canonical public GitHub repository and first maintainer commit.
- **Paths:** `LICENSE`, `SECURITY.md`, `README.md`, `CONTRIBUTING.md`, `.env.example`, `AGENTS.md`, `docs/architecture/*`, `.github/`, `.cursor/planx/20261030-2210-github-oss-bootstrap.md`, `.cursor/rules/00-core.mdc`, `.cursor/skills/project-bootstrap/SKILL.md`
- **Plans:** `.cursor/planx/20261030-2210-github-oss-bootstrap.md`

### 2026-10-30 - Phase 0 governance and structural scaffold

- **What:** Created repository skeleton with architecture docs, lightweight governance policy, agent rules/skills, planx archive, env template using `ZERO_TELEMETRY`, gitignore, and package placeholders without runtime worker/UI code.
- **Why:** Establish FinOps-oriented architecture, contribution hygiene, auditability, and plan archival before implementing Modal/Fooocus runtime.
- **Paths:** `AGENTS.md`, `README.md`, `CONTRIBUTING.md`, `.env.example`, `.gitignore`, `models.txt.example`, `docs/`, `.cursor/rules/`, `.cursor/skills/`, `.cursor/planx/`, `src/README.md`, `modal_app/README.md`, `local/README.md`, `config/README.md`, `outputs/.gitkeep`
- **Plans:** `.cursor/planx/20261030-2158-fooocus-modal-worker.md`, `.cursor/planx/20261030-2200-phase0-governance-scaffold.md`

### 2026-10-30 - Rename I/O retention flag to ZERO_TELEMETRY

- **What:** Adopted `ZERO_TELEMETRY` as the env switch controlling whether generation inputs/outputs may be stored on the Modal Volume (default `true` = no media retention on Volume).
- **Why:** Clearer FinOps/privacy naming for ephemeral generation artifacts while keeping model weights durable on the Volume.
- **Paths:** `.env.example`, `docs/architecture/OVERVIEW.md`, `.cursor/rules/20-finops-modal.mdc`, `.cursor/planx/20261030-2158-fooocus-modal-worker.md`
