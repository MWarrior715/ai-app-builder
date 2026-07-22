"""backend.py — Agente Backend.

Genera el código del backend según la especificación.
"""
from __future__ import annotations

import json
from pathlib import Path
from textwrap import dedent
from typing import Any

from ..models import AgentRole, Artifact, LogEntry
from ..providers import LLMProvider
from .base import SYSTEM_PROMPT, strip_code_fence


def _prompt(spec: dict[str, Any]) -> str:
    backend = spec.get("stack", {}).get("backend", "fastapi")
    db = spec.get("stack", {}).get("database", "sqlite")
    endpoints = json.dumps(spec.get("endpoints", []), ensure_ascii=False, indent=2)
    entities = ", ".join(spec.get("entities", ["item"]))
    features = ", ".join(spec.get("features", []))
    return dedent(
        f"""\
        Eres el Agente Backend. Genera el código completo de la API para:

        Proyecto: {spec.get('project_name', 'app')}
        Descripción: {spec.get('description', '')}
        Stack backend: {backend}
        Base de datos: {db}
        Entidades: {entities}
        Features: {features}
        Endpoints esperados:
        {endpoints}

        Escribe los archivos necesarios (main.py/app.py, models.py, routers/)
        para tener un backend funcional con CRUD completo.

        Responde ÚNICAMENTE con el contenido de los archivos en este formato:

        ---FILE: main.py---
        <contenido>

        ---FILE: models.py---
        <contenido>

        ---FILE: requirements.txt---
        <contenido>

        No agregues explicaciones fuera de los bloques FILE.
        """
    ).strip()


def _parse_files(raw: str) -> list[tuple[str, str]]:
    """Parsea bloques ---FILE: path---."""
    import re

    files: list[tuple[str, str]] = []
    pattern = re.compile(r"---FILE:\s*(.+?)---\n", re.MULTILINE)
    matches = list(pattern.finditer(raw))
    for i, m in enumerate(matches):
        path = m.group(1).strip()
        start = m.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(raw)
        content = strip_code_fence(raw[start:end])
        files.append((path, content))
    return files


def run_backend(spec: dict[str, Any], llm: LLMProvider) -> tuple[list[Artifact], list[LogEntry]]:
    logs: list[LogEntry] = [LogEntry(agent=AgentRole.BACKEND, step="code", status="started")]
    prompt = _prompt(spec)
    raw = llm.complete(prompt, system=SYSTEM_PROMPT)
    files = _parse_files(raw)

    if not files:
        # Fallback: al menos main.py con un CRUD genérico.
        files = [
            (
                "main.py",
                dedent(
                    f"""\
                    from fastapi import FastAPI
                    from pydantic import BaseModel

                    app = FastAPI(title="{spec.get('project_name', 'App')}")

                    class Item(BaseModel):
                        id: int | None = None
                        name: str

                    items = []

                    @app.get("/items")
                    def list_items():
                        return items

                    @app.post("/items")
                    def create_item(item: Item):
                        item.id = len(items) + 1
                        items.append(item)
                        return item

                    @app.get("/items/{{item_id}}")
                    def get_item(item_id: int):
                        return next((i for i in items if i.id == item_id), None)

                    @app.delete("/items/{{item_id}}")
                    def delete_item(item_id: int):
                        global items
                        items = [i for i in items if i.id != item_id]
                        return {{"deleted": item_id}}
                    """
                ).strip(),
            ),
            ("requirements.txt", "fastapi\nuvicorn\npydantic"),
        ]

    artifacts = [
        Artifact(path=Path("backend") / path, content=content, agent=AgentRole.BACKEND, description=f"Backend file {path}")
        for path, content in files
    ]
    logs.append(LogEntry(agent=AgentRole.BACKEND, step="code", status="done", message=f"{len(artifacts)} files"))
    return artifacts, logs
