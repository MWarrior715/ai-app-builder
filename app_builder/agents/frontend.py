"""frontend.py — Agente Frontend.

Genera un frontend simple según la especificación.
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
    frontend = spec.get("stack", {}).get("frontend", "vanilla")
    endpoints = json.dumps(spec.get("endpoints", []), ensure_ascii=False, indent=2)
    return dedent(
        f"""\
        Eres el Agente Frontend. Genera un frontend mínimo para:

        Proyecto: {spec.get('project_name', 'app')}
        Stack frontend: {frontend}
        Endpoints del backend:
        {endpoints}

        Escribe los archivos necesarios (index.html, app.js, styles.css o
        componentes React básicos) para consumir la API.

        Responde ÚNICAMENTE con el contenido de los archivos en este formato:

        ---FILE: index.html---
        <contenido>

        ---FILE: app.js---
        <contenido>

        ---FILE: styles.css---
        <contenido>

        No agregues explicaciones fuera de los bloques FILE.
        """
    ).strip()


def _parse_files(raw: str) -> list[tuple[str, str]]:
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


def run_frontend(spec: dict[str, Any], llm: LLMProvider) -> tuple[list[Artifact], list[LogEntry]]:
    logs: list[LogEntry] = [LogEntry(agent=AgentRole.FRONTEND, step="code", status="started")]
    prompt = _prompt(spec)
    raw = llm.complete(prompt, system=SYSTEM_PROMPT)
    files = _parse_files(raw)

    if not files:
        files = [
            (
                "index.html",
                dedent(
                    f"""\
                    <!DOCTYPE html>
                    <html lang="en">
                    <head>
                      <meta charset="UTF-8">
                      <title>{spec.get('project_name', 'App')}</title>
                      <link rel="stylesheet" href="styles.css">
                    </head>
                    <body>
                      <h1>{spec.get('project_name', 'App')}</h1>
                      <div id="app"></div>
                      <script src="app.js"></script>
                    </body>
                    </html>
                    """
                ).strip(),
            ),
            (
                "app.js",
                dedent(
                    """\
                    const API = "http://localhost:8000";
                    async function loadItems() {
                      const res = await fetch(`${API}/items`);
                      const items = await res.json();
                      document.getElementById("app").innerHTML = "<pre>" + JSON.stringify(items, null, 2) + "</pre>";
                    }
                    loadItems();
                    """
                ).strip(),
            ),
            ("styles.css", "body { font-family: system-ui; margin: 2rem; }"),
        ]

    artifacts = [
        Artifact(path=Path("frontend") / path, content=content, agent=AgentRole.FRONTEND, description=f"Frontend file {path}")
        for path, content in files
    ]
    logs.append(LogEntry(agent=AgentRole.FRONTEND, step="code", status="done", message=f"{len(artifacts)} files"))
    return artifacts, logs
