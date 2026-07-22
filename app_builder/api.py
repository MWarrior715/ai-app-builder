"""api.py — capa REST delgada sobre el orquestador (FastAPI).

    uvicorn app_builder.api:app --port 8000
    POST /build {"description": "...", "project_name": "...", "stack": "auto"}
"""
from __future__ import annotations

from fastapi import FastAPI
from pydantic import BaseModel, Field

from .models import BuildRequest
from .orchestrator import AppBuilder

app = FastAPI(title="AI App Builder", version="0.1.0")


class BuildRequestIn(BaseModel):
    description: str = Field(..., min_length=10)
    project_name: str | None = None
    stack: str = "auto"


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.post("/build")
def build(req: BuildRequestIn) -> dict:
    builder = AppBuilder()
    request = BuildRequest(
        description=req.description,
        project_name=req.project_name,
        stack=req.stack,
    )
    result = builder.build(request)
    return result.report()
