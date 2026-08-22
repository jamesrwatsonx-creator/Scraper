from __future__ import annotations

from datetime import UTC, datetime
from enum import StrEnum
from typing import Any, Literal

from pydantic import BaseModel, Field, HttpUrl, field_validator


def utcnow() -> datetime:
    return datetime.now(UTC)


class CapabilityStatus(StrEnum):
    QUARANTINED = "quarantined"
    CANDIDATE = "candidate"
    TRUSTED = "trusted"
    DEGRADED = "degraded"
    DISABLED = "disabled"


class StepType(StrEnum):
    NAVIGATE = "navigate"
    CLICK = "click"
    FILL = "fill"
    WAIT_FOR = "wait_for"
    EXTRACT_TEXT = "extract_text"
    EXTRACT_ATTR = "extract_attr"
    ASSERT_TEXT = "assert_text"
    ASSERT_URL = "assert_url"


class Evidence(BaseModel):
    url: HttpUrl
    observed_at: datetime = Field(default_factory=utcnow)
    source_type: str = "web"
    excerpt: str | None = None
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)
    content_hash: str | None = None


class CapabilityStep(BaseModel):
    type: StepType
    selector: str | None = None
    value: str | None = None
    output_key: str | None = None
    attribute: str | None = None
    timeout_ms: int = Field(default=10_000, ge=100, le=60_000)

    @field_validator("selector")
    @classmethod
    def selector_required_for_dom_steps(cls, value: str | None, info):
        dom_steps = {
            StepType.CLICK,
            StepType.FILL,
            StepType.WAIT_FOR,
            StepType.EXTRACT_TEXT,
            StepType.EXTRACT_ATTR,
            StepType.ASSERT_TEXT,
        }
        step_type = info.data.get("type")
        if step_type in dom_steps and not value:
            raise ValueError(f"selector is required for {step_type}")
        return value


class Capability(BaseModel):
    id: str
    domain: str
    name: str
    description: str
    goal: str
    input_schema: dict[str, Any] = Field(default_factory=dict)
    output_schema: dict[str, Any] = Field(default_factory=dict)
    steps: list[CapabilityStep]
    required_permissions: list[str] = Field(default_factory=lambda: ["public_web"])
    status: CapabilityStatus = CapabilityStatus.QUARANTINED
    version: int = 1
    success_count: int = 0
    failure_count: int = 0
    consecutive_successes: int = 0
    last_verified_at: datetime | None = None
    created_at: datetime = Field(default_factory=utcnow)
    updated_at: datetime = Field(default_factory=utcnow)
    source_trace_id: str | None = None
    notes: list[str] = Field(default_factory=list)

    @field_validator("domain")
    @classmethod
    def normalize_domain(cls, value: str) -> str:
        return value.lower().strip().removeprefix("www.")


class TraceEvent(BaseModel):
    at: datetime = Field(default_factory=utcnow)
    event: str
    detail: dict[str, Any] = Field(default_factory=dict)


class ExecutionResult(BaseModel):
    ok: bool
    provider: str
    data: dict[str, Any] = Field(default_factory=dict)
    evidence: list[Evidence] = Field(default_factory=list)
    trace: list[TraceEvent] = Field(default_factory=list)
    error: str | None = None
    capability_id: str | None = None


class WebRequest(BaseModel):
    url: HttpUrl
    goal: str = "read_page"
    inputs: dict[str, Any] = Field(default_factory=dict)
    interactive: bool = False


class PageSnapshot(BaseModel):
    url: HttpUrl
    title: str | None = None
    text: str
    html: str | None = None
    links: list[str] = Field(default_factory=list)
    phone_links: list[str] = Field(default_factory=list)
    forms: int = 0
    metadata: dict[str, Any] = Field(default_factory=dict)
    evidence: list[Evidence] = Field(default_factory=list)


class LeadSignal(BaseModel):
    kind: str
    label: str
    rationale: str
    score_delta: int
    confidence: float = Field(ge=0.0, le=1.0)
    evidence: list[Evidence] = Field(default_factory=list)


class OfferScore(BaseModel):
    offer: Literal["voice_ai", "website", "automation"]
    score: int = Field(ge=0, le=100)
    confidence: float = Field(ge=0.0, le=1.0)
    explanation: str


class LeadProfile(BaseModel):
    domain: str
    url: HttpUrl
    business_name: str | None = None
    signals: list[LeadSignal] = Field(default_factory=list)
    offer_scores: list[OfferScore] = Field(default_factory=list)
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    verified_at: datetime = Field(default_factory=utcnow)
    evidence: list[Evidence] = Field(default_factory=list)
    recommended_offer: str | None = None
    why_now: str | None = None


class CapabilityVerification(BaseModel):
    capability_id: str
    ok: bool
    checked_at: datetime = Field(default_factory=utcnow)
    failures: list[str] = Field(default_factory=list)
    result: ExecutionResult | None = None
