from __future__ import annotations

from typing import Any

from .capabilities import CapabilityRegistry
from .models import CapabilityStatus, ExecutionResult, TraceEvent, WebRequest
from .providers import BrowserExecutor, HttpExtractor, ProviderFallback, domain_for


class CapabilityRouter:
    """Choose the least expensive deterministic execution path that can satisfy a request."""

    def __init__(
        self,
        *,
        registry: CapabilityRegistry | None = None,
        http: HttpExtractor | None = None,
        browser: BrowserExecutor | None = None,
        fallbacks: list[ProviderFallback] | None = None,
    ):
        self.registry = registry or CapabilityRegistry()
        self.http = http or HttpExtractor()
        self.browser = browser or BrowserExecutor()
        self.fallbacks = fallbacks or []

    def find_capability(self, url: str, goal: str):
        domain = domain_for(url)
        matches = [
            item
            for item in self.registry.list(domain=domain)
            if item.goal == goal and item.status is CapabilityStatus.TRUSTED
        ]
        if not matches:
            return None
        return sorted(
            matches,
            key=lambda item: (item.consecutive_successes, item.success_count, item.version),
            reverse=True,
        )[0]

    async def execute(self, request: WebRequest) -> ExecutionResult:
        url = str(request.url)
        capability = self.find_capability(url, request.goal)
        if capability:
            result = await self.browser.run(capability, request.inputs)
            result.trace.insert(
                0,
                TraceEvent(
                    event="route_selected",
                    detail={"route": "trusted_capability", "capability_id": capability.id},
                ),
            )
            if result.ok:
                return result

        # Public read-only requests should not pay browser cost unless necessary.
        if not request.interactive and request.goal in {"read_page", "fetch", "inspect"}:
            try:
                snapshot = await self.http.fetch(url)
                return ExecutionResult(
                    ok=True,
                    provider=self.http.name,
                    data=snapshot.model_dump(mode="json"),
                    evidence=snapshot.evidence,
                    trace=[TraceEvent(event="route_selected", detail={"route": "direct_http"})],
                )
            except Exception as exc:
                http_error = str(exc)
        else:
            http_error = None

        for fallback in self.fallbacks:
            if await fallback.supports(url, request.goal):
                result = await fallback.execute(url, request.goal, request.inputs)
                if result.ok:
                    result.trace.insert(
                        0,
                        TraceEvent(
                            event="route_selected",
                            detail={"route": "external_fallback", "provider": fallback.name},
                        ),
                    )
                    return result

        # Live goal-planning is intentionally a separate agent concern. The router
        # does not pretend an unimplemented planner successfully executed a site.
        return ExecutionResult(
            ok=False,
            provider="router",
            error=(
                "No verified capability or provider could satisfy this request. "
                "A live browser planner must discover the workflow before it can be compiled."
                + (f" Direct HTTP error: {http_error}" if http_error else "")
            ),
            trace=[TraceEvent(event="route_exhausted", detail={"goal": request.goal})],
        )

    async def fetch(self, url: str) -> ExecutionResult:
        return await self.execute(WebRequest(url=url, goal="read_page", interactive=False))

    async def run_capability(self, capability_id: str, inputs: dict[str, Any]) -> ExecutionResult:
        capability = self.registry.get(capability_id)
        if not capability:
            return ExecutionResult(ok=False, provider="router", error="capability not found")
        if capability.status is not CapabilityStatus.TRUSTED:
            return ExecutionResult(
                ok=False,
                provider="router",
                error=f"capability is not trusted: {capability.status.value}",
                capability_id=capability.id,
            )
        return await self.browser.run(capability, inputs)
