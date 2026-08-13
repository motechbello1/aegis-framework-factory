from aegis_factory.database import RunRepository
from aegis_factory.models import IngestTextRequest, RunStatus
from aegis_factory.workflow import FrameworkFactory


def test_pipeline_builds_traceable_package(tmp_path, metadata, source_text):
    repo = RunRepository(tmp_path / "factory.db")
    run = FrameworkFactory(repo).ingest_text(IngestTextRequest(metadata=metadata, source_text=source_text, filename="standard.md", media_type="text/markdown"))
    assert run.status == RunStatus.AWAITING_REVIEW
    assert run.package is not None
    assert len(run.package.requirements) == 6
    assert len(run.package.mappings) == 6
    assert len(run.package.assessment_questions) == 6
    assert len(run.package.evidence_requirements) == 6
    assert not run.package.blocking_findings
    assert all(r.source_reference for r in run.package.requirements)


def test_privileged_access_maps_to_iam(tmp_path, metadata, source_text):
    run = FrameworkFactory(RunRepository(tmp_path / "factory.db")).ingest_text(IngestTextRequest(metadata=metadata, source_text=source_text))
    requirement = next(r for r in run.package.requirements if "privileged" in r.source_text.lower())
    mapping = next(m for m in run.package.mappings if m.requirement_id == requirement.requirement_id)
    assert mapping.control_id == "AEGIS-IAM-001"


def test_advisory_language_remains_advisory(tmp_path, metadata, source_text):
    run = FrameworkFactory(RunRepository(tmp_path / "factory.db")).ingest_text(IngestTextRequest(metadata=metadata, source_text=source_text))
    training = next(r for r in run.package.requirements if "training" in r.source_text.lower())
    assert training.kind.value == "advisory"
