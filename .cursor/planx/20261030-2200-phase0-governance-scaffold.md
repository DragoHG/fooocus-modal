---
name: Phase 0 governance scaffold
overview: Documentação de alto nível, regras, skills, planx, auditoria e templates - sem código runtime.
updated: 2026-10-30T22:00:00-03:00
status: done
---

# Phase 0 - governance and structure

## Scope

Create repository structure and agent governance before Fooocus/Modal runtime code.

## Deliverables

- `AGENTS.md`, `README.md`, `CONTRIBUTING.md`
- `docs/architecture/*`, `docs/governance/POLICY.md`, `docs/audit/CHANGELOG.md`
- `.cursor/rules/*.mdc` (core, git hygiene, finops, planx, audit, security)
- `.cursor/skills/{audit-trail,planx-archive,release-hygiene,project-bootstrap}`
- `.cursor/planx/` archive policy + seed plans
- `.env.example` with `ZERO_TELEMETRY`
- `.gitignore`, `models.txt.example`, package README stubs

## Out of scope

- `modal_app/app.py` implementation
- `local/ui.py` implementation
- Real model downloads / Modal deploy
