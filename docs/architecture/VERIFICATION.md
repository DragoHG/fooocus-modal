# Verification

Last checked: 2026-10-30 (deployed app `fooocus-modal`).

## Local unit tests

```bash
.venv/bin/python -m unittest discover -s tests -v
```

Expected: all tests OK (manifest, params, paths, presets, authorship script).

## Remote smoke (costs GPU time)

Deployed worker was verified with:

1. `list_assets` via CPU function (~4-5s, no GPU)
2. One Lightning txt2img on A10 (~70s round-trip cold-ish; ~17s worker compute) producing `outputs/smoke/txt2img_0.png`

Full multi-mode smoke (vary / FaceSwap / inpaint / outpaint / enhance):

```bash
.venv/bin/python scripts/smoke_remote.py
```

Run only when you intentionally want to spend GPU credits. Cancel any Modal call that stays Running without log progress.

## Ready to generate from the UI

If `modal deploy modal_app/app.py` is current and models were synced:

```bash
python local/ui.py
```

Open `http://127.0.0.1:7860` and use **Generate**.
