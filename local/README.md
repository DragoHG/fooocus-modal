# local

CPU Gradio UI that calls the deployed Modal `FooocusWorker`.

```bash
cp ../.env.example ../.env
# modal deploy ../modal_app/app.py
python ui.py
```

Open `http://127.0.0.1:7860` (defaults from `.env`).
