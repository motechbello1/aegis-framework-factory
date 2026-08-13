from __future__ import annotations

from .base import Agent, AgentResult, now
from ..catalog import CONTROL_CATALOG, CONTROL_KEYWORDS
from ..models import ControlMapping, MappingType, Requirement, UniversalControl


class ControlMappingAgent(Agent):
    name = "control_mapping"

    def run(self, requirements: list[Requirement]) -> AgentResult[tuple[list[UniversalControl], list[ControlMapping]]]:
        started = now()
        controls = {control.control_id: control for control in CONTROL_CATALOG}
        mappings: list[ControlMapping] = []
        for requirement in requirements:
            text = requirement.interpretation.lower()
            scores: list[tuple[int, str]] = []
            for control_id, keywords in CONTROL_KEYWORDS.items():
                score = sum(2 if " " in keyword and keyword in text else 1 for keyword in keywords if keyword in text)
                scores.append((score, control_id))
            best_score, best_control_id = max(scores)
            if best_score == 0:
                proposed_id = f"AEGIS-CAND-{len([c for c in controls.values() if c.is_proposed]) + 1:03d}"
                control = UniversalControl(control_id=proposed_id, title="Proposed control from unmapped obligation", statement=requirement.interpretation, domain=requirement.categories[0].replace("_", " ").title(), is_proposed=True)
                controls[proposed_id] = control
                mapping_type = MappingType.ADDITIONAL
                confidence = 0.55
                rationale = "No sufficiently related control was found in the seed Universal Control Library; proposed a new control for reviewer validation."
            else:
                control = controls[best_control_id]
                confidence = min(0.96, 0.58 + best_score * 0.08)
                if confidence >= 0.9:
                    mapping_type = MappingType.SUBSTANTIALLY_EQUIVALENT
                elif confidence >= 0.75:
                    mapping_type = MappingType.PARTIAL
                else:
                    mapping_type = MappingType.RELATED
                rationale = f"Matched requirement language to {control.title} using domain and obligation keywords."
            mappings.append(ControlMapping(requirement_id=requirement.requirement_id, control_id=control.control_id, mapping_type=mapping_type, confidence=confidence, rationale=rationale))
        used_control_ids = {mapping.control_id for mapping in mappings}
        used_controls = [control for control_id, control in controls.items() if control_id in used_control_ids]
        proposed = sum(control.is_proposed for control in used_controls)
        return AgentResult((used_controls, mappings), self.trace(started, f"mapped {len(mappings)} requirements to {len(used_controls)} controls; proposed={proposed}"))
