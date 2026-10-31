---
name: Runtime implementation
overview: Implement Modal FooocusWorker, models sync, and local Gradio UI with ZERO_TELEMETRY and L4→A10 FinOps defaults.
updated: 2026-10-30T22:25:00-03:00
status: done
---

# Runtime implementation

## Delivered

- `src/paths.py`, `manifest.py`, `generate_params.py`, `fooocus_task.py`
- `modal_app/app.py` - `sync_models`, `FooocusWorker.generate/list_assets`
- `modal_app/bootstrap.py` - Fooocus init without Gradio
- `local/ui.py` - Gradio client
- `tests/test_manifest.py`

## Ops

1. `modal run modal_app/app.py --action sync`
2. `modal deploy modal_app/app.py`
3. `python local/ui.py`
