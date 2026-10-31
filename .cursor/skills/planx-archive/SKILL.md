---
name: planx-archive
description: Archive implementation plans into .cursor/planx with dated filenames. Use when creating, revising, or confirming a plan, or when the user asks to save/update project plans.
---

# Planx archive

## Target

`.cursor/planx/`

## Filename

`YYYYMMDD-HHMM-<slug>.md`

Examples:

- `20261030-2158-fooocus-modal-worker.md`
- `20261030-2205-zero-telemetry-rename.md`

## File template

```markdown
---
name: <Plan name>
overview: <one line>
updated: <ISO-8601>
status: draft|active|done
---

# <Plan name>

<full plan body>
```

## Rules

- Always copy/save into planx; do not rely on external plan UIs alone.
- Prefer a **new dated file** on material revisions (audit-friendly).
- After archiving, add a short audit changelog item pointing at the new file.
- Strip assistant/tooling marketing language from the archived body if present.
