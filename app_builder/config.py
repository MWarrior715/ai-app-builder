"""config.py — carga de configuración por entorno.

Toda la configuración vive en variables de entorno (ver .env.example). Esto
mantiene el motor de IA enchufable: el mismo código corre local o en cloud.
"""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

from dotenv import load_dotenv

# Carga .env si existe (no falla si no está — las vars de entorno reales valen).
load_dotenv()

REPO_ROOT = Path(__file__).resolve().parent.parent


def _env(key: str, default: str) -> str:
    return os.getenv(key, default)


@dataclass
class Settings:
    # Motor de IA (OpenAI-compatible, local o cloud).
    openai_base_url: str = field(default_factory=lambda: _env("OPENAI_BASE_URL", "http://localhost:11434/v1"))
    openai_api_key: str = field(default_factory=lambda: _env("OPENAI_API_KEY", "local-dev-key"))
    llm_model: str = field(default_factory=lambda: _env("LLM_MODEL", "qwen2.5:7b-instruct"))

    # Salida.
    output_dir: Path = field(default_factory=lambda: Path(_env("OUTPUT_DIR", "./outputs")))

    def __post_init__(self) -> None:
        # Resolver rutas relativas contra la raíz del repo.
        if not self.output_dir.is_absolute():
            self.output_dir = (REPO_ROOT / self.output_dir).resolve()
        # Asegura que el directorio de salida exista.
        self.output_dir.mkdir(parents=True, exist_ok=True)


settings = Settings()
