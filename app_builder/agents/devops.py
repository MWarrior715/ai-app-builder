"""devops.py — Agente DevOps.

Genera Dockerfile, docker-compose.yml y README interno del proyecto.
"""
from __future__ import annotations

from pathlib import Path
from textwrap import dedent
from typing import Any

from ..models import AgentRole, Artifact, LogEntry
from ..providers import LLMProvider
from .base import SYSTEM_PROMPT, strip_code_fence


def _prompt(spec: dict[str, Any]) -> str:
    backend = spec.get("stack", {}).get("backend", "fastapi")
    frontend = spec.get("stack", {}).get("frontend", "vanilla")
    return dedent(
        f"""\
        Eres el Agente DevOps. Genera la configuración de despliegue local para:

        Proyecto: {spec.get('project_name', 'app')}
        Backend: {backend}
        Frontend: {frontend}

        Responde ÚNICAMENTE con el contenido de los archivos en este formato:

        ---FILE: Dockerfile---
        <contenido>

        ---FILE: docker-compose.yml---
        <contenido>

        ---FILE: README_PROJECT.md---
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


def run_devops(spec: dict[str, Any], llm: LLMProvider) -> tuple[list[Artifact], list[LogEntry]]:
    logs: list[LogEntry] = [LogEntry(agent=AgentRole.DEVOPS, step="deploy", status="started")]
    prompt = _prompt(spec)
    raw = llm.complete(prompt, system=SYSTEM_PROMPT)
    files = _parse_files(raw)

    if not files:
        files = [
            (
                "Dockerfile",
                dedent(
                    """\
                    FROM python:3.11-slim
                    WORKDIR /app
                    COPY backend/requirements.txt .
                    RUN pip install -r requirements.txt
                    COPY backend .
                    EXPOSE 8000
                    CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
                    """
                ).strip(),
            ),
            (
                "docker-compose.yml",
                dedent(
                    """\
                    services:
                      backend:
                        build: .
                        ports:
                          - "8000:8000"
                      frontend:
                        image: nginx:alpine
                        volumes:
                          - ./frontend:/usr/share/nginx/html:ro
                        ports:
                          - "3000:80"
                    """
                ).strip(),
            ),
            (
                "README_PROJECT.md",
                f"# {spec.get('project_name', 'App')}\n\nProyecto generado automáticamente. Ver backend/ y frontend/.",
            ),
        ]

    artifacts = [
        Artifact(path=Path(path), content=content, agent=AgentRole.DEVOPS, description=f"DevOps file {path}")
        for path, content in files
    ]
    logs.append(LogEntry(agent=AgentRole.DEVOPS, step="deploy", status="done", message=f"{len(artifacts)} files"))
    return artifacts, logs
