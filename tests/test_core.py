from __future__ import annotations

import pytest

from scraper.capabilities import CapabilityCompiler, CapabilityRegistry, CapabilityVerifier
from scraper.lead_intel import audit_lead
from scraper.models import Evidence, ExecutionResult, PageSnapshot
from scraper.security import SecurityError, UrlPolicy


def test_url_policy_blocks_localhost():
    with pytest.raises(SecurityError):
        UrlPolicy().validate("http://localhost:8000/private")


def test_compiler_starts_capability_quarantined():
    capability = CapabilityCompiler().compile(
        capability_id="example.search",
        domain="example.com",
        name="Search example",
        description="Search the example site",
        goal="search",
        input_schema={"type": "object", "properties": {"query": {"type": "string"}}},
        steps=[
            {"type": "navigate", "value": "https://example.com"},
            {"type": "fill", "selector": "input[name=q]", "value": "${query}"},
            {"type": "click", "selector": "button[type=submit]"},
            {"type": "wait_for", "selector": "main"},
            {"type": "extract_text", "selector": "main", "output_key": "results"},
        ],
    )
    assert capability.status.value == "quarantined"
    assert capability.domain == "example.com"
    assert capability.steps[-1].output_key == "results"


class AlwaysSuccessfulExecutor:
    async def run(self, capability, inputs):
        return ExecutionResult(ok=True, provider="fake", capability_id=capability.id)


@pytest.mark.asyncio
async def test_verifier_promotes_only_after_observed_successes(tmp_path):
    registry = CapabilityRegistry(tmp_path)
    capability = CapabilityCompiler().compile(
        capability_id="example.read",
        domain="example.com",
        name="Read example",
        description="Read the example page",
        goal="read",
        steps=[{"type": "navigate", "value": "https://example.com"}],
    )
    registry.save(capability)
    verifier = CapabilityVerifier(registry, AlwaysSuccessfulExecutor(), trusted_after=3)

    await verifier.verify(capability)
    assert capability.status.value == "candidate"
    await verifier.verify(capability)
    assert capability.status.value == "candidate"
    await verifier.verify(capability)
    assert capability.status.value == "trusted"


def test_lead_audit_returns_evidence_backed_scores():
    evidence = Evidence(url="https://example.com", source_type="test")
    snapshot = PageSnapshot(
        url="https://example.com",
        title="Example Plumbing",
        text="24/7 emergency service. Call now for a free estimate.",
        phone_links=["tel:+15555550123"],
        forms=0,
        metadata={"has_viewport_meta": True, "meta_description": None},
        evidence=[evidence],
    )

    profile = audit_lead(snapshot)
    voice = next(item for item in profile.offer_scores if item.offer == "voice_ai")
    website = next(item for item in profile.offer_scores if item.offer == "website")

    assert voice.score > website.score
    assert profile.recommended_offer == "voice_ai"
    assert profile.evidence[0].source_type == "test"
    assert any(signal.kind == "after_hours_demand" for signal in profile.signals)
