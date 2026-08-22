# Scraper Architecture

## 1. Product definition

Scraper is a **web capability compiler**.

The goal is not to maximize pages scraped. The goal is to make the useful behavior of the web callable by agents with the reliability profile of an API.

A normal browser agent pays the reasoning and browser-navigation cost on every run. Scraper separates **discovery** from **execution**:

1. discover how a task works on a site;
2. record the successful trace and evidence;
3. convert the trace into a constrained declarative capability;
4. quarantine and security-check it;
5. replay it against explicit assertions;
6. promote it only after observed successes;
7. expose the trusted capability through MCP/API/CLI;
8. monitor for drift and automatically degrade it when verification fails;
9. send degraded capabilities back through discovery/repair.

This is closer to a compiler + runtime than to a conventional scraper.

## 2. Architectural principles harvested from the repository fleet

### Browser Harness -> learn domain behavior

`browser-harness` demonstrates the leverage of a thin CDP connection plus reusable per-domain skills learned from successful browser work. Scraper keeps the learning concept but changes the artifact: production capabilities are declarative, reviewable and non-executable rather than arbitrary generated helper code.

### WebMCP -> prefer native tools, synthesize the missing ones

`webmcp` treats a page as capable of exposing structured tools directly from its client-side functionality. Scraper should detect native WebMCP/MCP first. When absent, its browser discovery layer should infer an equivalent capability from the actual interface.

### Crawl4AI / Firecrawl -> separate extraction from browsing

Simple read operations should not pay interactive-browser cost. HTTP/DOM extraction is the default for public pages; browser execution is escalation, not the first hammer.

### Agent-Reach / last30days -> capability routing + doctor

Every capability/source needs an ordered route list and observable health. A `doctor` subsystem should answer:

- which route is currently preferred;
- whether auth/session state is healthy;
- when the last successful run occurred;
- why a route is degraded;
- which fallback will be tried next.

### Apify MCP -> dynamic tool discovery

The MCP surface should not contain thousands of permanently loaded site tools. Agents discover capabilities by intent/domain and load only the schema they need.

### Argent -> replay + checkpoints + regression evidence

A capability is more than selectors. It should eventually store:

- deterministic action trace;
- expected URL/state checkpoints;
- extraction schema;
- optional screenshot checkpoint;
- observed network contract where useful;
- retry/recovery boundaries.

### SkillSpector / Promptfoo -> generated tools are untrusted input

Learned capabilities must pass security and behavioral evals before promotion. Important threat classes include prompt/tool poisoning, hidden instructions, exfiltration, excessive agency, SSRF, unsafe outputs, memory poisoning and description/behavior mismatch.

### mem0 / OpenViking -> memory should be selective and inspectable

Do not dump every browser transcript into the model. Store structured observations and retrieve progressively. Scraper should remember successful actions, failures, site entities, auth requirements and verified outputs; raw traces are cold evidence, not prompt context.

### codebase-memory-mcp / pgGraph / pgContext -> canonical relational state + derived indexes

Postgres should remain authoritative. Capability graph, semantic retrieval and relationship indexes are derived/rebuildable acceleration structures. This prevents drift between a lead database, skill store, vector store and graph database.

### Gauntlet / Superpowers -> verification before completion

A browser agent saying “done” is not evidence. Success exits on an external assertion: schema validated, expected state observed, or downstream result confirmed.

### MarketingSkills / Agency Agents / GEO SEO -> diagnose, do not merely discover

For prospecting, a business record without a problem/timing signal is commodity data. The lead layer therefore stores observable evidence and produces a ranked problem/offer hypothesis rather than a list of names.

## 3. Runtime layers

