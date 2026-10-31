# Security policy

## Supported versions

Security fixes target the default branch while the project is in early development.

## Reporting a vulnerability

Prefer a private GitHub security advisory when available. Otherwise contact **Fabio "Drago" Monreal** at [fabio.monreal@outlook.com](mailto:fabio.monreal@outlook.com) with:

- Short description
- Reproduction steps (if applicable)
- Likely impact

Do not open a public issue for unfixed issues that could expose credentials, Modal tokens, or Volume contents.

## Operational guidance

- Never commit `.env`, Modal tokens, or sensitive model URLs in `models.txt`
- Prefer `ZERO_TELEMETRY=true` unless you intentionally retain generation media on the Volume
