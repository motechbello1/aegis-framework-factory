from __future__ import annotations

import re

from .agents.assessment_builder import AssessmentBuilderAgent
from .agents.control_mapper import ControlMappingAgent
from .agents.evidence_builder import EvidenceBuilderAgent
from .agents.qa_challenger import QAChallengeAgent
from .agents.requirement_extractor import RequirementExtractionAgent
from .agents.source_verifier import SourceVerificationAgent
from .database import RunRepository
from .models import FrameworkPackage, FrameworkRun, IngestTextRequest, RunStatus


def framework_key(short_name: str, version: str) -> str:
    value = f"{short_name}-{version}".lower()
    return re.sub(r"[^a-z0-9]+", "-", value).strip("-")


class FrameworkFactory:
    def __init__(self, repository: RunRepository) -> None:
        self.repository = repository
        self.source_verifier = SourceVerificationAgent()
        self.extractor = RequirementExtractionAgent()
        self.mapper = ControlMappingAgent()
        self.assessment_builder = AssessmentBuilderAgent()
        self.evidence_builder = EvidenceBuilderAgent()
        self.qa = QAChallengeAgent()

    def ingest_text(self, request: IngestTextRequest) -> FrameworkRun:
        run = self.repository.create(FrameworkRun(status=RunStatus.PROCESSING))
        traces = []
        source_result = self.source_verifier.run(text=request.source_text, filename=request.filename, media_type=request.media_type, metadata=request.metadata)
        traces.append(source_result.trace)
        requirement_result = self.extractor.run(text=request.source_text, source=source_result.value)
        traces.append(requirement_result.trace)
        mapping_result = self.mapper.run(requirement_result.value)
        controls, mappings = mapping_result.value
        traces.append(mapping_result.trace)
        question_result = self.assessment_builder.run(requirement_result.value, mappings)
        traces.append(question_result.trace)
        evidence_result = self.evidence_builder.run(requirement_result.value, controls, mappings)
        traces.append(evidence_result.trace)
        qa_result = self.qa.run(source=source_result.value, requirements=requirement_result.value, mappings=mappings, questions=question_result.value, evidence=evidence_result.value)
        traces.append(qa_result.trace)
        package = FrameworkPackage(framework_key=framework_key(request.metadata.short_name, request.metadata.version), metadata=request.metadata, source=source_result.value, requirements=requirement_result.value, controls=controls, mappings=mappings, assessment_questions=question_result.value, evidence_requirements=evidence_result.value, qa_findings=qa_result.value, agent_trace=traces)
        run.package = package
        run.status = RunStatus.NEEDS_REWORK if package.blocking_findings else RunStatus.AWAITING_REVIEW
        self.repository.save(run)
        self.repository.audit(run.run_id, "pipeline.completed", "framework_factory", {"requirements": len(package.requirements), "controls": len(package.controls), "mappings": len(package.mappings), "qa_findings": len(package.qa_findings), "status": run.status.value})
        return run

    def review(self, run_id: str, *, reviewer: str, decision: str, notes: str = "") -> FrameworkRun:
        run = self.repository.get(run_id)
        if run is None:
            raise KeyError(run_id)
        if run.package is None:
            raise ValueError("Run has no framework package")
        if decision == "approve":
            if run.package.blocking_findings:
                raise ValueError("Cannot approve a framework package with blocking QA findings")
            run.status = RunStatus.APPROVED
        elif decision == "reject":
            run.status = RunStatus.REJECTED
        else:
            raise ValueError("Unsupported review decision")
        self.repository.add_review(run_id, reviewer, decision, notes)
        return self.repository.save(run)
