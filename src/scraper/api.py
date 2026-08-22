from __future__ import annotations

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field, HttpUrl

from .capabilities import CapabilityRegistry, CapabilityVerifier
from .health import ScraperDoctor
from .lead_intel import audit_lead
from .models import WebRequest
from .native_tools import discover_native_tools
from .providers import BrowserExecutor, HttpExtractor
from .router import CapabilityRouter

app = FastAPI(
    title="Scraper Capability Compiler",
    version="0.1.0",
    description="Turn human web interfaces into verified reusable agent capabilities.",
)

registry = CapabilityRegistry()
http = HttpExtractor()
browser = BrowserExecutor()
router = CapabilityRouter(registry=registry, http=http, browser=browser)
verifier = CapabilityVerifier(registry, browser)
doctor = ScraperDoctor(registry)


class FetchBody(BaseModel):
    url: HttpUrl


class ExecuteBody(BaseModel):
    url: HttpUrl
    goal: str
    inputs: dict = Field(default_factory=dict)
    interactive: bool = False


class VerifyBody(BaseModel):
    inputs: dict = Field(default_factory=dict)


@app.get("/health")
async def health():
    return {"ok": True, "service": "scraper", "version": "0.1.0"}


@app.get("/v1/doctor")
async def doctor_report(domain: str | None = None):
    return doctor.inspect(domain=domain)


@app.post("/v1/fetch")
async def fetch(body: FetchBody):
    result = await router.fetch(str(body.url))
    if not result.ok:
        raise HTTPException(status_code=502, detail=result.error)
    return result


@app.post("/v1/native-tools/discover")
async def native_tools_discover(body: FetchBody):
    try:
        snapshot = await http.fetch(str(body.url))
    except Exception as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    return discover_native_tools(snapshot)


@app.post("/v1/execute")
async def execute(body: ExecuteBody):
    return await router.execute(
        WebRequest(
            url=body.url,
            goal=body.goal,
            inputs=body.inputs,
            interactive=body.interactive,
        )
    )


@app.post("/v1/leads/audit")
async def lead_audit(body: FetchBody):
    try:
        snapshot = await http.fetch(str(body.url))
    except Exception as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    return audit_lead(snapshot)


@app.get("/v1/capabilities")
async def list_capabilities(domain: str | None = None, trusted_only: bool = False):
    return registry.list(domain=domain, trusted_only=trusted_only)


@app.post("/v1/capabilities/{capability_id}/run")
async def run_capability(capability_id: str, body: VerifyBody):
    result = await router.run_capability(capability_id, body.inputs)
    if not result.ok:
        raise HTTPException(status_code=409, detail=result.error)
    return result


@app.post("/v1/capabilities/{capability_id}/verify")
async def verify_capability(capability_id: str, body: VerifyBody):
    capability = registry.get(capability_id)
    if not capability:
        raise HTTPException(status_code=404, detail="capability not found")
    return await verifier.verify(capability, body.inputs)


def main() -> None:
    import uvicorn

    uvicorn.run("scraper.api:app", host="127.0.0.1", port=8787, reload=False)
