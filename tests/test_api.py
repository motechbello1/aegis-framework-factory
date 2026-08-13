from fastapi.testclient import TestClient

from aegis_factory.api import create_app


def payload(metadata, source_text):
    return {"metadata": metadata.model_dump(mode="json"), "source_text": source_text, "filename": "standard.md", "media_type": "text/markdown"}


def test_api_end_to_end(tmp_path, metadata, source_text):
    client = TestClient(create_app(str(tmp_path / "factory.db"), str(tmp_path / "published")))
    assert client.get("/health").status_code == 200
    created = client.post("/v1/runs/text", json=payload(metadata, source_text))
    assert created.status_code == 200
    run = created.json()
    run_id = run["run_id"]
    assert run["status"] == "awaiting_review"
    assert client.post(f"/v1/runs/{run_id}/publish").status_code == 409
    reviewed = client.post(f"/v1/runs/{run_id}/review", json={"reviewer": "GRC Reviewer", "decision": "approve", "notes": "Validated"})
    assert reviewed.status_code == 200
    assert reviewed.json()["status"] == "approved"
    published = client.post(f"/v1/runs/{run_id}/publish")
    assert published.status_code == 200
    assert client.get("/v1/runs?status=published").json()[0]["status"] == "published"
    audit = client.get(f"/v1/runs/{run_id}/audit").json()
    assert any(event["event_type"] == "review.recorded" for event in audit)
    assert any(event["event_type"] == "framework.published" for event in audit)


def test_controls_endpoint(tmp_path):
    client = TestClient(create_app(str(tmp_path / "factory.db"), str(tmp_path / "published")))
    controls = client.get("/v1/controls")
    assert controls.status_code == 200
    assert any(control["control_id"] == "AEGIS-IAM-001" for control in controls.json())
