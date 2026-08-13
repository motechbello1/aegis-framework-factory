"""Benign GRC compliance-framework data processing for Aegis360AI.

This module only extracts and structures regulatory/compliance text, maps it to
an internal control library, records reviewer decisions, and publishes approved
JSON framework packages. It does not perform security exploitation or access
external systems.
"""
from __future__ import annotations

import hashlib
import json
import re
import sqlite3
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any


def utcnow() -> str:
    return datetime.now(timezone.utc).isoformat()


class RunStatus(str, Enum):
    PROCESSING = "processing"
    AWAITING_REVIEW = "awaiting_review"
    NEEDS_REWORK = "needs_rework"
    APPROVED = "approved"
    REJECTED = "rejected"
    PUBLISHED = "published"


CONTROL_LIBRARY = [
    {"control_id": "AEGIS-GOV-001", "domain": "Governance", "title": "Governance and accountability", "keywords": ["governance", "management", "accountable", "oversight"]},
    {"control_id": "AEGIS-IAM-001", "domain": "Identity & Access", "title": "Access management", "keywords": ["access", "account", "authorised", "privileged"]},
    {"control_id": "AEGIS-IR-001", "domain": "Incident Management", "title": "Incident response and notification", "keywords": ["incident", "breach", "notify", "notification"]},
    {"control_id": "AEGIS-RISK-001", "domain": "Risk Management", "title": "Risk assessment and treatment", "keywords": ["risk", "assessment", "treatment"]},
    {"control_id": "AEGIS-PEOPLE-001", "domain": "People", "title": "Training and awareness", "keywords": ["training", "awareness", "personnel", "staff"]},
    {"control_id": "AEGIS-TPRM-001", "domain": "Third Party", "title": "Third-party due diligence", "keywords": ["third-party", "third party", "vendor", "supplier"]},
    {"control_id": "AEGIS-PRIV-001", "domain": "Privacy", "title": "Privacy management", "keywords": ["privacy", "personal data", "data subject"]},
]


@dataclass
class PipelineAgent:
    name: str
    purpose: str

    def trace(self, summary: str) -> dict[str, Any]:
        return {"agent": self.name, "purpose": self.purpose, "completed_at": utcnow(), "summary": summary}


