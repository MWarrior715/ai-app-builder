"""qa.py — Agente QA.

Revisa la especificación y los artefactos generados, produce tests y un
reporte de inconsistencias.
"""
from __future__ import annotations

import json
from pathlib import Path
from textwrap import dedent
from typing import Any

from ..models import AgentRole, Artifact, LogEntry
from ..providers import LLMProvider
from .base import SYSTEM_PROMPT, strip_code_fence


def _prompt(spec: dict[str, Any], artifact_paths: list[str]) -> str:
    return dedent(
        f"""\
        Eres el Agente QA. Revisa la especificación y los archivos generados.

        Proyecto: {spec.get('project_name', 'app')}
        Endpoints esperados:
        {json.dumps(spec.get('endpoints', []), ensure_ascii=False, indent=2)}
        Features esperadas:
        {', '.join(spec.get('features', []))}

        Archivos generados:
        {chr(10).join(artifact_paths)}

        Tu salida debe ser SOLO un objeto JSON con esta estructura:
        {{
          "tests": "contenido de un archivo de tests pytest",
          "review": "breve análisis de cobertura e inconsistencias",
          "score": 85
        }}

        No agregues markdown ni explicaciones fuera del JSON.
        """
    ).strip()


def run_qa(spec: dict[str, Any], artifacts: list[Artifact], llm: LLMProvider) -> tuple[list[Artifact], list[LogEntry]]:
    logs: list[LogEntry] = [LogEntry(agent=AgentRole.QA, step="review", status="started")]
    artifact_paths = [str(a.path) for a in artifacts]
    prompt = _prompt(spec, artifact_paths)
    raw = llm.complete(prompt, system=SYSTEM_PROMPT)
    raw = strip_code_fence(raw)

    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        data = {
            "tests": "def test_placeholder():\n    assert True",
            "review": "No se pudo parsear la revisión del LLM. Se generó placeholder.",
            "score": 50,
        }

    qa_artifacts: list[Artifact] = []
    if isinstance(data.get("tests"), str):
        qa_artifacts.append(
            Artifact(
                path=Path("tests") / "test_generated.py",
                content=data["tests"],
                agent=AgentRole.QA,
                description="Tests generados por QA",
            )
        )
    review = data.get("review", "")
    score = data.get("score", 0)
    logs.append(LogEntry(agent=AgentRole.QA, step="review", status="done", message=f"score={score} {review[:120]}"))
    return qa_artifacts, logs