```text
┌───────────────────────────────────────────────────────────────┐
│                       CALLER / AGENT                          │
│          MCP | REST | CLI | app | scheduled worker           │
└──────────────────────────────┬────────────────────────────────┘
                               │ intent
                               v
┌───────────────────────────────────────────────────────────────┐
│                    CAPABILITY ROUTER                          │
│ native API/MCP -> WebMCP -> trusted skill -> HTTP -> browser │
│                        -> provider fallback                   │
└──────────────────────────────┬────────────────────────────────┘
                               │
             ┌─────────────────┼─────────────────┐
             v                 v                 v
      ┌────────────┐    ┌──────────────┐   ┌───────────────┐
      │ HTTP/DOM   │    │ Skill Replay │   │ Live Browser  │
      │ extractor  │    │ Playwright   │   │ Planner       │
      └──────┬─────┘    └──────┬───────┘   └───────┬───────┘
             │                 │                   │
             └─────────────────┼───────────────────┘
                               v
┌───────────────────────────────────────────────────────────────┐
│                 EVIDENCE + VERIFICATION                       │
│ provenance | assertions | schema | trace | confidence | time │
└──────────────────────────────┬────────────────────────────────┘
                               v
┌───────────────────────────────────────────────────────────────┐
│                    CAPABILITY COMPILER                        │
│ live trace -> safe DSL -> quarantine -> candidate -> trusted │
└──────────────────────────────┬────────────────────────────────┘
                               v
┌───────────────────────────────────────────────────────────────┐
│                      SYSTEM OF RECORD                         │
│ Postgres: capabilities, runs, evidence, leads, sources, jobs │
│ derived: graph / semantic index / caches                     │
└───────────────────────────────────────────────────────────────┘
```

## 4. Capability trust state machine

```text
QUARANTINED
    |
    | static validation + first verified replay
    v
CANDIDATE
    |
    | N consecutive successful replays
    v
TRUSTED
    |
    | repeated failure / site drift
    v
DEGRADED
    |
    | repair + reverification
    +-----------------------> CANDIDATE
```

`DISABLED` is an operator terminal/administrative state.

Trust is empirical. A model cannot promote its own workflow by assertion.

## 5. Safe capability DSL

V0 operations are intentionally narrow:

- `navigate`
- `click`
- `fill`
- `wait_for`
- `extract_text`
- `extract_attr`
- `assert_text`
- `assert_url`

No shell, Python, arbitrary JavaScript, filesystem access, environment access or arbitrary network calls are allowed inside a learned capability.

Later additions must be capability-scoped and security-reviewed.

## 6. Discovery planner (next implementation layer)

The live planner is intentionally not hidden inside the router. It should be a separately testable component:

```text
Goal
 -> inspect page state
 -> prefer native page tools
 -> propose one action
 -> execute action
 -> observe state delta
 -> continue until ratification condition
 -> emit trace + structured result
 -> compiler attempts to generalize trace
```

The planner should consume DOM/accessibility structure before screenshots where possible, use vision when structure is insufficient, and never claim success without a ratification condition.

### Ratification conditions

Examples:

- required fields extracted and Pydantic/JSON Schema validates;
- URL transitioned to expected state;
- confirmation element appeared;
- expected record became visible;
- target page generated a stable identifier;
- read operation corroborated by an independent source where required.

## 7. Capability graph

Long term, Scraper should maintain entities such as:

```text
Site
Capability
Input
Output
UIState
Selector
Route
Evidence
Run
FailureMode
AuthProfile
Lead
Company
Signal
Offer
Source
```

Example edges:

```text
Site HAS_CAPABILITY Capability
Capability REQUIRES Input
Capability PRODUCES Output
Capability EXECUTED_AS Run
Run OBSERVED Evidence
Run FAILED_WITH FailureMode
Capability FALLS_BACK_TO Route
Lead HAS_SIGNAL Signal
Signal SUPPORTED_BY Evidence
Signal SUGGESTS Offer
```

This graph lets the system answer more valuable questions than “what can I scrape?”:

- Which capability is most reliable for this intent?
- What changed on this site since the workflow last worked?
- Which UI element causes most failures?
- Which prospect signals actually correlate with closed deals?
- Which capability learned on one site can transfer to another?

## 8. Prospect intelligence application

The prospect engine is the first vertical built on the general runtime.

### Discovery

Search a target market through permitted public surfaces and supported sources. Keep candidate discovery separate from qualification.

### Evidence collection

For each business inspect relevant public surfaces such as:

- company website;
- public contact/booking flows;
- careers page;
- public reviews where permitted;
- public business/social pages;
- technology/structured-data footprint;
- recent company/news signals;
- ad/landing-page surfaces where lawfully observable.

