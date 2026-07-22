"""orchestrator.py — motor del AI App Builder.

Coordina agentes especializados para transformar una descripción en un
proyecto de software en disco, con logs trazables.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .agents import run_architect, run_backend, run_devops, run_frontend, run_qa
from .artifacts import save_artifacts, slugify
from .config import settings
from .models import Artifact, BuildRequest, BuildResult, LogEntry
from .providers import LLMProvider, default_llm


class AppBuilder:
    """Fachada del orquestador."""

    def __init__(self, llm: LLMProvider | None = None) -> None:
        self.llm = llm or default_llm()

    def build(self, request: BuildRequest) -> BuildResult:
        logs: list[LogEntry] = []
        artifacts: list[Artifact] = []

        # 1. Arquitecto
        spec, arch_artifacts, arch_logs = run_architect(request, self.llm)
        artifacts.extend(arch_artifacts)
        logs.extend(arch_logs)

        # Normaliza nombre de proyecto.
        project_name = request.project_name or spec.get("project_name", "app")
        project_slug = slugify(project_name)
        project_dir = settings.output_dir / project_slug

        # 2. Backend
        backend_artifacts, backend_logs = run_backend(spec, self.llm)
        artifacts.extend(backend_artifacts)
        logs.extend(backend_logs)

        # 3. Frontend
        frontend_artifacts, frontend_logs = run_frontend(spec, self.llm)
        artifacts.extend(frontend_artifacts)
        logs.extend(frontend_logs)

        # 4. QA
        qa_artifacts, qa_logs = run_qa(spec, artifacts, self.llm)
        artifacts.extend(qa_artifacts)
        logs.extend(qa_logs)

        # 5. DevOps
        devops_artifacts, devops_logs = run_devops(spec, self.llm)
        artifacts.extend(devops_artifacts)
        logs.extend(devops_logs)

        # Persistir
        save_artifacts(project_dir, artifacts)
        report_path = project_dir / "report.json"
        result = BuildResult(
            project_slug=project_slug,
            project_dir=project_dir,
            spec=spec,
            artifacts=artifacts,
            logs=logs,
            summary=f"Generado proyecto {project_slug} con {len(artifacts)} archivos.",
        )
        report_path.write_text(json.dumps(result.report(), ensure_ascii=False, indent=2), encoding="utf-8")

        return result
