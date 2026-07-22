# AI App Builder Agent

> Orquestador multiagente que convierte una descripción en lenguaje natural en una aplicación web mínima lista para copiar, revisar y ejecutar.

Este proyecto demuestra **orquestación de agentes, generación de código y diseño de sistemas AI-First**: no es un generador de código perfecto, es una plataforma donde varios agentes especializados (Arquitecto, Backend, Frontend, QA, DevOps) coordinan su trabajo para materializar una idea de software en segundos.

## ¿Qué demuestra? (10 min con un CTO)

- Input en lenguaje natural → especificación técnica estructurada.
- Múltiples agentes especializados trabajando secuencialmente sobre una misma `spec`.
- Generación de backend, frontend, tests y configuración de despliegue.
- Logs trazables de cada paso del orquestador.
- Motor de IA **enchufable** (OpenAI-compatible): corre local o en cloud cambiando `.env`.

## Stack

- **Lenguaje:** Python 3.11+
- **Motor de IA:** proveedor OpenAI-compatible enchufable (Motor de IA Local/Cloud).
- **Agentes:** Arquitecto → Backend → Frontend → QA → DevOps.
- **Interfaces:** CLI, FastAPI REST.
- **Modelos:** Pydantic para validación de specs.

## Inicio rápido

```bash
git clone https://github.com/MWarrior715/ai-app-builder
cd ai-app-builder
python -m venv .venv
.venv\Scripts\activate          # Windows
# source .venv/bin/activate     # macOS/Linux
pip install -r requirements.txt

cp .env.example .env             # configura tu motor de IA (local o cloud)

python -m app_builder "Crea una API de tareas con autenticación JWT"
```

El proyecto generado se guarda en `outputs/<project_slug>/`.

### Otras interfaces

```bash
# API REST
uvicorn app_builder.api:app --port 8000
# POST /build  {"description": "Crea una API de tareas", "project_name": "TaskManager", "stack": "auto"}
```

## Configuración

| Variable | Descripción | Default |
|---|---|---|
| `OPENAI_BASE_URL` | Endpoint OpenAI-compatible del motor de IA (local o cloud) | `http://localhost:11434/v1` |
| `OPENAI_API_KEY` | API key (placeholder en motor local) | `local-dev-key` |
| `LLM_MODEL` | Modelo generativo | `qwen2.5:7b-instruct` |
| `OUTPUT_DIR` | Directorio donde se generan los proyectos | `./outputs` |

## Estructura

```
ai-app-builder/
├── app_builder/        # núcleo del orquestador
│   ├── providers.py    # interfaz de motor LLM enchufable
│   ├── config.py       # variables de entorno
│   ├── models.py       # estructuras de datos
│   ├── orchestrator.py # motor que coordina agentes
│   ├── artifacts.py    # guardado en disco
│   ├── agents/         # agentes especializados
│   ├── cli.py          # CLI
│   └── api.py          # FastAPI
├── tests/              # smoke tests con LLM falso
├── outputs/            # proyectos generados (gitignored)
└── README.md · ARCHITECTURE.md · DECISIONS.md · ROADMAP.md · CHANGELOG.md
```

## Documentación

- [ARCHITECTURE.md](ARCHITECTURE.md) — diagrama y capas del sistema.
- [DECISIONS.md](DECISIONS.md) — por qué Python puro, por qué agentes secuenciales, etc.
- [ROADMAP.md](ROADMAP.md) — loops de refinamiento, ejecución real de código, UI web.
- [CHANGELOG.md](CHANGELOG.md)

## Licencia

[MIT](LICENSE).
