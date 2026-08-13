from __future__ import annotations

import re
from collections import Counter

from .base import Agent, AgentResult, now
from ..models import Requirement, RequirementKind, SourceArtifact

NORMATIVE = re.compile(r"\b(shall|must|required to|is required to|should|may not|must not|shall not|prohibited|within\s+\d+\s+(?:hours?|days?|months?|years?))\b", re.IGNORECASE)
DEADLINE = re.compile(r"\bwithin\s+\d+\s+(?:hours?|days?|months?|years?)\b", re.IGNORECASE)
FREQUENCY = re.compile(r"\b(annually|annual|quarterly|monthly|weekly|semi-annual(?:ly)?|every\s+\d+\s+(?:months?|years?))\b", re.IGNORECASE)
SECTION = re.compile(r"^\s*((?:section|article|clause|part|schedule)\s+[\w.()/-]+)\s*[:.-]?\s*(.*)$", re.IGNORECASE)


def classify(text: str) -> RequirementKind:
    lower = text.lower()
    if any(token in lower for token in ("must not", "shall not", "may not", "prohibited")):
        return RequirementKind.PROHIBITION
    if any(token in lower for token in ("report", "return", "notify", "notification", "submit", "file")):
        return RequirementKind.REPORTING
    if "should" in lower:
        return RequirementKind.ADVISORY
    if "if " in lower or "where " in lower or "when " in lower:
        return RequirementKind.CONDITIONAL
    return RequirementKind.MANDATORY


def categories_for(text: str) -> list[str]:
    lower = text.lower()
    rules = {"privacy": ["privacy", "personal data", "data subject", "consent"], "security": ["security", "access", "encrypt", "incident", "breach"], "governance": ["management", "board", "policy", "officer", "governance"], "reporting": ["report", "return", "notify", "submit", "filing"], "third_party": ["vendor", "processor", "third party", "third-party", "supplier"], "training": ["training", "awareness", "staff", "personnel"]}
    found = [category for category, words in rules.items() if any(word in lower for word in words)]
    return found or ["operational"]


def role_hints(text: str) -> list[str]:
    lower = text.lower()
    roles: list[str] = []
    if "data protection officer" in lower or "dpo" in lower:
        roles.append("DPO")
    if "board" in lower or "management" in lower:
        roles.append("Management")
    if "security" in lower or "incident" in lower:
        roles.append("CISO / Security")
    return roles or ["Compliance Owner"]


def sentence_chunks(text: str) -> list[tuple[str, str]]:
    chunks: list[tuple[str, str]] = []
    current_ref = "Source"
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        section_match = SECTION.match(line)
        if section_match:
            current_ref = section_match.group(1)
            line = section_match.group(2).strip()
            if not line:
                continue
        for sentence in re.split(r"(?<=[.!?;])\s+(?=[A-Z0-9])", line):
            sentence = sentence.strip(" -*\t")
            if sentence:
                chunks.append((current_ref, sentence))
    return chunks


class RequirementExtractionAgent(Agent):
    name = "requirement_extraction"

    def run(self, *, text: str, source: SourceArtifact) -> AgentResult[list[Requirement]]:
        started = now()
        requirements: list[Requirement] = []
        for reference, sentence in sentence_chunks(text):
            if not NORMATIVE.search(sentence):
                continue
            deadline_match = DEADLINE.search(sentence)
            frequency_match = FREQUENCY.search(sentence)
            interpretation = re.sub(r"\s+", " ", sentence).strip()
            requirements.append(Requirement(source_id=source.source_id, source_reference=reference, source_text=sentence, interpretation=interpretation, kind=classify(sentence), categories=categories_for(sentence), frequency=frequency_match.group(0) if frequency_match else None, deadline=deadline_match.group(0) if deadline_match else None, responsible_roles=role_hints(sentence), applicability=source.metadata.applicability, confidence=0.88 if reference != "Source" else 0.76))
        kinds = Counter(requirement.kind.value for requirement in requirements)
        summary = f"extracted {len(requirements)} normative requirements; kinds={dict(kinds)}"
        return AgentResult(requirements, self.trace(started, summary))
