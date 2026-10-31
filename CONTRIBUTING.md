# Contributing

Thanks for your interest in **fooocus-modal**.

**Author:** Fabio "Drago" Monreal · [Email](mailto:fabio.monreal@outlook.com) · [LinkedIn](https://www.linkedin.com/in/fabiomonreal/) · [Website](https://fabio-monreal.vercel.app/en)

## Before you change code

1. Read the [user guide](docs/USER_GUIDE.md) and [architecture overview](docs/architecture/OVERVIEW.md).
2. Prefer small, reviewable diffs that match existing style.
3. Keep FinOps defaults: scale to zero, short idle, no warm GPU pool, models on Volume only.
4. Do not commit secrets (`.env`, private `models.txt`, Modal tokens).

## Local checks

```bash
source .venv/bin/activate
python -m unittest discover -s tests -v
scripts/check_git_authorship.sh   # before push
```

Useful layout:

| Path | Role |
|------|------|
| `local/` | Gradio UI + presets/session cache |
| `modal_app/` | Modal Image, Volume, `FooocusWorker` |
| `src/` | Shared params, paths, Fooocus task builder |
| `docs/` | User, architecture, governance, audit |
| `.cursor/rules/` | Agent/project rules (optional for humans) |

## Pull requests

1. Fork and branch from `main`
2. Explain the problem and the outcome in the PR body
3. Update `docs/audit/CHANGELOG.md` when the change is meaningful
4. Update `docs/USER_GUIDE.md` when user-facing behavior changes
5. Keep commit authorship as normal human maintainer work (see [contribution hygiene](docs/governance/CONTRIBUTION_HYGIENE.md))

## Ideas that fit well

- Clearer product docs and onboarding
- Reliability and cost defaults (scale-to-zero, short idle, lean cold start)
- UI controls that match Fooocus without complicating the happy path
- Safer model sync and Volume layout fixes

## Security

Report vulnerabilities through [SECURITY.md](SECURITY.md).
