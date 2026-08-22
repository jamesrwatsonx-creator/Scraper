from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from .models import (
    Capability,
    CapabilityStatus,
    CapabilityStep,
    CapabilityVerification,
    ExecutionResult,
    utcnow,
)
from .providers import BrowserExecutor
from .security import validate_step_type


class CapabilityRegistry:
    """Filesystem-backed registry for versionable, inspectable capabilities."""

    def __init__(self, root: str | Path = "scraper-data/capabilities"):
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def _safe_id(capability_id: str) -> str:
        safe = re.sub(r"[^a-zA-Z0-9._-]+", "-", capability_id).strip("-")
        if not safe:
            raise ValueError("capability id must contain a safe character")
        return safe

    def _path(self, capability_id: str) -> Path:
        return self.root / f"{self._safe_id(capability_id)}.json"

    def save(self, capability: Capability) -> Capability:
        capability.updated_at = utcnow()
        self._path(capability.id).write_text(
            capability.model_dump_json(indent=2), encoding="utf-8"
        )
        return capability

    def get(self, capability_id: str) -> Capability | None:
        path = self._path(capability_id)
        if not path.exists():
            return None
        return Capability.model_validate_json(path.read_text(encoding="utf-8"))

    def list(self, *, domain: str | None = None, trusted_only: bool = False) -> list[Capability]:
        capabilities: list[Capability] = []
        for path in self.root.glob("*.json"):
            try:
                item = Capability.model_validate_json(path.read_text(encoding="utf-8"))
            except (ValueError, json.JSONDecodeError):
                continue
            if domain and item.domain != domain.lower().removeprefix("www."):
                continue
            if trusted_only and item.status is not CapabilityStatus.TRUSTED:
                continue
            capabilities.append(item)
        return sorted(capabilities, key=lambda item: (item.domain, item.name, item.version))


class CapabilityCompiler:
    """Promotes successful browser discoveries into a constrained capability DSL."""

    def compile(
        self,
        *,
        capability_id: str,
        domain: str,
        name: str,
        description: str,
        goal: str,
        steps: list[dict[str, Any] | CapabilityStep],
        input_schema: dict[str, Any] | None = None,
        output_schema: dict[str, Any] | None = None,
        source_trace_id: str | None = None,
    ) -> Capability:
        parsed_steps: list[CapabilityStep] = []
        for raw in steps:
            step = raw if isinstance(raw, CapabilityStep) else CapabilityStep.model_validate(raw)
            validate_step_type(step.type.value)
            parsed_steps.append(step)

        if not parsed_steps:
            raise ValueError("a capability must contain at least one execution step")

        return Capability(
            id=capability_id,
            domain=domain,
            name=name,
            description=description,
            goal=goal,
            steps=parsed_steps,
            input_schema=input_schema or {},
            output_schema=output_schema or {},
            source_trace_id=source_trace_id,
            status=CapabilityStatus.QUARANTINED,
        )


class CapabilityVerifier:
    """Replays a capability and updates trust only from observed outcomes."""

    def __init__(
        self,
        registry: CapabilityRegistry,
        executor: BrowserExecutor,
        *,
        candidate_after: int = 1,
        trusted_after: int = 3,
        degrade_after_failures: int = 2,
    ):
        self.registry = registry
        self.executor = executor
        self.candidate_after = candidate_after
        self.trusted_after = trusted_after
        self.degrade_after_failures = degrade_after_failures

    async def verify(
        self, capability: Capability, inputs: dict[str, Any] | None = None
    ) -> CapabilityVerification:
        result: ExecutionResult = await self.executor.run(capability, inputs or {})
        capability.last_verified_at = utcnow()

        if result.ok:
            capability.success_count += 1
            capability.consecutive_successes += 1
            if capability.consecutive_successes >= self.trusted_after:
                capability.status = CapabilityStatus.TRUSTED
            elif capability.consecutive_successes >= self.candidate_after:
                capability.status = CapabilityStatus.CANDIDATE
            failures: list[str] = []
        else:
            capability.failure_count += 1
            capability.consecutive_successes = 0
            if capability.failure_count >= self.degrade_after_failures:
                capability.status = CapabilityStatus.DEGRADED
            failures = [result.error or "unknown execution failure"]

        self.registry.save(capability)
        return CapabilityVerification(
            capability_id=capability.id,
            ok=result.ok,
            failures=failures,
            result=result,
        )
