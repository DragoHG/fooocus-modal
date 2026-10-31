---
name: FinOps CUDA and list_assets fix
overview: Disable unsafe memory snapshots, move list_assets to CPU, fix expansion tokenizer, verify one Lightning generate.
updated: 2026-10-30T23:43:00-03:00
status: done
---

# FinOps CUDA and list_assets fix

## Root causes

1. CPU memory snapshot enter had no GPU; Fooocus init needs CUDA.
2. `list_assets` on the GPU class woke L4/A10 for directory listing.
3. Missing expansion tokenizer sidecars crashed the worker while Modal kept Running.

## Fixes shipped

- Snapshots hard-off in `modal_app/app.py`
- CPU `list_assets` function + UI/smoke callers updated
- Expansion sidecars copied in bootstrap; generation timeouts
- Docs: COLD_START, VERIFICATION, README env table
