# Contributing

**fooocus-modal** is MIT-licensed. Issues and pull requests that improve reliability, FinOps defaults, or documentation are welcome.

**Author:** Fabio "Drago" Monreal · [Email](mailto:fabio.monreal@outlook.com) · [LinkedIn](https://www.linkedin.com/in/fabiomonreal/) · [Website](https://fabio-monreal.vercel.app/en)

## How we work

1. Clarify the change (plan when the scope is non-trivial)
2. Prefer structure and docs before large runtime shifts
3. Implement
4. Record the change in `docs/audit/CHANGELOG.md`
5. Commit; open a PR when contributing from a fork
6. Maintainers push to the canonical remote only when intentional

## Pull requests

- Branch from `main` with a clear problem and solution summary
- Keep secrets out of the tree (`.env`, private `models.txt`, Modal tokens)
- Prefer focused diffs; update the audit changelog for meaningful changes
- External contributors: use your own GitHub author identity on fork/PR commits

## Maintainer commit identity

Direct commits to the canonical repository use:

```text
DragoHG <fabio.monreal@outlook.com>
```

```bash
git commit --author="DragoHG <fabio.monreal@outlook.com>" -m "message"
```

## Maintainer push policy

Do not push to the canonical remote unless the maintainer explicitly requests it for that change set.

## Hygiene

- Keep `.env` and `models.txt` gitignored
- Prefer commit messages that explain why
- Remove accidental tooling banners or generator footnotes before commit
- Follow [SECURITY.md](SECURITY.md) for vulnerability reports
