# Scraper — Verified Project State

Last updated: 2026-08-21 (America/Toronto)

## Current verified commit

`4190f033f94a0c530624bc7facd9a652f0b54c29`

This commit merged PR #2 after its independent GitHub Actions gate passed.

## Verification evidence

PR #2 CI completed successfully on Python 3.11:

- package installation: PASS
- Ruff lint: PASS
- pytest: PASS
- tests: **7 passed in 0.20s**

The test suite currently verifies:

- localhost/private-target protection at the URL-policy boundary;
- compiled capabilities begin quarantined;
- trust promotion requires repeated observed execution successes;
- lead scoring retains evidence and ranks observable voice-AI signals;
- declarative WebMCP forms are discovered and converted into structured input schemas;
- imperative `document.modelContext.registerTool(...)` presence is detectable;
- doctor health reports degraded capability state;
- doctor reports an empty/unconfigured scope accurately.

## Implemented now

### Web execution primitives

- public HTTP/DOM fetcher using `httpx` + BeautifulSoup;
- Playwright replay executor for constrained compiled capabilities;
- redirect/target validation through the URL security policy;
- source evidence with observation time and content hash.

### Capability compiler

- typed capability model;
- safe declarative browser-step DSL;
- filesystem-backed capability registry for the bootstrap phase;
- trust states: `quarantined`, `candidate`, `trusted`, `degraded`, `disabled`;
- empirical verifier that promotes only after successful replays;
- deterministic router that prefers trusted compiled behavior before expensive fallbacks.

### Native web-agent affordances

- declarative WebMCP form discovery (`toolname`, `tooldescription`, `toolautosubmit`);
- input-schema synthesis from semantic form controls;
- `toolparamdescription`, required fields, select enums, and numeric bounds;
- detection of imperative `document.modelContext.registerTool(...)` usage.

### Prospect intelligence bootstrap

- evidence-backed website audit;
- phone-dependent conversion signal;
- after-hours/emergency signal;
- missing obvious booking/chat/form signals;
- basic mobile/SEO foundation signals;
- separate scores for `voice_ai`, `website`, and `automation`;
- recommended offer + `why_now` explanation.

### Interfaces

REST:

- `/health`
- `/v1/doctor`
- `/v1/fetch`
- `/v1/native-tools/discover`
- `/v1/execute`
- `/v1/leads/audit`
- `/v1/capabilities`
- capability run/verify endpoints

MCP:

- `web_fetch`
- `webmcp_discover`
- `lead_audit`
- `capability_discover`
- `capability_run`
- `capability_verify`
- `doctor`

### Architecture / provenance

- 117-repository harvest ledger;
- licensing boundaries and clean-room reuse policy;
- capability graph design;
- security model;
- provider/fallback strategy;
- staged M0–M4 roadmap.

## Explicitly not implemented yet

These are architectural commitments, not completed functionality:

### M1 — live discovery compiler

- autonomous DOM/accessibility observation loop;
- LLM planner/provider adapter;
- browser action selection from a natural-language goal;
- successful live trace normalization;
- automatic trace -> candidate capability compilation;
- human review/approval command;
- vision fallback when semantic structure is insufficient.

### M2 — durability and repair

- Postgres system of record;
- persistent run/evidence/lead tables;
- encrypted authenticated browser profile/session vault;
- scheduled capability re-verification;
- automatic repair queue for site drift;
- screenshot/network regression checkpoints;
- per-domain circuit breaker and runtime cost telemetry.

### M3 — full prospect engine

- market/geography candidate discovery;
- Google Maps/search/directory source adapters;
- multi-source company/entity resolution;
- public review/careers/social signal collection;
- cross-source corroboration;
- lead pipeline and CRM state;
- decision-maker/contact enrichment where permitted;
- outcome labels: contacted/replied/meeting/proposal/won/lost;
- learning which observable signals actually predict sales.

### M4 — capability network

- semantic capability search;
- derived capability graph over canonical relational state;
- cross-site capability transfer/generalization;
- cost/latency/reliability-aware routing;
- multi-tenant authorization and audit controls.

## Next engineering milestone

**M1: live discovery compiler.**

Acceptance test:

> Given an unfamiliar public website and a natural-language read/interact goal, Scraper can observe the live page, discover a successful authorized workflow, prove the result with an external assertion, emit a safe declarative candidate capability, and successfully replay that candidate without asking the planner to rediscover the workflow.

Until that acceptance test passes, Scraper should not be described as a complete universal website-to-API system.
