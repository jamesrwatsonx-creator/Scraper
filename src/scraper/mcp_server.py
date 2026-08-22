from __future__ import annotations

from mcp.server.fastmcp import FastMCP

from .capabilities import CapabilityRegistry, CapabilityVerifier
from .lead_intel import audit_lead
from .providers import BrowserExecutor, HttpExtractor
from .router import CapabilityRouter

mcp = FastMCP("scraper")
registry = CapabilityRegistry()
http = HttpExtractor()
browser = BrowserExecutor()
router = CapabilityRouter(registry=registry, http=http, browser=browser)
verifier = CapabilityVerifier(registry, browser)


@mcp.tool()
async def web_fetch(url: str) -> dict:
    """Fetch public web content with provenance using the least expensive route."""
    result = await router.fetch(url)
    return result.model_dump(mode="json")


@mcp.tool()
async def lead_audit(url: str) -> dict:
    """Audit a public business website for evidence-backed sales opportunity signals."""
    snapshot = await http.fetch(url)
    return audit_lead(snapshot).model_dump(mode="json")


@mcp.tool()
def capability_discover(domain: str, goal: str = "") -> list[dict]:
    """Find compiled capabilities already learned for a domain."""
    items = registry.list(domain=domain)
    if goal:
        items = [item for item in items if item.goal == goal]
    return [item.model_dump(mode="json") for item in items]


@mcp.tool()
async def capability_run(capability_id: str, inputs: dict | None = None) -> dict:
    """Run a trusted compiled website capability."""
    result = await router.run_capability(capability_id, inputs or {})
    return result.model_dump(mode="json")


@mcp.tool()
async def capability_verify(capability_id: str, inputs: dict | None = None) -> dict:
    """Replay a capability's assertions and update its observed trust state."""
    capability = registry.get(capability_id)
    if not capability:
        return {"ok": False, "error": "capability not found"}
    result = await verifier.verify(capability, inputs or {})
    return result.model_dump(mode="json")


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
