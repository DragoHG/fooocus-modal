---
name: release-hygiene
description: Verify commit authorship, push policy, secrets hygiene, and clean contribution provenance before git commits. Use when committing, reviewing staged files, or preparing a release.
---

# Release hygiene

## Pre-commit checklist

- [ ] Author will be `DragoHG <fabio.monreal@outlook.com>`
- [ ] Committer email will be `fabio.monreal@outlook.com`
- [ ] No `.env`, `models.txt`, keys, or Volume dumps staged
- [ ] No assistant/IDE attribution or co-author trailers in staged text or commit message
- [ ] Audit entry exists for the slice being committed
- [ ] Push only if the user explicitly asked

## Commit command pattern

```bash
git commit --author="DragoHG <fabio.monreal@outlook.com>" -m "$(cat <<'EOF'
<message>

EOF
)"
```

After commit (and before any push):

```bash
scripts/check_git_authorship.sh
```

If the check fails, amend only when allowed by maintainer commit rules, or create a corrected new commit - never push a failing range.

## Hooks

Repo hooks live in `.githooks/` (`prepare-commit-msg`, `commit-msg`, `pre-push`). Ensure:

```bash
git config core.hooksPath .githooks
```

Never use `--no-verify` to skip these gates.

## Push

Default: stop after commit. Push only on explicit maintainer request. When pushing, the `pre-push` authorship gate must pass.
