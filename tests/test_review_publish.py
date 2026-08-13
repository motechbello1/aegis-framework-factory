import pytest

from aegis_factory.database import RunRepository
from aegis_factory.models import ContentRights, IngestTextRequest, RunStatus
from aegis_factory.publisher import AegisPublisher
from aegis_factory.workflow import FrameworkFactory


def test_human_approval_required_before_publication(tmp_path, metadata, source_text):
    repo = RunRepository(tmp_path / "factory.db")
    factory = FrameworkFactory(repo)
    run = factory.ingest_text(IngestTextRequest(metadata=metadata, source_text=source_text))
    publisher = AegisPublisher(repo, tmp_path / "published")
    with pytest.raises(ValueError):
        publisher.publish(run.run_id)
    approved = factory.review(run.run_id, reviewer="GRC Reviewer", decision="approve", notes="Source and mappings checked")
    assert approved.status == RunStatus.APPROVED
    result = publisher.publish(run.run_id)
    assert result.framework_key == "ex-csf-2026"
    assert (tmp_path / "published" / "ex-csf-2026.json").exists()


def test_unverified_source_is_blocked(tmp_path, metadata, source_text):
    meta = metadata.model_copy(update={"source_uri": None, "content_rights": ContentRights.UNKNOWN})
    run = FrameworkFactory(RunRepository(tmp_path / "factory.db")).ingest_text(IngestTextRequest(metadata=meta, source_text=source_text))
    assert run.status == RunStatus.NEEDS_REWORK
    assert any(f.code == "SOURCE_NOT_VERIFIED" for f in run.package.qa_findings)
