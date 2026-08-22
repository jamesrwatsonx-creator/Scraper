# Scraper

**Scraper is a capability compiler for the web.**

It turns websites that were built for humans into verified, reusable tools for AI agents — even when the site has no official API or MCP server.

Scraper is not intended to be another generic scraping API. The core loop is:

```text
intent
  -> discover the best execution path
  -> use native API/MCP/WebMCP when available
  -> replay a verified compiled capability when available
  -> use direct HTTP/DOM extraction for simple public reads
  -> use a live browser agent only when necessary
  -> capture evidence + execution trace
  -> verify the result
  -> compile successful behavior into a declarative skill
  -> re-use that capability through MCP/API/CLI
```

The result is a web execution layer that gets cheaper and more reliable as it learns.

## Why this exists

Most integrations assume the target service has an API. The web already contains far more functionality than official APIs expose. Search boxes, forms, filters, booking flows, dashboards, public directories and logged-in user interfaces are latent machine-callable functions.

Scraper converts those interfaces into a **capability graph**.

A capability is not just a selector script. It records:

- intent and tool description
- domain and route constraints
- typed input/output schemas
- declarative execution steps
- required permissions
- provenance and source URLs
- verification checkpoints
- successful and failed runs
- last verified time
- confidence and trust state
- recovery/fallback strategy

## Execution hierarchy

Scraper always prefers the most deterministic and least expensive path:

1. **Official API / MCP** — use the supported machine interface when it exists.
2. **Native WebMCP** — use tool definitions exposed directly by the page when available.
3. **Verified compiled capability** — replay a previously proven workflow.
4. **Direct web extraction** — HTTP + DOM extraction for public, read-only content.
5. **Live browser execution** — Playwright/CDP for dynamic or interactive workflows.
6. **Optional external provider fallback** — Firecrawl, Apify, Browserbase, proxy infrastructure, etc., behind adapters rather than hard dependencies.

The caller should not have to know which path was used.

## The differentiator: learn once, replay safely

A live browser agent can discover how to complete a task, but rediscovering the same workflow every run is expensive and brittle. Scraper promotes successful traces into a constrained declarative DSL.

```text
live exploration
     |
     v
quarantined capability
     |
     | security scan + schema validation
     v
candidate capability
     |
     | repeated successful verification
     v
trusted capability
     |
     +----> MCP tool
     +----> REST endpoint
     +----> CLI command
```

Generated capabilities never get arbitrary shell or Python execution. Learned behavior is represented as an allow-listed set of browser operations and assertions.

## First application: prospect intelligence

The first product built on Scraper is a sales-intelligence engine for finding businesses likely to need AI receptionists, websites and automation.

```text
market + geography + ICP
        -> discover candidate businesses
        -> inspect public business surfaces
        -> collect evidence
        -> detect buying/problem signals
        -> cross-check important claims
        -> score opportunity
        -> explain why the lead matters now
        -> retain source lineage + verification date
```

The valuable record is not `business exists`. It is:

```text
business
  x problem
  x evidence
  x confidence
  x timing signal
  x recommended offer
```

## Initial MCP surface

The intended tool surface is deliberately small:

- `web_fetch(url)` — retrieve clean public page content with provenance.
- `web_execute(url, goal, inputs)` — execute an interactive browser task.
- `capability_discover(domain, goal)` — find native or compiled capabilities.
- `capability_run(capability_id, inputs)` — execute a verified capability.
- `capability_verify(capability_id)` — replay checkpoints and update trust.
- `lead_audit(url)` — inspect a business website and return evidence-backed opportunity signals.

## Safety and operating rules

Scraper is designed for authorized and public web use.

- No CAPTCHA bypass capability.
- No arbitrary code inside learned site skills.
- Block localhost/private-network targets by default to prevent SSRF.
- Explicit domain/permission declarations for capabilities.
- Rate limits and per-domain health/circuit breakers.
- Preserve provenance for extracted facts.
- Do not label a lead signal as verified without evidence.
- Authenticated workflows use user-authorized sessions; credentials are never embedded in skills.
- External providers are optional fallbacks, not architectural dependencies.

## Repository harvest

This architecture was derived after auditing the GitHub repositories available to this account. The connected GitHub search currently exposes **117 repositories**, not the older remembered count of ~80.

The highest-signal sources include:

- `browser-harness` — direct CDP control and learned domain skills
- `crawl4ai` — LLM-ready crawling, sessions and structured extraction
- `firecrawl` — search/scrape/interact/agent endpoint design
- `apify-mcp-server` — dynamic MCP tool discovery
- `Agent-Reach` — capability routing, fallbacks and doctor diagnostics
- `webmcp` — browser-native tool exposure model
- `argent` — record/replay, visual regression and network inspection
- `codebase-memory-mcp` — graph indexing and incremental change detection
- `mem0` — durable memory and multi-signal retrieval patterns
- `pgGraph` / `pgContext` — derived graph/search indexes over canonical relational data
- `SkillSpector` — skill/MCP security scanning patterns
- `promptfoo` — eval/red-team gates
- `gauntlet-loop` / `superpowers` — evidence-driven verification and development gates
- `last30days-skill` — multi-source routing, scoring, diagnostics and freshness
- `marketingskills` / `agency-agents` / `geo-seo-claude` — prospect qualification and audit logic
- `n8n` / `ruflo` / `uAgents` — scheduled/event-driven orchestration patterns
- `AIOS` — operator-facing browser mission/evidence history

See `docs/REPO_HARVEST.md` and `docs/ARCHITECTURE.md` for the extraction ledger and design decisions.

## Status

This repository is being initialized as a clean implementation rather than merging forked projects wholesale. That keeps the architecture coherent and avoids accidentally importing incompatible licenses or enormous dependency trees.

The first milestone is a local-first Python service with:

- typed capability model
- safe declarative skill registry
- public HTTP extractor
- Playwright browser executor
- capability router/compiler/verifier
- evidence/provenance model
- lead opportunity scorer
- REST + MCP adapters
- tests for routing, security and trust promotion

## License

No license has been selected for Scraper yet. Until one is chosen, do not assume third parties have permission to redistribute this repository.
