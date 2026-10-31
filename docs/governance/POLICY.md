# Product principles

## Purpose

Run Fooocus on Modal with a local UI, pay for GPU only while work runs, and keep day-to-day operation simple.

## Product owner

**Fabio "Drago" Monreal** · [Email](mailto:fabio.monreal@outlook.com) · [LinkedIn](https://www.linkedin.com/in/fabiomonreal/) · [Website](https://fabio-monreal.vercel.app/en)

Repository: [DragoHG/fooocus-modal](https://github.com/DragoHG/fooocus-modal) (MIT)

## Operating defaults

- GPU workers scale to zero when idle
- Models stay on a Modal Volume; generation media stays ephemeral unless you opt in
- Local UI drives on-demand remote generation (no always-on cloud Gradio)
- Prefer short idle windows and an ordered GPU fallback list

## Change discipline

- Prefer clarify → document → implement for non-trivial work
- Record meaningful changes in `docs/audit/CHANGELOG.md`
- Keep secrets (`.env`, private `models.txt`, tokens) out of git

## Security baseline

- Constrain model downloads to known Volume folders
- Avoid logging prompts or media when retention is off
- Report security issues via [SECURITY.md](../../SECURITY.md)