class FactoryRepository:
    def __init__(self, db_path: str = "./aegis_factory.db") -> None:
        self.db_path = db_path
        self._init()

    def _connect(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init(self) -> None:
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        with self._connect() as conn:
            conn.execute("CREATE TABLE IF NOT EXISTS runs (run_id TEXT PRIMARY KEY, status TEXT NOT NULL, payload TEXT NOT NULL, created_at TEXT NOT NULL, updated_at TEXT NOT NULL)")
            conn.execute("CREATE TABLE IF NOT EXISTS audit (id INTEGER PRIMARY KEY AUTOINCREMENT, run_id TEXT NOT NULL, event_type TEXT NOT NULL, actor TEXT, detail TEXT, created_at TEXT NOT NULL)")

    def save(self, run: dict[str, Any]) -> dict[str, Any]:
        now = utcnow()
        run.setdefault("created_at", now)
        run["updated_at"] = now
        with self._connect() as conn:
            conn.execute(
                "INSERT INTO runs(run_id,status,payload,created_at,updated_at) VALUES(?,?,?,?,?) ON CONFLICT(run_id) DO UPDATE SET status=excluded.status,payload=excluded.payload,updated_at=excluded.updated_at",
                (run["run_id"], run["status"], json.dumps(run), run["created_at"], run["updated_at"]),
            )
        return run

    def get(self, run_id: str) -> dict[str, Any]:
        with self._connect() as conn:
            row = conn.execute("SELECT payload FROM runs WHERE run_id=?", (run_id,)).fetchone()
        if not row:
            raise KeyError(run_id)
        return json.loads(row["payload"])

    def list(self, status: str | None = None) -> list[dict[str, Any]]:
        with self._connect() as conn:
            rows = conn.execute("SELECT payload FROM runs ORDER BY created_at DESC").fetchall()
        runs = [json.loads(r["payload"]) for r in rows]
        return [r for r in runs if not status or r["status"] == status]

    def audit(self, run_id: str, event_type: str, actor: str = "system", detail: str = "") -> None:
        with self._connect() as conn:
            conn.execute("INSERT INTO audit(run_id,event_type,actor,detail,created_at) VALUES(?,?,?,?,?)", (run_id, event_type, actor, detail, utcnow()))

    def audit_events(self, run_id: str) -> list[dict[str, Any]]:
        with self._connect() as conn:
            rows = conn.execute("SELECT event_type,actor,detail,created_at FROM audit WHERE run_id=? ORDER BY id", (run_id,)).fetchall()
        return [dict(r) for r in rows]


class FrameworkFactory:
    def __init__(self, repository: FactoryRepository) -> None:
        self.repo = repository
        self.agents = [
            PipelineAgent("source-verifier", "Validate source metadata, rights and provenance"),
            PipelineAgent("requirement-extractor", "Decompose source material into traceable obligations"),
            PipelineAgent("control-mapper", "Map obligations to the Aegis Universal Control Library"),
            PipelineAgent("assessment-builder", "Generate assessment questions"),
            PipelineAgent("evidence-builder", "Generate evidence requests"),
            PipelineAgent("qa-challenger", "Challenge unsupported interpretations and publishing blockers"),
        ]

    def _requirements(self, source_text: str) -> list[dict[str, Any]]:
        requirements = []
        for line in source_text.splitlines():
            text = line.strip()
            if not text or text.startswith("#"):
                continue
            match = re.match(r"(?P<ref>(?:Section|Article|Clause|Part)\s+[\w.()/-]+)\s*[:.-]?\s*(?P<body>.+)", text, flags=re.I)
            ref = match.group("ref") if match else f"Extract {len(requirements)+1}"
            body = match.group("body") if match else text
            lower = body.lower()
            if not any(word in lower for word in ["shall", "must", "should", "required", "may not", "notify"]):
                continue
            kind = "advisory" if " should " in f" {lower} " else "mandatory"
            deadline = None
            deadline_match = re.search(r"within\s+(\d+)\s+(hours?|days?)", lower)
            if deadline_match:
                deadline = f"within {deadline_match.group(1)} {deadline_match.group(2)}"
            frequency = next((f for f in ["daily", "monthly", "quarterly", "annually", "annual", "periodically"] if f in lower), None)
            requirements.append({
                "requirement_id": f"REQ-{len(requirements)+1:04d}",
                "source_reference": ref,
                "source_text": body,
                "interpretation": body.rstrip(".;"),
                "kind": kind,
                "deadline": deadline,
                "frequency": frequency,
            })
        return requirements

    def _map(self, requirement: dict[str, Any]) -> dict[str, Any]:
        text = requirement["source_text"].lower()
        scored = []
        for control in CONTROL_LIBRARY:
            score = sum(1 for keyword in control["keywords"] if keyword in text)
            scored.append((score, control))
        score, control = max(scored, key=lambda item: item[0])
        confidence = min(0.98, 0.56 + score * 0.12) if score else 0.51
        return {
            "requirement_id": requirement["requirement_id"],
            "control_id": control["control_id"],
            "mapping_type": "substantially_equivalent" if confidence >= 0.8 else "supporting" if confidence >= 0.65 else "related",
            "confidence": round(confidence, 2),
            "rationale": f"Matched to {control['title']} using domain and obligation language.",
        }

    def ingest(self, metadata: dict[str, Any], source_text: str, filename: str = "source.txt") -> dict[str, Any]:
        run_id = str(uuid.uuid4())
        source_hash = hashlib.sha256(source_text.encode()).hexdigest()
        traces: list[dict[str, Any]] = []
        verified = bool(metadata.get("source_uri")) and metadata.get("content_rights") not in {None, "unknown", "legal_review_required"}
        traces.append(self.agents[0].trace(f"SHA-256 recorded; provenance_verified={verified}"))

        requirements = self._requirements(source_text)
        traces.append(self.agents[1].trace(f"Extracted {len(requirements)} obligations with source references"))
        mappings = [self._map(req) for req in requirements]
        traces.append(self.agents[2].trace(f"Mapped {len(mappings)} obligations to universal controls"))

        questions = [{"requirement_id": r["requirement_id"], "prompt": f"Is the organisation able to demonstrate compliance with: {r['interpretation']}?"} for r in requirements]
        traces.append(self.agents[3].trace(f"Generated {len(questions)} assessment questions"))
        evidence = [{"requirement_id": r["requirement_id"], "title": "Implementation evidence", "examples": ["approved policy or procedure", "implementation record", "review or approval evidence"]} for r in requirements]
        traces.append(self.agents[4].trace(f"Generated {len(evidence)} evidence requests"))

        findings = []
        if not verified:
            findings.append({"code": "SOURCE_NOT_VERIFIED", "severity": "blocker", "message": "Official source URI and usable content rights must be verified before approval."})
        if not requirements:
            findings.append({"code": "NO_REQUIREMENTS", "severity": "blocker", "message": "No normative obligations were extracted from the source."})
        low_confidence = [m for m in mappings if m["confidence"] < 0.6]
        if low_confidence:
            findings.append({"code": "LOW_CONFIDENCE_MAPPING", "severity": "warning", "message": f"{len(low_confidence)} mappings require closer reviewer attention."})
        traces.append(self.agents[5].trace(f"QA completed with {len(findings)} findings"))

        status = RunStatus.NEEDS_REWORK.value if any(f["severity"] == "blocker" for f in findings) else RunStatus.AWAITING_REVIEW.value
        run = {
            "run_id": run_id,
            "status": status,
            "metadata": metadata,
            "source": {"filename": filename, "sha256": source_hash, "verified": verified, "character_count": len(source_text)},
            "requirements": requirements,
            "controls": CONTROL_LIBRARY,
            "mappings": mappings,
            "assessment_questions": questions,
            "evidence_requirements": evidence,
            "qa_findings": findings,
            "agent_trace": traces,
            "review": None,
            "publication": None,
        }
        self.repo.save(run)
        self.repo.audit(run_id, "pipeline.completed", detail=f"status={status}; requirements={len(requirements)}")
        return run

    def review(self, run_id: str, reviewer: str, decision: str, notes: str = "") -> dict[str, Any]:
        run = self.repo.get(run_id)
        blockers = [f for f in run["qa_findings"] if f["severity"] == "blocker"]
        if decision == "approve" and blockers:
            raise ValueError("Cannot approve a run with blocking QA findings")
        if decision not in {"approve", "reject"}:
            raise ValueError("decision must be approve or reject")
        run["status"] = RunStatus.APPROVED.value if decision == "approve" else RunStatus.REJECTED.value
        run["review"] = {"reviewer": reviewer, "decision": decision, "notes": notes, "reviewed_at": utcnow()}
        self.repo.save(run)
        self.repo.audit(run_id, "review.recorded", actor=reviewer, detail=decision)
        return run

    def publish(self, run_id: str, publish_dir: str = "./published") -> dict[str, Any]:
        run = self.repo.get(run_id)
        if run["status"] != RunStatus.APPROVED.value:
            raise ValueError("Framework must be human-approved before publication")
        metadata = run["metadata"]
        key = re.sub(r"[^a-z0-9]+", "-", f"{metadata.get('short_name','framework')}-{metadata.get('version','v1')}".lower()).strip("-")
        path = Path(publish_dir)
        path.mkdir(parents=True, exist_ok=True)
        target = path / f"{key}.json"
        if target.exists():
            raise ValueError("Published framework versions are immutable")
        package = {"schema_version": "1.0", "framework_key": key, **{k: v for k, v in run.items() if k not in {"publication"}}}
        target.write_text(json.dumps(package, indent=2), encoding="utf-8")
        run["status"] = RunStatus.PUBLISHED.value
        run["publication"] = {"framework_key": key, "location": str(target), "published_at": utcnow()}
        self.repo.save(run)
        self.repo.audit(run_id, "framework.published", detail=key)
        return run["publication"]
