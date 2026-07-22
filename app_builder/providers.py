"""providers.py — capa de proveedores de IA enchufables.

Interfaz LLMProvider implementada por OpenAICompatibleLLM. El repo NO depende
de un proveedor concreto: basta apuntar OPENAI_BASE_URL al motor que se use en
runtime. Ese motor no se nombra en el código; la configuración vive en .env.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol, runtime_checkable

from openai import OpenAI

from .config import settings


@runtime_checkable
class LLMProvider(Protocol):
    """Genera texto a partir de un prompt."""

    def complete(self, prompt: str, *, system: str | None = None) -> str: ...


@dataclass
class OpenAICompatibleLLM:
    """LLM vía API OpenAI-compatible."""

    model: str = settings.llm_model
    client: OpenAI = None  # type: ignore[assignment]
    temperature: float = 0.2
    max_tokens: int = 2048

    def __post_init__(self) -> None:
        if self.client is None:
            self.client = OpenAI(
                base_url=settings.openai_base_url,
                api_key=settings.openai_api_key,
            )

    def complete(self, prompt: str, *, system: str | None = None) -> str:
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})
        resp = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=self.temperature,
            max_tokens=self.max_tokens,
        )
        content = resp.choices[0].message.content
        return (content or "").strip()


def default_llm() -> LLMProvider:
    return OpenAICompatibleLLM()
