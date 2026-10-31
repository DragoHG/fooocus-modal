# Governance policy (lightweight)

## Purpose

Keep the project maintainable, cost-aware, and safe enough for a single-maintainer serverless ML workload—without enterprise ceremony.

## Roles

- **Author / maintainer**: Fabio "Drago" Monreal — `fabio.monreal@outlook.com` — [LinkedIn](https://www.linkedin.com/in/fabiomonreal/)
- **GitHub**: [DragoHG/fooocus-modal](https://github.com/DragoHG/fooocus-modal)
- **Maintainer git identity** (direct commits): `DragoHG <fabio.monreal@outlook.com>`
- **License**: MIT (see `LICENSE`).
- **Canonical remote**: `https://github.com/DragoHG/fooocus-modal.git`

## Change control

1. Prefer plan → structure → implementation.
2. Archive plans under `.cursor/planx/`.
3. Record alterations in `docs/audit/CHANGELOG.md`.
4. Commits only with the maintainer identity above.
5. No remote push unless the maintainer requests it.

## Contribution hygiene

Release artifacts and history should look like ordinary maintainer work. Omit IDE/assistant/tooling attribution from source, docs, and commit messages. Treat leftover generator banners or “written by …” footnotes as defects to remove before commit.

## Data and FinOps

- Default `ZERO_TELEMETRY=true`: no retention of generation inputs/outputs on the Modal Volume.
- Models on Volume are intentional durable state; media is not, unless telemetry is disabled flag is turned off.
- Scale-to-zero is mandatory for GPU workers (`min_containers=0`).

## Security baseline

- Secrets out of git.
- Manifest downloads constrained to known model subfolders.
- Avoid logging user media/prompts under zero-telemetry mode.
- Document security-relevant changes in the audit log.

## References

Inspired by pragmatic subsets of secure SDLC practice (threat-aware defaults, least privilege, change traceability)—applied at small-project scale.
