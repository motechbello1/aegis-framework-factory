from __future__ import annotations

import hashlib

from .base import Agent, AgentResult, now
from ..models import FrameworkMetadata, SourceArtifact


class SourceVerificationAgent(Agent):
    name = "source_verification"

    def run(self, *, text: str, filename: str, media_type: str, metadata: FrameworkMetadata) -> AgentResult[SourceArtifact]:
        started = now()
        notes: list[str] = ["Automated checks validate provenance metadata completeness only; source authenticity remains a human GRC review responsibility."]
        verified = True
        if not metadata.source_uri:
            notes.append("No official source URI supplied; reviewer must verify provenance before production publication.")
            verified = False
        if metadata.content_rights.value.endswith("legal_review_required"):
            notes.append("Content rights are unknown; legal/licensing review is required.")
            verified = False
        if len(text.strip()) < 100:
            notes.append("Source text is unusually short and may be incomplete.")
            verified = False
        source = SourceArtifact(filename=filename, media_type=media_type, sha256=hashlib.sha256(text.encode("utf-8")).hexdigest(), char_count=len(text), metadata=metadata, verification_notes=notes, verified=verified)
        return AgentResult(source, self.trace(started, f"hashed and checked source; verified={verified}"))
