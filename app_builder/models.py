"""models.py — estructuras de datos del orquestador multiagente."""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any


class AgentRole(str, Enum):
    ARCHITECT = "architect"
    BACKEND = "backend"
    FRONTEND = "frontend"
    QA = "qa"
    DEVOPS = "devops"


@dataclass
class LogEntry:
    agent: str
    step: str
    status: str  # "started" | "done" | "error"
    message: str = ""
    timestamp: float = field(default_factory=lambda: __import__("time").time())


@dataclass
class Artifact:
    """Un archivo generado por un agente."""

    path: Path  # relativo al proyecto generado
    content: str
    agent: str
    description: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "path": str(self.path),
            "agent": self.agent,
            "description": self.description,
            "size": len(self.content),
        }


@dataclass
class BuildRequest:
    """Entrada del usuario para el orquestador."""

    description: str
    project_name: str | None = None
    stack: str = "auto"  # auto | fastapi-react | flask-vanilla


@dataclass
class BuildResult:
    """Salida completa del orquestador."""

    project_slug: str
    project_dir: Path
    spec: dict[str, Any]
    artifacts: list[Artifact]
    logs: list[LogEntry]
    summary: str = ""

    def report(self) -> dict[str, Any]:
        return {
            "project_slug": self.project_slug,
            "project_dir": str(self.project_dir),
            "spec": self.spec,
            "artifacts": [a.to_dict() for a in self.artifacts],
            "logs": [
                {"agent": l.agent, "step": l.step, "status": l.status, "message": l.message}
                for l in self.logs
            ],
            "summary": self.summary,
        }
