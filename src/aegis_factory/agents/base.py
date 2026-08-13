from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Generic, TypeVar

from ..models import AgentTrace

T = TypeVar("T")


def now() -> datetime:
    return datetime.now(timezone.utc)


@dataclass
class AgentResult(Generic[T]):
    value: T
    trace: AgentTrace


class Agent:
    name = "agent"
    version = "1.0.0"

    def trace(self, started: datetime, summary: str) -> AgentTrace:
        return AgentTrace(agent=self.name, version=self.version, started_at=started, completed_at=now(), output_summary=summary)
