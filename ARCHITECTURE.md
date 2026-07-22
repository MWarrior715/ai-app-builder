# AI App Builder — Arquitectura

## Diagrama conceptual

```
Usuario
  │ "Crea una API de tareas con autenticación JWT"
  ▼
┌─────────────────────────────────────────────┐
│  Orquestador (AppBuilder)                   │
│  Recibe BuildRequest, ejecuta agentes,      │
│  guarda artefactos y reporte.               │
└─────────────────────────────────────────────┘
  │
  ├──▶ Arquitecto: spec.json (stack, endpoints, entidades)
  │
  ├──▶ Backend: main.py, requirements.txt...
  │
  ├──▶ Frontend: index.html, app.js, styles.css...
  │
  ├──▶ QA: tests/test_generated.py, score de revisión
  │
  └──▶ DevOps: Dockerfile, docker-compose.yml, README_PROJECT.md

              │
              ▼
        outputs/<project_slug>/
        ├── spec.json
        ├── backend/
        ├── frontend/
        ├── tests/
        ├── Dockerfile
        ├── docker-compose.yml
        ├── README_PROJECT.md
        └── report.json
```

## Capas

1. **Proveedores de IA** (`providers.py`): abstracción `LLMProvider` con implementación OpenAI-compatible. Permite cambiar entre motor local y cloud sin tocar el resto del código.
2. **Configuración** (`config.py`): variables de entorno vía `.env`, rutas resueltas contra la raíz del repo.
3. **Modelos** (`models.py`): dataclasses inmutables para `BuildRequest`, `BuildResult`, `Artifact`, `LogEntry`.
4. **Agentes** (`agents/`): cada agente recibe la especificación y/o artefactos previos, llama al LLM, parsea la respuesta y devuelve nuevos artefactos + logs.
5. **Orquestador** (`orchestrator.py`): coordina agentes en orden fijo. Guarda todo en disco y genera `report.json`.
6. **Interfaces** (`cli.py`, `api.py`): CLI para demos rápidas, FastAPI para integración.

## Decisiones clave

- **Agentes secuenciales, no concurrentes.** El output de cada agente alimenta al siguiente (Backend depende de la spec, QA depende del código). Esto hace visible la cadena de dependencias en un demo.
- **No se ejecuta el código generado.** El alcance es generar scaffold con trazabilidad. Ejecutar y corregir códigos auto-generados es material de ROADMAP.
- **Formato `---FILE: path---`.** Se usa un delimitador simple para que el LLM devuelva múltiples archivos en una sola respuesta, reduciendo llamadas.
