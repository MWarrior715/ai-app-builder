# AI App Builder — API

> Referencia de las interfaces del orquestador multiagente: CLI (`python -m app_builder`) y REST (FastAPI, `app_builder.api:app`).

El orquestador expone dos fachadas sobre el mismo motor (`AppBuilder.build`): una línea de comandos y una API HTTP. Ambas aceptan una `BuildRequest` (descripción en lenguaje natural + opciones) y devuelven un `BuildResult` con la especificación, los artefactos generados y los logs de cada agente.

El motor de IA es enchufable vía variables de entorno: cualquier endpoint OpenAI-compatible (Motor de IA Local/Cloud) sirve cambiando `.env`.

---

## CLI

Punto de entrada: `app_builder.cli:main` (invocado como `python -m app_builder`).

```bash
python -m app_builder "<descripción>" [--name <nombre>] [--stack <stack>] [--json]
```

### Argumentos y flags

| Argumento / Flag | Tipo | Requerido | Default | Descripción |
|---|---|---|---|---|
| `description` | posicional, str | sí | — | Descripción en lenguaje natural de la aplicación a generar. |
| `--name` | str | no | `None` | Nombre del proyecto. Si se omite, lo determina el Arquitecto desde la `spec`. |
| `--stack` | enum | no | `auto` | Stack predefinido. Valores: `auto`, `fastapi-react`, `flask-vanilla`. |
| `--json` | flag | no | `False` | Imprime el reporte completo en JSON en lugar del formato legible. |

### Ejemplo

```bash
python -m app_builder "Crea una API de tareas con autenticación JWT" --name TaskManager --stack fastapi-react
```

Salida legible (resumen):

```
======================================================================
PROYECTO: taskmanager
DIRECTORIO: outputs/taskmanager
======================================================================

AGENTES Y PASOS:
  [architect] spec: done — spec=task-api backend=fastapi frontend=vanilla
  [backend]   code: done — 1 files
  [frontend]  code: done — 3 files
  [qa]        review: done — score=85 ...
  [devops]    deploy: done — 3 files

ARTEFACTOS GENERADOS:
  - spec.json (766 bytes) — architect
  - backend/main.py (105 bytes) — backend
  - frontend/index.html (556 bytes) — frontend
  - frontend/app.js (1684 bytes) — frontend
  - frontend/styles.css (907 bytes) — frontend
  - tests/test_generated.py (824 bytes) — qa
  - Dockerfile (202 bytes) — devops
  - docker-compose.yml (211 bytes) — devops
  - README_PROJECT.md (581 bytes) — devops

RESUMEN:
  Generado proyecto taskmanager con 9 archivos.
======================================================================
```

Con `--json` la salida es el objeto `BuildResult.report()` documentado más abajo.

---

## REST (FastAPI)

### Levantar el servidor

```bash
uvicorn app_builder.api:app --port 8000
```

La app FastAPI se instancia en `app_builder.api:app` (`FastAPI(title="AI App Builder", version="0.1.0")`).

### Endpoints

| Método | Ruta | Descripción |
|---|---|---|
| `GET` | `/health` | Verificación de salud. |
| `POST` | `/build` | Ejecuta el orquestador y devuelve el `BuildResult`. |

### `GET /health`

```bash
curl http://localhost:8000/health
```

```json
{ "status": "ok" }
```

### `POST /build`

Body — `BuildRequestIn` (Pydantic):

| Campo | Tipo | Requerido | Default | Restricciones |
|---|---|---|---|---|
| `description` | str | sí | — | `min_length=10` |
| `project_name` | str \| null | no | `null` | Si es `null`, lo resuelve el Arquitecto. |
| `stack` | str | no | `"auto"` | `auto` · `fastapi-react` · `flask-vanilla` |

Ejemplo:

```bash
curl -X POST http://localhost:8000/build \
  -H "Content-Type: application/json" \
  -d '{"description": "Crea una API de tareas con autenticación JWT", "project_name": "TaskManager", "stack": "auto"}'
```

Respuesta — `BuildResult.report()`:

