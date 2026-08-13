from __future__ import annotations

import re

from .base import Agent, AgentResult, now
from ..models import AssessmentQuestion, ControlMapping, Requirement


def make_question(text: str) -> str:
    cleaned = re.sub(r"\s+", " ", text).strip().rstrip(".;")
    replacements = [(r"\bthe organisation shall\b", "Does the organisation"), (r"\bthe organization shall\b", "Does the organisation"), (r"\borganisations shall\b", "Does the organisation"), (r"\borganizations shall\b", "Does the organisation"), (r"\bshall\b", "Does the organisation"), (r"\bmust\b", "Does the organisation"), (r"\bis required to\b", "Does the organisation")]
    for pattern, replacement in replacements:
        candidate = re.sub(pattern, replacement, cleaned, count=1, flags=re.IGNORECASE)
        if candidate != cleaned:
            cleaned = candidate
            break
    if not cleaned.lower().startswith(("does ", "is ", "are ", "has ", "can ")):
        cleaned = f"Is the organisation compliant with this requirement: {cleaned}"
    return cleaned[0].upper() + cleaned[1:] + "?"


class AssessmentBuilderAgent(Agent):
    name = "assessment_builder"

    def run(self, requirements: list[Requirement], mappings: list[ControlMapping]) -> AgentResult[list[AssessmentQuestion]]:
        started = now()
        mapping_by_requirement = {mapping.requirement_id: mapping for mapping in mappings}
        questions = [AssessmentQuestion(requirement_id=requirement.requirement_id, control_id=mapping_by_requirement[requirement.requirement_id].control_id, prompt=make_question(requirement.interpretation)) for requirement in requirements if requirement.requirement_id in mapping_by_requirement]
        return AgentResult(questions, self.trace(started, f"generated {len(questions)} assessment questions"))
