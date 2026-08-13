from __future__ import annotations

from pathlib import Path

from .database import RunRepository
from .models import PublishResult, RunStatus


class AegisPublisher:
    def __init__(self, repository: RunRepository, publish_dir: str | Path) -> None:
        self.repository = repository
        self.publish_dir = Path(publish_dir)
        self.publish_dir.mkdir(parents=True, exist_ok=True)
