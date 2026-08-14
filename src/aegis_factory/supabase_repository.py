from __future__ import annotations

from typing import Any

import httpx

from .models import FrameworkRun, PublishResult, utc_now


class SupabaseRunRepository:
    """Persistent Framework Factory repository backed by locked-down Supabase RPCs.

    The publishable key identifies the Supabase project, while every RPC also
    requires the server-only Factory secret. Direct table access is revoked and
    RLS remains enabled, so this repository is intended for backend use only.
    """

    def __init__(self, url: str, api_key: str, factory_secret: str, timeout: float = 20.0) -> None:
        self.url = url.rstrip("/")
        self.api_key = api_key
        self.factory_secret = factory_secret
        self.timeout = timeout

    def _rpc(self, function: str, payload: dict[str, Any]) -> Any:
        body = {"p_secret": self.factory_secret, **payload}
        response = httpx.post(
            f"{self.url}/rest/v1/rpc/{function}",
            json=body,
            headers={
                "apikey": self.api_key,
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            timeout=self.timeout,
        )
        if response.status_code >= 400:
            detail = response.text
            if "unauthorized" in detail.lower():
                raise RuntimeError("Supabase rejected the Framework Factory server credential")
            raise RuntimeError(f"Supabase RPC {function} failed ({response.status_code}): {detail}")
        if not response.content:
            return None
        return response.json()

    def create(self, run: FrameworkRun) -> FrameworkRun:
        self._rpc("factory_save_run", {"p_run": run.model_dump(mode="json")})
        self.audit(run.run_id, "run.created", "system", {"status": run.status.value})
        return run

    def save(self, run: FrameworkRun) -> FrameworkRun:
        run.updated_at = utc_now()
        self._rpc("factory_save_run", {"p_run": run.model_dump(mode="json")})
        return run

    def get(self, run_id: str) -> FrameworkRun | None:
        payload = self._rpc("factory_get_run", {"p_run_id": run_id})
        return FrameworkRun.model_validate(payload) if payload else None

    def list_runs(self, status: str | None = None, limit: int = 100) -> list[FrameworkRun]:
        payload = self._rpc(
            "factory_list_runs",
            {"p_status": status, "p_limit": max(1, min(limit, 500))},
        )
        return [FrameworkRun.model_validate(item) for item in (payload or [])]

    def add_review(self, run_id: str, reviewer: str, decision: str, notes: str) -> None:
        self._rpc(
            "factory_add_review",
            {
                "p_run_id": run_id,
                "p_reviewer": reviewer,
                "p_decision": decision,
                "p_notes": notes,
            },
        )
        self.audit(run_id, "review.recorded", reviewer, {"decision": decision, "notes": notes})

    def audit(self, run_id: str, event_type: str, actor: str, payload: dict) -> None:
        self._rpc(
            "factory_add_audit",
            {
                "p_run_id": run_id,
                "p_event_type": event_type,
                "p_actor": actor,
                "p_payload": payload,
            },
        )

    def list_audit(self, run_id: str) -> list[dict]:
        payload = self._rpc("factory_list_audit", {"p_run_id": run_id})
        return payload or []

    def publish_persisted(self, run_id: str) -> PublishResult:
        try:
            payload = self._rpc("factory_publish", {"p_run_id": run_id})
        except RuntimeError as exc:
            text = str(exc)
            if "run_not_found" in text:
                raise KeyError(run_id) from exc
            if "not_approved" in text:
                raise ValueError("Only human-approved framework packages can be published") from exc
            if "package_missing" in text:
                raise ValueError("Framework package is missing") from exc
            if "immutable_version_conflict" in text:
                raise ValueError(
                    "A published package already exists for this framework key. "
                    "Published framework versions are immutable; use a new version."
                ) from exc
            raise
        return PublishResult.model_validate(payload)
