from __future__ import annotations

from collections import Counter
from datetime import datetime

from pydantic import BaseModel, Field

from .capabilities import CapabilityRegistry
from .models import Capability, CapabilityStatus


class DomainHealth(BaseModel):
    domain: str
    status: str
    capability_count: int
    trusted: int = 0
    candidate: int = 0
    quarantined: int = 0
    degraded: int = 0
    disabled: int = 0
    last_verified_at: datetime | None = None
    issues: list[str] = Field(default_factory=list)


class DoctorReport(BaseModel):
    status: str
    capability_count: int
    domains: list[DomainHealth] = Field(default_factory=list)
    issues: list[str] = Field(default_factory=list)


def _latest_verification(capabilities: list[Capability]) -> datetime | None:
    verified = [item.last_verified_at for item in capabilities if item.last_verified_at is not None]
    return max(verified) if verified else None


def _domain_health(domain: str, capabilities: list[Capability]) -> DomainHealth:
    counts = Counter(item.status for item in capabilities)
    issues: list[str] = []

    if counts[CapabilityStatus.DEGRADED]:
        status = "needs_attention"
        issues.append(f"{counts[CapabilityStatus.DEGRADED]} degraded capability/capabilities")
    elif counts[CapabilityStatus.TRUSTED]:
        status = "healthy"
    elif counts[CapabilityStatus.CANDIDATE] or counts[CapabilityStatus.QUARANTINED]:
        status = "unproven"
        issues.append("No trusted capability is available for this domain")
    else:
        status = "inactive"
        issues.append("All capabilities are disabled or unavailable")

    if counts[CapabilityStatus.DISABLED]:
        issues.append(f"{counts[CapabilityStatus.DISABLED]} disabled capability/capabilities")

    return DomainHealth(
        domain=domain,
        status=status,
        capability_count=len(capabilities),
        trusted=counts[CapabilityStatus.TRUSTED],
        candidate=counts[CapabilityStatus.CANDIDATE],
        quarantined=counts[CapabilityStatus.QUARANTINED],
        degraded=counts[CapabilityStatus.DEGRADED],
        disabled=counts[CapabilityStatus.DISABLED],
        last_verified_at=_latest_verification(capabilities),
        issues=issues,
    )


class ScraperDoctor:
    def __init__(self, registry: CapabilityRegistry):
        self.registry = registry

    def inspect(self, domain: str | None = None) -> DoctorReport:
        capabilities = self.registry.list(domain=domain)
        if not capabilities:
            return DoctorReport(
                status="empty",
                capability_count=0,
                issues=["No capabilities are registered for the requested scope"],
            )

        grouped: dict[str, list[Capability]] = {}
        for capability in capabilities:
            grouped.setdefault(capability.domain, []).append(capability)

        domains = [
            _domain_health(domain_name, grouped[domain_name])
            for domain_name in sorted(grouped)
        ]
        if any(item.status == "needs_attention" for item in domains):
            overall = "needs_attention"
        elif all(item.status == "healthy" for item in domains):
            overall = "healthy"
        else:
            overall = "mixed"

        issues = [
            f"{item.domain}: {issue}"
            for item in domains
            for issue in item.issues
        ]
        return DoctorReport(
            status=overall,
            capability_count=len(capabilities),
            domains=domains,
            issues=issues,
        )
