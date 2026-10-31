# src

Shared libraries used by the Modal worker and local UI.

| Module | Role |
|--------|------|
| `paths.py` | Volume layout + `ZERO_TELEMETRY` I/O roots |
| `manifest.py` | Parse/download `models.txt` |
| `generate_params.py` | Request/response dataclasses |
| `fooocus_task.py` | Build Fooocus `AsyncTask` args and run generation |
