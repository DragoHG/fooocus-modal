# Security policy

## Supported versions

This project is under active early development. Security fixes target the default branch.

## Reporting a vulnerability

Please open a **private** security advisory on GitHub when available, or email the maintainer at `fabio.monreal@outlook.com` with:

- A short description of the issue
- Steps to reproduce (if applicable)
- Impact assessment

Do not open a public issue for unfixed vulnerabilities that could expose credentials, Modal tokens, or Volume contents.

## Operational notes

- Never commit `.env`, Modal tokens, or a private `models.txt` with non-public URLs if that matters to you.
- Prefer `ZERO_TELEMETRY=true` unless you intentionally retain generation media on the Volume.
