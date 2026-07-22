"""Punto de entrada: `python -m app_builder <descripción>`."""
import sys

from .cli import main

if __name__ == "__main__":
    sys.exit(main())
