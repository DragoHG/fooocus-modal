# Contributing

Thanks for interest in **fooocus-on-modal**. This project is MIT-licensed and welcomes issues and pull requests.

## Development sequence

1. Plan (saved under `.cursor/planx/` when using the project agent workflow)
2. Structure/docs if needed
3. Implementation
4. Audit entry in `docs/audit/CHANGELOG.md`
5. Commit
6. Push / open a PR (maintainers push to default branch only when intentional)

## Pull requests

- Fork, branch from `main`, open a PR with a clear problem/solution summary.
- Keep secrets out of the tree (`.env`, private `models.txt`, Modal tokens).
- Prefer focused diffs and update the audit changelog for meaningful changes.
- External contributors: use your own GitHub author identity on commits in your fork/PR.

## Maintainer commit identity

Direct commits to the canonical repository by the maintainer (and automation acting for the maintainer) use:

```text
DragoHG <fabio.monreal@outlook.com>
```

Example:

```bash
git commit --author="DragoHG <fabio.monreal@outlook.com>" -m "message"
```

## Push policy (maintainers)

Do not push to the canonical remote unless the maintainer explicitly requests it for that change set.

## Hygiene

- Keep `.env` and `models.txt` gitignored.
- Prefer commit messages that explain why.
- Strip accidental tooling banners or generator footnotes from files before commit.
- Follow [SECURITY.md](SECURITY.md) for vulnerability reports.