### Diagnosis

Store signals such as:

- phone-heavy conversion path;
- after-hours/emergency demand;
- no obvious online booking;
- no obvious chat/self-service;
- receptionist/customer-service hiring;
- recent expansion or new location;
- negative public feedback about response/callback where legitimately sourced;
- missing conversion form;
- weak mobile/SEO/structured-data foundations;
- high-intent acquisition language.

Every signal has provenance, observation time and confidence.

### Output

The system ranks:

```text
voice AI fit
website fit
automation fit
confidence
why now
strongest evidence
recommended opening angle
```

The scoring model should eventually learn from outcomes (`contacted`, `replied`, `meeting`, `proposal`, `won`, `lost`) so the proprietary asset becomes a mapping from observable web signals to buying probability.

## 9. Provider strategy

Do not build a proxy/CAPTCHA infrastructure company before it is necessary.

Core ownership:

- router
- compiler
- declarative skill format
- verification
- capability graph
- evidence model
- lead diagnosis
- outcome learning
- MCP/API surface

Replaceable adapters:

- search provider
- hosted browser provider
- proxy provider
- CAPTCHA/human-intervention provider where lawful and user-authorized
- LLM provider
- vector/graph acceleration layer

Hosted tools such as Firecrawl, Apify, Browserbase or similar services can be fallbacks without becoming architectural dependencies.

## 10. Security model

### Default deny

- only HTTP/HTTPS public targets;
- localhost/private/link-local/reserved network targets blocked;
- skills declare domains and permissions;
- no credentials stored in skill files;
- no arbitrary code in compiled capabilities;
- outputs schema-validated before downstream use;
- provenance retained with sensitive workflows;
- rate limits by domain/capability;
- explicit approval gates for consequential writes.

### Prompt injection

Content retrieved from websites is data, not authority. Page content cannot alter system policy, tool permissions or capability trust state.

### Authenticated sessions

Authenticated execution should use encrypted session/profile references. A skill may declare `requires_auth`, but never contain cookies, passwords or bearer tokens.

## 11. Observability

Every run should eventually record:

- trace ID
- capability/version
- provider/route
- target domain
- timings per step
- tokens/model cost for live planning
- browser/runtime cost
- evidence references
- assertions passed/failed
- retries/fallbacks
- final status
- error class
- site-change fingerprint

This enables cost-aware routing and automatic repair prioritization.

## 12. Licensing boundary

The repository fleet contains mixed licenses. Scraper should copy source only after confirming compatibility and attribution obligations.

Examples from the audit:

- permissive/MIT or Apache projects can be candidates for selective reuse subject to their notices;
- `OpenViking` is AGPLv3 — architecture ideas are useful, but copying code changes distribution obligations;
- `goclaw` advertises CC BY-NC for its repository — use conceptual patterns only for a commercial product;
- `n8n` uses its fair-code/Sustainable Use model — integrate as an external workflow engine rather than absorb it;
- `argent` has Apache-licensed source plus proprietary binaries — do not redistribute proprietary components.

The default rule is **reimplement the primitive cleanly** unless direct reuse is clearly justified.

## 13. Milestones

### M0 — repository foundation

- typed models
- URL security policy
- public HTTP extractor
- safe browser replay
- capability registry/compiler/verifier
- deterministic router
- lead website audit
- REST + MCP adapters

### M1 — live discovery compiler

- DOM/accessibility observation
- LLM planner adapter
- action/observation loop
- trace normalization
- auto-generated candidate capability
- evidence checkpoints
- human review command

### M2 — durability

- Postgres system of record
- run/evidence tables
- domain health + circuit breaker
- scheduled re-verification
- capability repair queue
- screenshot/network checkpoints
- native WebMCP detection

### M3 — prospect engine

- candidate discovery adapters
- multi-source corroboration
- company dedupe/entity resolution
- lead pipeline
- buyer-signal scoring
- outreach-ready evidence brief
- outcome feedback

### M4 — capability network

- semantic capability discovery
- site/capability graph
- cross-site skill transfer
- cost/latency reliability routing
- team/multi-tenant controls
- capability marketplace/registry only if it creates real distribution advantage
