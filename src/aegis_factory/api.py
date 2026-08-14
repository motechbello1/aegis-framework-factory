from __future__ import annotations

import json
import os

from fastapi import FastAPI, File, Form, HTTPException, Query, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from .catalog import CONTROL_CATALOG
from .database import RunRepository
from .models import FrameworkMetadata, IngestTextRequest, ReviewDecision
from .parsers import UnsupportedDocumentError, extract_text
from .publisher import AegisPublisher
from .supabase_repository import SupabaseRunRepository
from .workflow import FrameworkFactory


def build_repository(db_path: str | None = None):
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_PUBLISHABLE_KEY")
    factory_secret = os.getenv("AEGIS_FACTORY_SUPABASE_SECRET")
    configured = [bool(supabase_url), bool(supabase_key), bool(factory_secret)]
    if any(configured) and not all(configured):
        raise RuntimeError(
            "Supabase persistence is partially configured. SUPABASE_URL, "
            "SUPABASE_PUBLISHABLE_KEY and AEGIS_FACTORY_SUPABASE_SECRET must all be set."
        )
    if all(configured):
        return SupabaseRunRepository(supabase_url, supabase_key, factory_secret)
    return RunRepository(db_path)


def create_app(db_path: str | None = None, publish_dir: str | None = None) -> FastAPI:
    repository = build_repository(db_path)
    factory = FrameworkFactory(repository)
    publisher = AegisPublisher(repository, publish_dir or "./published")

    app = FastAPI(title="Aegis360AI Framework Factory", version="0.2.0", description="Builds source-traceable compliance framework packages and gates publication behind human GRC review.")
    allowed_origins = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "https://aegis-framework-factory.vercel.app",
    ]
    extra_origin = os.getenv("AEGIS_FACTORY_FRONTEND_ORIGIN")
    if extra_origin and extra_origin not in allowed_origins:
        allowed_origins.append(extra_origin)
    app.add_middleware(CORSMiddleware, allow_origins=allowed_origins, allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

    @app.get("/health")
    def health() -> dict:
        persistence = "supabase" if isinstance(repository, SupabaseRunRepository) else "sqlite"
        return {"status": "ok", "service": "aegis-framework-factory", "persistence": persistence}

    @app.get("/v1/runs")
    def list_runs(status: str | None = Query(default=None), limit: int = Query(default=100, ge=1, le=500)) -> list[dict]:
        return [run.model_dump(mode="json") for run in repository.list_runs(status=status, limit=limit)]

    @app.get("/v1/controls")
    def list_controls() -> list[dict]:
        return [control.model_dump(mode="json") for control in CONTROL_CATALOG]

    @app.post("/v1/runs/text")
    def ingest_text(request: IngestTextRequest) -> dict:
        return factory.ingest_text(request).model_dump(mode="json")

    @app.post("/v1/runs/file")
    async def ingest_file(file: UploadFile = File(...), metadata_json: str = Form(...)) -> dict:
        try:
            metadata = FrameworkMetadata.model_validate(json.loads(metadata_json))
            raw = await file.read()
            text = extract_text(raw, file.filename or "source", file.content_type)
        except (json.JSONDecodeError, ValueError, UnsupportedDocumentError) as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        request = IngestTextRequest(metadata=metadata, source_text=text, filename=file.filename or "source", media_type=file.content_type or "application/octet-stream")
        return factory.ingest_text(request).model_dump(mode="json")

    @app.get("/v1/runs/{run_id}")
    def get_run(run_id: str) -> dict:
        run = repository.get(run_id)
        if run is None:
            raise HTTPException(status_code=404, detail="Run not found")
        return run.model_dump(mode="json")

    @app.get("/v1/runs/{run_id}/audit")
    def get_audit(run_id: str) -> list[dict]:
        if repository.get(run_id) is None:
            raise HTTPException(status_code=404, detail="Run not found")
        return repository.list_audit(run_id)

    @app.post("/v1/runs/{run_id}/review")
    def review(run_id: str, decision: ReviewDecision) -> dict:
        try:
            run = factory.review(run_id, reviewer=decision.reviewer, decision=decision.decision, notes=decision.notes)
        except KeyError as exc:
            raise HTTPException(status_code=404, detail="Run not found") from exc
        except ValueError as exc:
            raise HTTPException(status_code=409, detail=str(exc)) from exc
        return run.model_dump(mode="json")

    @app.post("/v1/runs/{run_id}/publish")
    def publish(run_id: str) -> dict:
        try:
            return publisher.publish(run_id).model_dump(mode="json")
        except KeyError as exc:
            raise HTTPException(status_code=404, detail="Run not found") from exc
        except ValueError as exc:
            raise HTTPException(status_code=409, detail=str(exc)) from exc

    return app


app = create_app()
