"""Parse models.txt and download assets into Volume folders."""

from __future__ import annotations

import os
import subprocess
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlparse

from .paths import MODEL_SUBDIRS, ensure_layout, model_dir

ALLOWED_KINDS = set(MODEL_SUBDIRS)


@dataclass(frozen=True)
class ManifestEntry:
    kind: str
    relative_name: str
    url: str

    @property
    def target(self) -> Path:
        base = model_dir(self.kind)
        target = (base / self.relative_name).resolve()
        if not str(target).startswith(str(base.resolve())):
            raise ValueError(f"Path escapes model dir: {self.relative_name}")
        return target


def parse_manifest(text: str) -> list[ManifestEntry]:
    entries: list[ManifestEntry] = []
    for lineno, raw in enumerate(text.splitlines(), start=1):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split("\t") if "\t" in line else [p for p in line.split() if p]
        if len(parts) < 3:
            raise ValueError(f"models.txt line {lineno}: expected kind, filename, url")
        kind, name, url = parts[0].lower(), parts[1], parts[2]
        if kind not in ALLOWED_KINDS:
            raise ValueError(f"models.txt line {lineno}: unknown kind {kind!r}")
        if ".." in Path(name).parts:
            raise ValueError(f"models.txt line {lineno}: invalid relative path")
        parsed = urlparse(url)
        if parsed.scheme not in {"http", "https"}:
            raise ValueError(f"models.txt line {lineno}: only http(s) URLs allowed")
        entries.append(ManifestEntry(kind=kind, relative_name=name, url=url))
    return entries


def parse_manifest_file(path: Path) -> list[ManifestEntry]:
    return parse_manifest(path.read_text(encoding="utf-8"))


def _download(url: str, dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    tmp = dest.with_suffix(dest.suffix + ".partial")
    if tmp.exists():
        tmp.unlink()
    cmd = [
        "aria2c",
        "-x",
        "8",
        "-s",
        "8",
        "-k",
        "1M",
        "--file-allocation=none",
        "--allow-overwrite=true",
        "-d",
        str(tmp.parent),
        "-o",
        tmp.name,
        url,
    ]
    try:
        subprocess.run(cmd, check=True)
    except (FileNotFoundError, subprocess.CalledProcessError):
        subprocess.run(["curl", "-L", "--fail", "-o", str(tmp), url], check=True)
    tmp.replace(dest)
    os.chmod(dest, 0o644)


def sync_entries(entries: list[ManifestEntry]) -> list[dict]:
    ensure_layout()
    report: list[dict] = []
    for entry in entries:
        target = entry.target
        if target.exists() and target.stat().st_size > 0:
            report.append(
                {
                    "kind": entry.kind,
                    "path": str(target),
                    "status": "skipped",
                    "bytes": target.stat().st_size,
                }
            )
            continue
        _download(entry.url, target)
        report.append(
            {
                "kind": entry.kind,
                "path": str(target),
                "status": "downloaded",
                "bytes": target.stat().st_size,
            }
        )
    return report
