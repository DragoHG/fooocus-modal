# modal_app

Modal application for **fooocus-modal**.

## Commands

```bash
# Populate Volume from models.txt (CPU)
modal run modal_app/app.py --action sync

# Deploy worker
modal deploy modal_app/app.py

# Optional: list models on a warm/cold worker
modal run modal_app/app.py --action list
```

Entrypoint: [`app.py`](app.py) (`FooocusWorker`, `sync_models`).
