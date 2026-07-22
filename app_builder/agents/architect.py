"""architect.py — Agente Arquitecto.

Convierte una descripción en lenguaje natural en una especificación técnica
estructurada (stack, entidades, endpoints, requisitos).
"""
from __future__ import annotations

import json
from pathlib import Path
from textwrap import dedent
from typing import Any

from ..models import AgentRole, Artifact, BuildRequest, LogEntry
from ..providers import LLMProvider
from .base import SYSTEM_PROMPT, strip_code_fence


def _prompt(request: BuildRequest) -> str:
    return dedent(
        f"""\
        Eres el Arquitecto de un orquestador multiagente. Tu trabajo es
        convertir la descripción del usuario en una especificación técnica
        clara y estructurada en JSON.

        Descripción del usuario:
        {request.description}

        Stack preferido: {request.stack}

        Genera ÚNICAMENTE un objeto JSON con esta estructura exacta:
        {{
          "project_name": "nombre corto en inglés",
          "description": "paráfrasis breve del propósito",
          "stack": {{
            "backend": "fastapi | flask | express | node",
            "frontend": "react | nextjs | vanilla",
            "database": "sqlite | postgres | none"
          }},
          "entities": ["tarea", "usuario"],
          "endpoints": [
            {{"method": "GET", "path": "/items", "purpose": "listar"}}
          ],
          "features": ["auth jwt", "CRUD"],
          "constraints": ["sqlite por simplicidad"]
        }}

        Si el stack es "auto", elige el más apropiado para la descripción.
        Devuelve SOLO el JSON, sin markdown ni explicaciones.
        """
    ).strip()


def run_architect(request: BuildRequest, llm: LLMProvider) -> tuple[dict[str, Any], list[Artifact], list[LogEntry]]:
    logs: list[LogEntry] = [LogEntry(agent=AgentRole.ARCHITECT, step="spec", status="started")]
    prompt = _prompt(request)
    raw = llm.complete(prompt, system=SYSTEM_PROMPT)
    raw = strip_code_fence(raw)

    try:
        spec = json.loads(raw)
    except json.JSONDecodeError as exc:
        logs.append(
            LogEntry(
                agent=AgentRole.ARCHITECT,
                step="spec",
                status="error",
                message=f"JSON inválido: {exc}",
            )
        )
        # Fallback mínimo para no romper el pipeline.
        spec = {
            "project_name": request.project_name or "app",
            "description": request.description,
            "stack": {"backend": "fastapi", "frontend": "vanilla", "database": "sqlite"},
            "entities": ["item"],
            "endpoints": [{"method": "GET", "path": "/items", "purpose": "listar"}],
            "features": ["CRUD básico"],
            "constraints": [],
        }

    artifact = Artifact(
        path=Path("spec.json"),
        content=json.dumps(spec, ensure_ascii=False, indent=2),
        agent=AgentRole.ARCHITECT,
        description="Especificación técnica generada por el Arquitecto",
    )
    logs.append(LogEntry(agent=AgentRole.ARCHITECT, step="spec", status="done", message=f"spec={spec.get('project_name')} backend={spec.get('stack',{}).get('backend')} frontend={spec.get('stack',{}).get('frontend')}"))
    return spec, [artifact], logs
