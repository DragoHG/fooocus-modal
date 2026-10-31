---
name: audit-trail
description: Append structured entries to docs/audit/CHANGELOG.md for an auditable history of project changes. Use when finishing a development slice, editing architecture/governance, archiving plans, or when the user asks to document alterations.
---

# Audit trail

## When

After meaningful changes land in the working tree (even before commit).

## Steps

1. Open `docs/audit/CHANGELOG.md`.
2. Under `## [Unreleased]` (create if missing), prepend:

```markdown
### YYYY-MM-DD - <short title>

- **What:** ...
- **Why:** ...
- **Paths:** `path/a`, `path/b`
```

3. Keep tone neutral and maintainer-authored.
4. Do not mention assistants, IDEs, or generation tools.
5. If the change came from a plan, link the archived file: `.cursor/planx/<file>.md`.

## Batching

One entry per logical slice is enough; group tiny related file tweaks.
