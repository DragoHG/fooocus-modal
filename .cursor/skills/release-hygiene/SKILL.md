---
name: release-hygiene
description: Verify commit authorship, push policy, secrets hygiene, and clean contribution provenance before git commits. Use when committing, reviewing staged files, or preparing a release.
---

# Release hygiene

## Pre-commit checklist

- [ ] Author will be `DragoHG <fabio.monreal@outlook.com>`
- [ ] No `.env`, `models.txt`, keys, or Volume dumps staged
- [ ] No assistant/IDE attribution in staged text
- [ ] Audit entry exists for the slice being committed
- [ ] Push only if the user explicitly asked

## Commit command pattern

```bash
git commit --author="DragoHG <fabio.monreal@outlook.com>" -m "$(cat <<'EOF'
<message>

EOF
)"
```

## Push

Default: stop after commit. Push only on explicit maintainer request.
