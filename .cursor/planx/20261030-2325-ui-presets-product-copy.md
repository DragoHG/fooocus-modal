---
name: UI presets and product copy
overview: End-user executive docs, fuller Gradio controls, JSON preset save/load.
updated: 2026-10-30T23:25:00-03:00
status: done
---

# UI presets and product copy

## Goals

1. Public docs speak to operators/creators, not internal git process.
2. Local UI exposes advanced sampling options plus Input Image tools.
3. Users can download/upload JSON presets to restore settings later.

## Delivered

- `local/presets.py` + UI accordion for export/import
- Advanced accordion (sampler, scheduler, VAE, CLIP skip, ADM, adaptive CFG, NSFW, wildcards, formats)
- CONTRIBUTING / POLICY / README / OVERVIEW rewritten
- Tests for presets; paths env-dynamic for layout tests
