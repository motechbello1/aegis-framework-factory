from pathlib import Path

import pytest

from aegis_factory.models import ContentRights, FrameworkMetadata


@pytest.fixture
def metadata():
    return FrameworkMetadata(
        framework_name="Example Financial Services Cybersecurity Standard 2026",
        short_name="EX-CSF",
        country="Nigeria",
        regulator="Example Regulator",
        authority="Example Regulator",
        industry="Financial Services",
        version="2026",
        applicability="Regulated financial institutions",
        source_uri="https://regulator.example/standard-2026",
        content_rights=ContentRights.PUBLIC_REGULATORY,
        submitted_by="BPO Research Team",
    )


@pytest.fixture
def source_text():
    return Path("fixtures/example_standard.md").read_text(encoding="utf-8")
