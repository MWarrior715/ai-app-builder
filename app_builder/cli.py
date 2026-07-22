"""cli.py — interfaz de línea de comandos del AI App Builder.

Uso:
    python -m app_builder "Crea una API de tareas con autenticación JWT"
"""
from __future__ import annotations

import argparse
import json
import sys

from .models import BuildRequest
from .orchestrator import AppBuilder


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="app_builder",
        description="AI App Builder — genera aplicaciones desde lenguaje natural",
    )
    parser.add_argument("description", help="Descripción de la aplicación a generar")
    parser.add_argument("--name", default=None, help="Nombre del proyecto (opcional)")
    parser.add_argument(
        "--stack",
        default="auto",
        choices=["auto", "fastapi-react", "flask-vanilla"],
        help="Stack predefinido (default: auto)",
    )
    parser.add_argument("--json", action="store_true", help="Imprime reporte JSON en lugar de texto legible")
    args = parser.parse_args(argv)

    request = BuildRequest(description=args.description, project_name=args.name, stack=args.stack)
    builder = AppBuilder()
    result = builder.build(request)

    if args.json:
        print(json.dumps(result.report(), ensure_ascii=False, indent=2))
        return 0

    print("=" * 70)
    print(f"PROYECTO: {result.project_slug}")
    print(f"DIRECTORIO: {result.project_dir}")
    print("=" * 70)
    print("\nAGENTES Y PASOS:")
    for log in result.logs:
        print(f"  [{log.agent}] {log.step}: {log.status} — {log.message}")
    print("\nARTEFACTOS GENERADOS:")
    for art in result.artifacts:
        print(f"  - {art.path} ({len(art.content)} bytes) — {art.agent}")
    print("\nRESUMEN:")
    print(f"  {result.summary}")
    print("=" * 70)
    return 0


if __name__ == "__main__":
    sys.exit(main())
