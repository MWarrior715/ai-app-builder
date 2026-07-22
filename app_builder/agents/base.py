"""base.py — utilidades comunes para todos los agentes."""
from __future__ import annotations

from textwrap import dedent


SYSTEM_PROMPT = dedent(
    """\
    Eres un agente constructor de software dentro de un orquestador multiagente.
    Recibes especificaciones claras y produces artefactos técnicos concretos:
    código, configuración o documentación.

    Reglas:
    - Responde ÚNICAMENTE con el artefacto solicitado, sin explicaciones externas.
    - El código debe ser funcional, minimalista y listo para copiar a un archivo.
    - No uses frameworks ni dependencias que no estén en la especificación.
    - No incluyas comentarios redundantes tipo "// código generado por IA".
    """
).strip()


def strip_code_fence(text: str) -> str:
    """Elimina fences ```...``` si el LLM los devuelve."""
    t = text.strip()
    if t.startswith("```"):
        lines = t.splitlines()
        if lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        t = "\n".join(lines)
    return t.strip()
