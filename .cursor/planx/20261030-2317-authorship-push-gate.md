---
name: Authorship push gate
overview: Versioned git hooks + script that block any push lacking sole DragoHG authorship or carrying tooling provenance.
updated: 2026-10-30T23:17:00-03:00
status: done
---

# Authorship push gate

## Goal

Canonical remote must never show non-maintainer contributors from tooling co-author trailers. Enforce at commit-msg, prepare-commit-msg, and pre-push.

## Deliverables

- `scripts/check_git_authorship.sh` - validates author/committer email and banned message patterns
- `.githooks/{prepare-commit-msg,commit-msg,pre-push}` - strip/reject/block
- Stronger `.cursor/rules/10-git-authorship.mdc` + release-hygiene skill + CONTRIBUTING note
- Enable `core.hooksPath=.githooks` locally; push clean history to recreated GitHub repo