```json
{
  "project_slug": "taskdemo",
  "project_dir": "outputs/taskdemo",
  "spec": {
    "project_name": "task-api",
    "description": "API simple de tareas con FastAPI y frontend vanilla",
    "stack": { "backend": "fastapi", "frontend": "vanilla", "database": "sqlite" },
    "entities": ["tarea"],
    "endpoints": [
      { "method": "GET",    "path": "/tasks",      "purpose": "listar tareas" },
      { "method": "POST",   "path": "/tasks",      "purpose": "crear tarea" },
      { "method": "PUT",    "path": "/tasks/{id}", "purpose": "actualizar tarea" },
      { "method": "DELETE", "path": "/tasks/{id}", "purpose": "eliminar tarea" }
    ],
    "features": ["CRUD"],
    "constraints": ["sqlite por simplicidad", "frontend vanilla sin frameworks"]
  },
  "artifacts": [
    { "path": "spec.json",                 "agent": "architect", "description": "Especificación técnica generada por el Arquitecto", "size": 766 },
    { "path": "backend/main.py",           "agent": "backend",   "description": "Backend file main.py",    "size": 105 },
    { "path": "frontend/index.html",       "agent": "frontend",  "description": "Frontend file index.html", "size": 556 },
    { "path": "frontend/app.js",           "agent": "frontend",  "description": "Frontend file app.js",     "size": 1684 },
    { "path": "frontend/styles.css",       "agent": "frontend",  "description": "Frontend file styles.css", "size": 907 },
    { "path": "tests/test_generated.py",   "agent": "qa",        "description": "Tests generados por QA",   "size": 824 },
    { "path": "Dockerfile",                "agent": "devops",    "description": "DevOps file Dockerfile",       "size": 202 },
    { "path": "docker-compose.yml",        "agent": "devops",    "description": "DevOps file docker-compose.yml", "size": 211 },
    { "path": "README_PROJECT.md",         "agent": "devops",    "description": "DevOps file README_PROJECT.md", "size": 581 }
  ],
  "logs": [
    { "agent": "architect", "step": "spec",   "status": "started", "message": "" },
    { "agent": "architect", "step": "spec",   "status": "done",    "message": "spec=task-api backend=fastapi frontend=vanilla" },
    { "agent": "backend",   "step": "code",   "status": "started", "message": "" },
    { "agent": "backend",   "step": "code",   "status": "done",    "message": "1 files" },
    { "agent": "frontend",  "step": "code",   "status": "started", "message": "" },
    { "agent": "frontend",  "step": "code",   "status": "done",    "message": "3 files" },
    { "agent": "qa",        "step": "review", "status": "started", "message": "" },
    { "agent": "qa",        "step": "review", "status": "done",    "message": "score=85 ..." },
    { "agent": "devops",    "step": "deploy", "status": "started", "message": "" },
    { "agent": "devops",    "step": "deploy", "status": "done",    "message": "3 files" }
  ],
  "summary": "Generado proyecto taskdemo con 9 archivos."
}
```

### Esquemas

`BuildRequest` (`app_builder.models.BuildRequest`):

| Campo | Tipo | Default |
|---|---|---|
| `description` | `str` | — |
| `project_name` | `str \| None` | `None` |
| `stack` | `str` | `"auto"` |

`BuildResult` (`app_builder.models.BuildResult`):

| Campo | Tipo | Descripción |
|---|---|---|
| `project_slug` | `str` | Slug seguro derivado del nombre (vía `slugify`). |
| `project_dir` | `Path` | Ruta absoluta del proyecto en `OUTPUT_DIR/<project_slug>`. |
| `spec` | `dict` | Especificación técnica producida por el Arquitecto. |
| `artifacts` | `list[Artifact]` | Archivos generados por cada agente. |
| `logs` | `list[LogEntry]` | Trazas `started`/`done`/`error` por agente y paso. |
| `summary` | `str` | Resumen de una línea. |

`Artifact.to_dict()`:

| Campo | Tipo | Descripción |
|---|---|---|
| `path` | `str` | Ruta relativa dentro del proyecto generado. |
| `agent` | `str` | Rol que lo generó (`architect` · `backend` · `frontend` · `qa` · `devops`). |
| `description` | `str` | Descripción breve del artefacto. |
| `size` | `int` | Tamaño del contenido en bytes. |

`LogEntry`:

| Campo | Tipo | Valores |
|---|---|---|
| `agent` | `str` | `architect` · `backend` · `frontend` · `qa` · `devops` |
| `step` | `str` | `spec` · `code` · `review` · `deploy` |
| `status` | `str` | `started` · `done` · `error` |
| `message` | `str` | Mensaje de trazabilidad. |

---

## Output en disco

El orquestador persiste todo en `OUTPUT_DIR/<project_slug>/` (default `./outputs/<project_slug>/`). Cada artefacto se escribe respetando su `path` relativo y además se guarda un `report.json` con el `BuildResult` completo.

Estructura típica de un proyecto generado:

```
outputs/<project_slug>/
├── spec.json                 # especificación técnica (Arquitecto)
├── backend/
│   └── main.py               # código de backend (Backend)
├── frontend/
│   ├── index.html            # (Frontend)
│   ├── app.js
│   └── styles.css
├── tests/
│   └── test_generated.py     # pruebas generadas (QA)
├── Dockerfile                # (DevOps)
├── docker-compose.yml        # (DevOps)
├── README_PROJECT.md         # (DevOps)
└── report.json               # BuildResult completo (orquestador)
```

El contenido exacto varía según la `spec` y el stack elegido; el conjunto de agentes (Arquitecto → Backend → Frontend → QA → DevOps) y el `report.json` son invariantes.