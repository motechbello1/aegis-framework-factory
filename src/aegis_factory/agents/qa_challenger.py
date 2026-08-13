from __future__ import annotations

from collections import Counter

from .base import Agent, AgentResult, now
from ..models import AssessmentQuestion, ControlMapping, EvidenceRequirement, QAFinding, Requirement, SourceArtifact


class QAChallengeAgent(Agent):
    name = "qa_challenge"

    def run(self, *, source: SourceArtifact, requirements: list[Requirement], mappings: list[ControlMapping], questions: list[AssessmentQuestion], evidence: list[EvidenceRequirement]) -> AgentResult[list[QAFinding]]:
        started = now()
        findings: list[QAFinding] = []
        if not source.verified:
            findings.append(QAFinding(severity="blocker", code="SOURCE_NOT_VERIFIED", message="Source provenance or content rights are not fully verified. Human reviewer must verify before publication."))
        if not requirements:
            findings.append(QAFinding(severity="blocker", code="NO_REQUIREMENTS", message="No normative requirements were extracted from the source."))
        mapping_by_requirement = {m.requirement_id: m for m in mappings}
        question_requirements = {q.requirement_id for q in questions}
        evidence_requirements = {e.requirement_id for e in evidence}
        for requirement in requirements:
            if not requirement.source_reference:
                findings.append(QAFinding(severity="blocker", code="MISSING_SOURCE_REFERENCE", message="Requirement has no traceable source reference.", requirement_id=requirement.requirement_id))
            if requirement.requirement_id not in mapping_by_requirement:
                findings.append(QAFinding(severity="blocker", code="UNMAPPED_REQUIREMENT", message="Requirement has no Universal Control mapping.", requirement_id=requirement.requirement_id))
            if requirement.requirement_id not in question_requirements:
                findings.append(QAFinding(severity="warning", code="MISSING_ASSESSMENT", message="Requirement has no generated assessment question.", requirement_id=requirement.requirement_id))
            if requirement.requirement_id not in evidence_requirements:
                findings.append(QAFinding(severity="warning", code="MISSING_EVIDENCE", message="Requirement has no evidence request.", requirement_id=requirement.requirement_id))
            if "should" in requirement.source_text.lower() and requirement.kind.value == "mandatory":
                findings.append(QAFinding(severity="blocker", code="MODALITY_MISMATCH", message="Advisory language was classified as mandatory.", requirement_id=requirement.requirement_id))
        for mapping in mappings:
            if mapping.confidence < 0.65:
                findings.append(QAFinding(severity="warning", code="LOW_MAPPING_CONFIDENCE", message=f"Control mapping confidence is {mapping.confidence:.0%}; reviewer should validate or remap.", requirement_id=mapping.requirement_id))
        counts = Counter(f.severity for f in findings)
        return AgentResult(findings, self.trace(started, f"qa completed; findings={dict(counts)}"))
