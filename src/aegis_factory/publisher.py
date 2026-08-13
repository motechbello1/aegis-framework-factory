from __future__ import annotations

from pathlib import Path

from .database import RunRepository
from .models import PublishResult, RunStatus


class AegisPublisher:
    def __init__(self, repository: RunRepository, publish_dir: str | Path) -> None:
        self.repository = repository
        self.publish_dir = Path(publish_dir)
        self.publish_dir.mkdir(parents=True, exist_ok=True)

    def publish(self, run_id: str) -> PublishResult:
        run = self.repository.get(run_id)
        if run is None:
            raise KeyError(run_id)
        if run.status != RunStatus.APPROVED:
            raise ValueError("Only human-approved framework packages can be published")
        if run.package is None:
            raise ValueError("Framework package is missing")

        target = self.publish_dir / f"{run.package.framework_key}.json"
        package_json = run.package.model_dump_json(indent=2)
        if target.exists() and target.read_text(encoding="utf-8") != package_json:
            raise ValueError("A published package already exists for this framework key. Published framework versions are immutable; use a new version.")
        target.write_text(package_json, encoding="utf-8")

        run.status = RunStatus.PUBLISHED
        self.repository.save(run)
        self.repository.audit(run_id, "framework.published", "publisher", {"location": str(target)})
        return PublishResult(run_id=run.run_id, framework_key=run.package.framework_key, location=str(target))
