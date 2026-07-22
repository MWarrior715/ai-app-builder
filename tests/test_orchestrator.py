"""test_orchestrator.py — smoke tests end-to-end con LLM falso.

No toca Ollama ni ningún motor cloud: usa un LLMProvider falso y determinista.
Verifica que el orquestador coordina agentes y genera archivos.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from app_builder.models import BuildRequest
from app_builder.orchestrator import AppBuilder
from app_builder.providers import LLMProvider


class FakeLLM(LLMProvider):
    """LLM falso que devuelve respuestas mínimas para cada agente."""

    def complete(self, prompt: str, *, system: str | None = None) -> str:  # noqa: ARG002
        prompt_lower = prompt.lower()
        if "arquitecto" in prompt_lower or "json" in prompt_lower and "stack" in prompt_lower:
            return json.dumps(
                {
                    "project_name": "taskmanager",
                    "description": "API de tareas",
                    "stack": {"backend": "fastapi", "frontend": "vanilla", "database": "sqlite"},
                    "entities": ["task", "user"],
                    "endpoints": [
                        {"method": "GET", "path": "/tasks", "purpose": "listar"},
                        {"method": "POST", "path": "/tasks", "purpose": "crear"},
                    ],
                    "features": ["CRUD"],
                    "constraints": [],
                }
            )
        if "backend" in prompt_lower:
            return "---FILE: main.py---\nfrom fastapi import FastAPI\napp = FastAPI()\n"
        if "frontend" in prompt_lower:
            return "---FILE: index.html---\n<html><body>App</body></html>\n"
        if "qa" in prompt_lower or "tests" in prompt_lower:
            return json.dumps(
                {
                    "tests": "def test_placeholder():\n    assert True\n",
                    "review": "Cobertura mínima. OK para smoke test.",
                    "score": 80,
                }
            )
        if "devops" in prompt_lower or "docker" in prompt_lower:
            return "---FILE: docker-compose.yml---\nservices:\n  app:\n    image: python:3.11\n"
        return "mock"


@pytest.fixture()
def builder(tmp_path):
    from app_builder import config

    config.settings.output_dir = tmp_path / "outputs"
    return AppBuilder(llm=FakeLLM())


def test_build_runs_all_agents(builder: AppBuilder):
    request = BuildRequest(description="Crea una API de tareas", project_name="TaskManager")
    result = builder.build(request)

    assert result.project_slug == "taskmanager"
    assert result.project_dir.exists()

    agents = {log.agent for log in result.logs if log.status == "done"}
    assert "architect" in agents
    assert "backend" in agents
    assert "frontend" in agents
    assert "qa" in agents
    assert "devops" in agents

    assert result.artifacts
    paths = [str(a.path) for a in result.artifacts]
    assert any("spec.json" in p for p in paths)
    assert any("main.py" in p for p in paths)

    report_path = result.project_dir / "report.json"
    assert report_path.exists()
    data = json.loads(report_path.read_text(encoding="utf-8"))
    assert data["project_slug"] == "taskmanager"
