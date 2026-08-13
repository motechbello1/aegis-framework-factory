from __future__ import annotations

import json
import os
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator

from .models import FrameworkRun, utc_now


class RunRepository:
    def __init__(self, db_path: str | Path | None = None) -> None:
        self.db_path = Path(db_path or os.getenv("AEGIS_FACTORY_DB", "./aegis_factory.db"))
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._initialise()

    @contextmanager
    def connect(self) -> Iterator[sqlite3.Connection]:
        connection = sqlite3.connect(self.db_path)
        connection.row_factory = sqlite3.Row
        try:
            yield connection
            connection.commit()
        finally:
            connection.close()

    def _initialise(self) -> None:
        with self.connect() as connection:
            connection.executescript("""
                CREATE TABLE IF NOT EXISTS framework_runs (
                    run_id TEXT PRIMARY KEY,
                    status TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    package_json TEXT
                );
                CREATE TABLE IF NOT EXISTS review_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    run_id TEXT NOT NULL,
                    reviewer TEXT NOT NULL,
                    decision TEXT NOT NULL,
                    notes TEXT NOT NULL,
                    created_at TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS audit_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    run_id TEXT NOT NULL,
                    event_type TEXT NOT NULL,
                    actor TEXT NOT NULL,
                    payload_json TEXT NOT NULL,
                    created_at TEXT NOT NULL
                );
            """)

    def create(self, run: FrameworkRun) -> FrameworkRun:
        with self.connect() as connection:
            connection.execute("INSERT INTO framework_runs(run_id, status, created_at, updated_at, package_json) VALUES (?, ?, ?, ?, ?)", (run.run_id, run.status.value, run.created_at.isoformat(), run.updated_at.isoformat(), run.package.model_dump_json() if run.package else None))
        self.audit(run.run_id, "run.created", "system", {"status": run.status.value})
        return run

    def save(self, run: FrameworkRun) -> FrameworkRun:
        run.updated_at = utc_now()
        with self.connect() as connection:
            connection.execute("UPDATE framework_runs SET status=?, updated_at=?, package_json=? WHERE run_id=?", (run.status.value, run.updated_at.isoformat(), run.package.model_dump_json() if run.package else None, run.run_id))
        return run

    def get(self, run_id: str) -> FrameworkRun | None:
        with self.connect() as connection:
            row = connection.execute("SELECT * FROM framework_runs WHERE run_id=?", (run_id,)).fetchone()
        if row is None:
            return None
        payload = {"run_id": row["run_id"], "status": row["status"], "created_at": row["created_at"], "updated_at": row["updated_at"], "package": json.loads(row["package_json"]) if row["package_json"] else None}
        return FrameworkRun.model_validate(payload)

    def list_runs(self, status: str | None = None, limit: int = 100) -> list[FrameworkRun]:
        limit = max(1, min(limit, 500))
        with self.connect() as connection:
            if status:
                rows = connection.execute("SELECT * FROM framework_runs WHERE status=? ORDER BY updated_at DESC LIMIT ?", (status, limit)).fetchall()
            else:
                rows = connection.execute("SELECT * FROM framework_runs ORDER BY updated_at DESC LIMIT ?", (limit,)).fetchall()
        runs: list[FrameworkRun] = []
        for row in rows:
            payload = {"run_id": row["run_id"], "status": row["status"], "created_at": row["created_at"], "updated_at": row["updated_at"], "package": json.loads(row["package_json"]) if row["package_json"] else None}
            runs.append(FrameworkRun.model_validate(payload))
        return runs

    def add_review(self, run_id: str, reviewer: str, decision: str, notes: str) -> None:
        with self.connect() as connection:
            connection.execute("INSERT INTO review_events(run_id, reviewer, decision, notes, created_at) VALUES (?, ?, ?, ?, ?)", (run_id, reviewer, decision, notes, utc_now().isoformat()))
        self.audit(run_id, "review.recorded", reviewer, {"decision": decision, "notes": notes})

    def audit(self, run_id: str, event_type: str, actor: str, payload: dict) -> None:
        with self.connect() as connection:
            connection.execute("INSERT INTO audit_events(run_id, event_type, actor, payload_json, created_at) VALUES (?, ?, ?, ?, ?)", (run_id, event_type, actor, json.dumps(payload, sort_keys=True), utc_now().isoformat()))

    def list_audit(self, run_id: str) -> list[dict]:
        with self.connect() as connection:
            rows = connection.execute("SELECT event_type, actor, payload_json, created_at FROM audit_events WHERE run_id=? ORDER BY id", (run_id,)).fetchall()
        return [{"event_type": row["event_type"], "actor": row["actor"], "payload": json.loads(row["payload_json"]), "created_at": row["created_at"]} for row in rows]
