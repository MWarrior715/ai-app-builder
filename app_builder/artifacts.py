"""artifacts.py — guardado de artefactos en disco."""
from __future__ import annotations

from pathlib import Path

from .models import Artifact


def slugify(name: str) -> str:
    """Convierte un nombre en un slug seguro para carpetas."""
    import re

    s = name.lower().strip()
    s = re.sub(r"[^a-z0-9]+", "-", s)
    s = re.sub(r"^-+|-+$", "", s)
    return s or "project"


def save_artifacts(base_dir: Path, artifacts: list[Artifact]) -> None:
    """Escribe cada artefacto en el directorio base respetando su path relativo."""
    base_dir.mkdir(parents=True, exist_ok=True)
    for artifact in artifacts:
        target = base_dir / artifact.path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(artifact.content, encoding="utf-8")
