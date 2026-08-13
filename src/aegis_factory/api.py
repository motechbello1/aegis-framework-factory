"""Benign REST API for the Aegis360AI compliance-framework workflow."""
from __future__ import annotations

import os
from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from .core import CONTROL_LIBRARY, FactoryRepository, FrameworkFactory


class IngestRequest(BaseModel):
    metadata: dict[str, Any]
    source_text: str = Field(min_length=1)
    filename: str = "source.txt"


class ReviewRequest(BaseModel):
    reviewer: str = Field(min_length=2)
    decision: str
    notes: str = ""


def create_app(db_path: str | None = None, publish_dir: str | None = None) -> FastAPI:
    repository = FactoryRepository(db_path or os.getenv("AEGIS_FACTORY_DB", "./aegis_factory.db"))
    factory = FrameworkFactory(repository)
    target_dir = publish_dir or os.getenv("AEGIS_PUBLISH_DIR", "./published")
    app = FastAPI(title="Aegis360AI Framework Factory", version="0.2.0")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://127.0.0.1:5173", "http://localhost:5173", "http://127.0.0.1:8080", "http://localhost:8080"],
        allow_credentials=False,
        allow_methods=["GET", "POST"],
        allow_headers=["Content-Type"],
    )

    @app.get("/health")
    def health():
        return {"status": "ok", "service": "aegis-framework-factory"}

    @app.get("/v1/controls")
    def controls():
        return CONTROL_LIBRARY

    @app.get("/v1/runs")
    def list_runs(status: str | None = None):
        return repository.list(status)

    @app.get("/v1/runs/{run_id}")
    def get_run(run_id: str):
        try:
            run = repository.get(run_id)
            run["audit"] = repository.audit_events(run_id)
            return run
        except KeyError:
            raise HTTPException(404, "Run not found")

    @app.post("/v1/runs/text")
    def ingest_text(request: IngestRequest):
        return factory.ingest(request.metadata, request.source_text, request.filename)

    @app.post("/v1/runs/{run_id}/review")
    def review(run_id: str, request: ReviewRequest):
        try:
            return factory.review(run_id, request.reviewer, request.decision, request.notes)
        except KeyError:
            raise HTTPException(404, "Run not found")
        except ValueError as exc:
            raise HTTPException(409, str(exc))

    @app.post("/v1/runs/{run_id}/publish")
    def publish(run_id: str):
        try:
            return factory.publish(run_id, target_dir)
        except KeyError:
            raise HTTPException(404, "Run not found")
        except ValueError as exc:
            raise HTTPException(409, str(exc))

    return app


app = create_app()
