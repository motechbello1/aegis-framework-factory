from __future__ import annotations

from .base import Agent, AgentResult, now
from ..models import ControlMapping, EvidenceRequirement, Requirement, UniversalControl

DOMAIN_EVIDENCE = {
    "Governance": ["approved policy", "governance charter", "management approval record"],
    "Identity & Access Management": ["access control policy", "user access matrix", "periodic access review record", "privileged account register"],
    "Incident Management": ["incident response plan", "incident register", "notification record", "post-incident review"],
    "Privacy": ["privacy policy", "privacy notice", "lawful basis register", "processing inventory"],
    "Data Subject Rights": ["request register", "request procedure", "response evidence"],
    "Risk Management": ["risk assessment", "risk register", "treatment plan", "approval record"],
    "People & Training": ["training material", "attendance record", "awareness schedule"],
    "Third Party Risk": ["vendor assessment", "data processing agreement", "contract review", "monitoring record"],
    "Audit & Assurance": ["audit report", "control test result", "management response", "remediation evidence"],
    "Data Security": ["encryption configuration", "key management record", "security standard"],
    "Information Lifecycle": ["retention schedule", "disposal log", "deletion evidence"],
    "Regulatory Reporting": ["submitted return", "submission acknowledgement", "approved report", "filing calendar"],
}


class EvidenceBuilderAgent(Agent):
    name = "evidence_builder"

    def run(self, requirements: list[Requirement], controls: list[UniversalControl], mappings: list[ControlMapping]) -> AgentResult[list[EvidenceRequirement]]:
        started = now()
        requirement_by_id = {r.requirement_id: r for r in requirements}
        control_by_id = {c.control_id: c for c in controls}
        evidence: list[EvidenceRequirement] = []
        for mapping in mappings:
            requirement = requirement_by_id[mapping.requirement_id]
            control = control_by_id[mapping.control_id]
            examples = DOMAIN_EVIDENCE.get(control.domain, ["policy or procedure", "implementation record", "review evidence"])
            evidence.append(EvidenceRequirement(requirement_id=requirement.requirement_id, control_id=control.control_id, title=f"Evidence for {control.title}", description=f"Provide current, attributable evidence demonstrating implementation of: {requirement.interpretation}", examples=examples))
        return AgentResult(evidence, self.trace(started, f"generated {len(evidence)} evidence requests"))
