from __future__ import annotations

import hashlib
from typing import Any
from urllib.parse import urljoin, urlparse

import httpx
from bs4 import BeautifulSoup

from .models import Capability, Evidence, ExecutionResult, PageSnapshot, TraceEvent
from .security import UrlPolicy, validate_step_type


class HttpExtractor:
    name = "http"

    def __init__(self, *, timeout: float = 20.0, url_policy: UrlPolicy | None = None):
        self.timeout = timeout
        self.url_policy = url_policy or UrlPolicy()

    async def fetch(self, url: str) -> PageSnapshot:
        self.url_policy.validate(url)
        headers = {"User-Agent": "ScraperCapabilityCompiler/0.1 (+public-web-research)"}
        async with httpx.AsyncClient(
            timeout=self.timeout,
            follow_redirects=True,
            headers=headers,
        ) as client:
            response = await client.get(url)
            response.raise_for_status()

        final_url = str(response.url)
        self.url_policy.validate(final_url)
        soup = BeautifulSoup(response.text, "html.parser")

        for tag in soup(["script", "style", "noscript", "template"]):
            tag.decompose()

        text = "\n".join(
            line.strip() for line in soup.get_text("\n").splitlines() if line.strip()
        )
        title = soup.title.get_text(strip=True) if soup.title else None
        links = []
        phone_links = []
        for anchor in soup.find_all("a", href=True):
            href = str(anchor.get("href"))
            if href.startswith("tel:"):
                phone_links.append(href)
            elif href.startswith(("http://", "https://", "/")):
                links.append(urljoin(final_url, href))

        digest = hashlib.sha256(response.content).hexdigest()
        evidence = Evidence(
            url=final_url,
            source_type="direct_http",
            excerpt=text[:500] or None,
            content_hash=digest,
        )
        viewport = soup.find("meta", attrs={"name": "viewport"}) is not None
        description = soup.find("meta", attrs={"name": "description"})

        return PageSnapshot(
            url=final_url,
            title=title,
            text=text,
            html=response.text,
            links=sorted(set(links)),
            phone_links=sorted(set(phone_links)),
            forms=len(soup.find_all("form")),
            metadata={
                "status_code": response.status_code,
                "content_type": response.headers.get("content-type"),
                "has_viewport_meta": viewport,
                "meta_description": description.get("content") if description else None,
            },
            evidence=[evidence],
        )


class BrowserExecutor:
    name = "browser"

    def __init__(self, *, headless: bool = True, url_policy: UrlPolicy | None = None):
        self.headless = headless
        self.url_policy = url_policy or UrlPolicy()

    @staticmethod
    def _render(value: str | None, inputs: dict[str, Any]) -> str:
        rendered = value or ""
        for key, replacement in inputs.items():
            rendered = rendered.replace("${" + key + "}", str(replacement))
        return rendered

    async def run(self, capability: Capability, inputs: dict[str, Any]) -> ExecutionResult:
        # Lazy import keeps public HTTP-only deployments lightweight.
        from playwright.async_api import async_playwright

        trace: list[TraceEvent] = []
        data: dict[str, Any] = {}
        evidence: list[Evidence] = []

        async with async_playwright() as playwright:
            browser = await playwright.chromium.launch(headless=self.headless)
            context = await browser.new_context()
            page = await context.new_page()
            try:
                for index, step in enumerate(capability.steps):
                    validate_step_type(step.type.value)
                    trace.append(
                        TraceEvent(
                            event="step_started",
                            detail={"index": index, "type": step.type.value},
                        )
                    )
                    value = self._render(step.value, inputs)
                    selector = self._render(step.selector, inputs) if step.selector else None

                    if step.type.value == "navigate":
                        target = value or f"https://{capability.domain}"
                        self.url_policy.validate(target)
                        await page.goto(
                            target,
                            wait_until="domcontentloaded",
                            timeout=step.timeout_ms,
                        )
                    elif step.type.value == "click":
                        await page.locator(selector).click(timeout=step.timeout_ms)
                    elif step.type.value == "fill":
                        await page.locator(selector).fill(value, timeout=step.timeout_ms)
                    elif step.type.value == "wait_for":
                        await page.locator(selector).wait_for(timeout=step.timeout_ms)
                    elif step.type.value == "extract_text":
                        output_key = step.output_key or f"step_{index}"
                        data[output_key] = await page.locator(selector).inner_text(
                            timeout=step.timeout_ms
                        )
                    elif step.type.value == "extract_attr":
                        if not step.attribute:
                            raise ValueError("extract_attr requires attribute")
                        output_key = step.output_key or f"step_{index}"
                        data[output_key] = await page.locator(selector).get_attribute(
                            step.attribute,
                            timeout=step.timeout_ms,
                        )
                    elif step.type.value == "assert_text":
                        actual = await page.locator(selector).inner_text(timeout=step.timeout_ms)
                        if value not in actual:
                            raise AssertionError(f"expected text not found at step {index}")
                    elif step.type.value == "assert_url":
                        if value not in page.url:
                            raise AssertionError(f"expected URL fragment not found at step {index}")

                    trace.append(
                        TraceEvent(
                            event="step_completed",
                            detail={"index": index, "type": step.type.value},
                        )
                    )

                final_url = page.url
                if final_url:
                    self.url_policy.validate(final_url)
                    evidence.append(
                        Evidence(
                            url=final_url,
                            source_type="browser_replay",
                            excerpt=(await page.title())[:300] or None,
                        )
                    )
                return ExecutionResult(
                    ok=True,
                    provider=self.name,
                    data=data,
                    evidence=evidence,
                    trace=trace,
                    capability_id=capability.id,
                )
            except Exception as exc:
                trace.append(TraceEvent(event="execution_failed", detail={"error": str(exc)}))
                return ExecutionResult(
                    ok=False,
                    provider=self.name,
                    data=data,
                    evidence=evidence,
                    trace=trace,
                    error=str(exc),
                    capability_id=capability.id,
                )
            finally:
                await context.close()
                await browser.close()


class ProviderFallback:
    """Small adapter seam for optional hosted providers.

    External services such as Firecrawl, Apify or Browserbase should implement
    this interface rather than leak vendor-specific contracts into the router.
    """

    name = "external"

    async def supports(self, url: str, goal: str) -> bool:
        return False

    async def execute(self, url: str, goal: str, inputs: dict[str, Any]) -> ExecutionResult:
        raise NotImplementedError


def domain_for(url: str) -> str:
    hostname = urlparse(url).hostname or ""
    return hostname.lower().removeprefix("www.")
