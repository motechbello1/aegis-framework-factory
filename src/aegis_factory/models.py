from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from uuid import uuid4

from pydantic import BaseModel, Field, field_validator


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def new_id(prefix: str) -> str:
    return f"{prefix}-{uuid4().hex[:12].upper()}"


class RunStatus(str, Enum):
    RECEIVED = "received"
    PROCESSING = "processing"
    NEEDS_REWORK = "needs_rework"
    AWAITING_REVIEW = "awaiting_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    PUBLISHED = "published"


class MappingType(str, Enum):
    EXACT = "exact"
    SUBSTANTIALLY_EQUIVALENT = "substantially_equivalent"
    PARTIAL = "partial"
    SUPPORTING = "supporting"
    RELATED = "related"
    ADDITIONAL = "additional"
    CONFLICT = "conflict"
    NO_EQUIVALENCE = "no_equivalence"


class RequirementKind(str, Enum):
    MANDATORY = "mandatory"
    CONDITIONAL = "conditional"
    ADVISORY = "advisory"
    REPORTING = "reporting"
    PROHIBITION = "prohibition"


class ContentRights(str, Enum):
    PUBLIC_REGULATORY = "public_regulatory_document"
    LICENSED = "licensed"
    INTERNAL_ONLY = "internal_use_only"
    REDISTRIBUTION_PERMITTED = "redistribution_permitted"
    CITATION_ONLY = "citation_only"
    RESTRICTED = "restricted"
    UNKNOWN = "unknown_legal_review_required"


class FrameworkMetadata(BaseModel):
    framework_name: str = Field(min_length=3)
    short_name: str = Field(min_length=2, max_length=40)
    country: str = Field(min_length=2)
    regulator: str = Field(min_length=2)
    authority: str = Field(min_length=2)
    industry: str = Field(min_length=2)
    version: str = Field(min_length=1)
    effective_date: str | None = None
    publication_date: str | None = None
    applicability: str = Field(min_length=3)
    source_uri: str | None = None
    content_rights: ContentRights = ContentRights.UNKNOWN
    submitted_by: str = "BPO"

    @field_validator("source_uri")
    @classmethod
    def normalise_source_uri(cls, value: str | None) -> str | None:
        if value is None:
            return None
        value = value.strip()
        return value or None


class SourceArtifact(BaseModel):
    source_id: str = Field(default_factory=lambda: new_id("SRC"))
    filename: str
    media_type: str
    sha256: str
    char_count: int
    extracted_at: datetime = Field(default_factory=utc_now)
    metadata: FrameworkMetadata
    verification_notes: list[str] = Field(default_factory=list)
    verified: bool = False


class Requirement(BaseModel):
    requirement_id: str = Field(default_factory=lambda: new_id("REQ"))
    source_id: str
    source_reference: str
    source_text: str
    interpretation: str
    kind: RequirementKind
    categories: list[str] = Field(default_factory=list)
    frequency: str | None = None
    deadline: str | None = None
    responsible_roles: list[str] = Field(default_factory=list)
    applicability: str | None = None
    confidence: float = Field(ge=0, le=1)


class UniversalControl(BaseModel):
    control_id: str
    title: str
    statement: str
    domain: str
    is_proposed: bool = False


class ControlMapping(BaseModel):
    mapping_id: str = Field(default_factory=lambda: new_id("MAP"))
    requirement_id: str
    control_id: str
    mapping_type: MappingType
    confidence: float = Field(ge=0, le=1)
    rationale: str


class AssessmentQuestion(BaseModel):
    question_id: str = Field(default_factory=lambda: new_id("Q"))
    requirement_id: str
    control_id: str
    prompt: str
    response_options: list[str] = Field(default_factory=lambda: ["Fully implemented", "Partially implemented", "Planned", "Not implemented", "Not applicable"])


class EvidenceRequirement(BaseModel):
    evidence_id: str = Field(default_factory=lambda: new_id("EVD"))
    requirement_id: str
    control_id: str
    title: str
    description: str
    examples: list[str] = Field(default_factory=list)


class QAFinding(BaseModel):
    finding_id: str = Field(default_factory=lambda: new_id("QA"))
    severity: str
    code: str
    message: str
    requirement_id: str | None = None


class AgentTrace(BaseModel):
    agent: str
    version: str
    started_at: datetime
    completed_at: datetime
    output_summary: str


class FrameworkPackage(BaseModel):
    schema_version: str = "1.0.0"
    package_id: str = Field(default_factory=lambda: new_id("PKG"))
    framework_key: str
    metadata: FrameworkMetadata
    source: SourceArtifact
    requirements: list[Requirement]
    controls: list[UniversalControl]
    mappings: list[ControlMapping]
    assessment_questions: list[AssessmentQuestion]
    evidence_requirements: list[EvidenceRequirement]
    qa_findings: list[QAFinding]
    agent_trace: list[AgentTrace]
    generated_at: datetime = Field(default_factory=utc_now)

    @property
    def blocking_findings(self) -> list[QAFinding]:
        return [finding for finding in self.qa_findings if finding.severity == "blocker"]


class FrameworkRun(BaseModel):
    run_id: str = Field(default_factory=lambda: new_id("RUN"))
    status: RunStatus = RunStatus.RECEIVED
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)
    package: FrameworkPackage | None = None


class ReviewDecision(BaseModel):
    reviewer: str = Field(min_length=2)
    decision: str
    notes: str = ""

    @field_validator("decision")
    @classmethod
    def validate_decision(cls, value: str) -> str:
        value = value.lower().strip()
        if value not in {"approve", "reject"}:
            raise ValueError("decision must be approve or reject")
        return value


class IngestTextRequest(BaseModel):
    metadata: FrameworkMetadata
    source_text: str = Field(min_length=20)
    filename: str = "uploaded-source.txt"
    media_type: str = "text/plain"


class PublishResult(BaseModel):
    run_id: str
    framework_key: str
    location: str
    published_at: datetime = Field(default_factory=utc_now)
    remote_status_code: int | None = None
