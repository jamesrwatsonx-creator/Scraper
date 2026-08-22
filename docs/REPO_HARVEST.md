# Repository Harvest Ledger

## Scope

The connected GitHub account was inventoried using repository search on 2026-08-21. Search returned two populated pages and an empty third page: **117 repositories total**. This supersedes the older remembered count of roughly 80.

Every repository was evaluated for relevance to Scraper at the repository/capability level. High-signal repositories were then inspected more deeply through their current README/skill documentation. This document intentionally distinguishes **reuse**, **adapt**, **integration**, and **no direct use** so Scraper does not become a pile of forks.

The governing question was:

> Does this repository contain a primitive, pattern, workflow, evaluation method, distribution mechanism, data model, or product capability that materially improves a system that turns websites into reliable agent-callable tools and uses that system for prospect intelligence?

## Tier A — direct architectural harvest

These are the repos that materially shape Scraper's core.

| Repository | What Scraper should harvest | Treatment |
| --- | --- | --- |
| `browser-harness` | Thin CDP browser control; successful per-domain workflows becoming reusable skills; self-improving browser helpers | Reimplement core concept with declarative skill output |
| `crawl4ai` | Async crawling, sessions, cache, structured extraction, JS rendering, remote/user browser, deployment API | Reuse compatible libraries/patterns; avoid swallowing full project |
| `firecrawl` | Clean search/scrape/interact/agent separation; structured output; browser actions; provider abstraction | Adapter + endpoint-design reference |
| `apify-mcp-server` | Dynamic discovery of capabilities and schemas instead of permanently loading thousands of tools | Reimplement dynamic MCP capability discovery |
| `Agent-Reach` | Ordered preferred/fallback routes, source health, `doctor` diagnostics, local browser-session reuse | Core router/health architecture |
| `webmcp` | Treat page functionality as tools; prefer native browser-exposed tools over simulated clicks | Native route; synthesize equivalent tool when absent |
| `argent` | Record/replay, screenshot regression, DOM/network inspection, deterministic replay | Add checkpoints and regression verification |
| `codebase-memory-mcp` | Persistent knowledge graph, incremental change detection, cross-entity graph queries, agent as intelligence layer | Adapt into Website Capability Graph |
| `mem0` | Durable structured memory, entity linking, hybrid retrieval, temporal facts | Memory design; do not stuff raw traces into prompts |
| `pgGraph` | Keep relational tables canonical and graph indexes derived/rebuildable; bounded traversal | Optional derived capability graph over Postgres |
| `pgContext` | Hybrid dense + lexical retrieval next to canonical relational data; exact recheck | Optional capability/evidence retrieval layer |
| `SkillSpector` | Skill/MCP poisoning, excessive agency, exfiltration, SSRF-adjacent and description/behavior security checks | Security gate for learned/imported capabilities |
| `promptfoo` | Automated evals, red-team suites, CI gates, model/provider comparison | Verification/eval harness integration |
| `last30days-skill` | Parallel source routing, backend failover, scoring, freshness windows, doctor command, hiring signals, watchlist deltas | Prospect research/source-router patterns |
| `marketingskills` | ICP definition, discovery→qualification→scoring→lead-sheet flow, confidence levels, source lineage, compliance posture | Core prospect intelligence contract |
| `agency-agents` | Signal-based outbound strategy, account/pipeline roles and specialized sales-agent decomposition | Lead diagnosis and sales workflows |
| `geo-seo-claude` | Website audit decomposition, parallel specialized audits, CRM-lite prospects, reports, delta comparison | Website/SEO/GEO opportunity scoring |
| `n8n` | Scheduling, event workflows, connector ecosystem | External optional workflow engine; do not absorb fair-code core |
| `ruflo` | Scheduled workers, workflow orchestration, memory, learning loop, observability and security patterns | Optional orchestration layer / architecture reference |
| `uAgents` | Event/schedule driven agents; explicit agent identities | Lightweight event-worker concepts |
| `AIOS` | Browser mission history, action logs, screenshots, extracted results, local-first operator console | Operator/evidence UX patterns |
| `gauntlet-loop` | External quality bar, independent critic, verify rather than self-grade | Capability verification philosophy |
| `superpowers` | Systematic planning/TDD/review and verification-before-completion | Engineering workflow for Scraper itself |
| `github-mcp-server` | Production MCP server organization, auth/tool surface patterns | MCP implementation reference |
| `skills` | Cross-agent skill packaging conventions | Capability/skill distribution compatibility |
| `agent-skills` | Agent skill structure and installation conventions | Skill interoperability reference |
| `yt-dlp` | Large plugin/extractor ecosystem and site-specific adapter dispatch | Extractor registry / plugin lifecycle pattern |
| `goclaw` | Agent pipeline, permission layers, encrypted keys, observability, event workers, retries | Conceptual patterns only; licensing blocks commercial code reuse |
| `OpenViking` | Hierarchical context, observable retrieval trajectory, resources/skills/memory namespace | Conceptual memory pattern only; AGPL boundary |

### Tier A synthesis

The core product assembled from these ideas is:

```text
Capability Router
  + Native MCP/WebMCP detection
  + HTTP/DOM extractor
  + Browser planner
  + Safe capability compiler
  + Trusted skill registry
  + Replay verifier/regression monitor
  + Evidence/provenance ledger
  + Website capability graph
  + MCP/REST/CLI adapters
  + Doctor/health/circuit breakers
  + Prospect intelligence vertical
```

## Tier B — useful adjacent components or later integrations

These repos contain useful patterns, distribution surfaces, secondary product capabilities or future adapters, but they should not shape the V0 core.

| Repository | Potential use |
| --- | --- |
| `Flowise` | Visual agent/workflow composition; possible integration surface |
| `open-webui` | Self-hosted operator/chat UI patterns |
| `lobehub` | Multi-provider chat/tool UX and plugin distribution patterns |
| `graphrag` | Graph-assisted evidence synthesis once enough relationship data exists |
| `graphify` | Graph extraction/visualization concepts |
| `open-notebook` | Research workspace / source organization patterns |
| `orca` | Agent/runtime ideas; defer until a concrete capability beats current core |
| `social-media-skills` | Social research and performance scoring for prospect/brand intelligence |
| `pm-skills` | Product-management skill composition and reusable procedures |
| `skills-finds` | Skill discovery/distribution ideas |
| `skills-learning` | Learning-oriented skill patterns |
| `headroom` | Context/token optimization patterns if browser evidence becomes expensive |
| `launch-your-agent` | Packaging/deployment convenience for agent products |
| `loop-engineering` | Iterative engineering loop and verification patterns |
| `loop-engineer-template` | Repo/session-state conventions for autonomous development |
| `Claude-of-Duty` | Builder/critic loop patterns |
| `james-watson-gauntlet-loop` | Localized quality-loop patterns |
| `AGI-1.0` | Experimental agent-loop ideas; only harvest when verified against Scraper needs |
| `dcode-agent-kit` | Agent scaffolding patterns |
| `free-claude-code` | Provider/runtime flexibility concepts |
| `andrej-karpathy-skills` | Skill design/agent coding heuristics |
| `slack-mcp-server` | Second production MCP-server reference; future notifications/collaboration |
| `GHL` | Future CRM/voice-agent handoff target; currently not a code source |
| `odoo` | Mature CRM/pipeline/entity-model reference; too large to embed |
| `watson-ai-site` | Product/offer context for the initial prospecting vertical |
| `watson-app-foundation` | Product-definition and acceptance-test workflow |
| `watson-mobile-foundation` | Mobile engineering contract if Scraper gets a mobile operator app |
| `Watson-Design-Foundation` | Design system process for a later dashboard |
| `base44-to-supabase-sdk` | Migration/data-layer bridge patterns, not core runtime |
| `vibe-coding-with-base44` | Builder workflow reference only |
| `grok-build` | Coding/build orchestration ideas |
| `makerskills` | General creation skills; possible skill-format examples |
| `useful-ai-prompts` | Prompt reference corpus; do not make prompt collections a runtime dependency |
| `system_prompts_leaks` | Adversarial/security research input for prompt-injection tests |
| `humanizer` | Downstream outreach copy post-processing, not prospect discovery |
| `taste-skill` | Future dashboard/design critic |
| `impeccable` | Future UI quality reference |
| `ui-ux-pro-max-skill` | Future operator-console design reference |
| `diagram-design` | Architecture/flow visualization generation |
| `vibefeed` | Feed/stream product ideas if monitoring becomes a UI surface |
| `Crowned` | No core extraction primitive; potential content/research consumer of Scraper |
| `MoneyPrinterTurbo` | Generate short visual explainers/reports from harvested intelligence |
| `video-use` | Video workflow automation as a downstream capability |
| `skills-video` | Video-specific skills for downstream content generation |
| `OpenMontage` | Video assembly downstream of research/results |
| `OpenCut` | Editing/export layer for generated sales/research media |
| `cli-printing-press` | CLI content-production orchestration patterns |
| `printing-press-library` | Reusable media/content templates, downstream only |
| `voicebox` | Voice generation/demos for outreach or product demos |
| `Real-Time-Voice-Cloning` | Voice demo experimentation; not part of web execution core |

## Tier C — audited, no direct V0 harvest

These repositories were included in the account inventory but do not add a strong primitive to the current web-capability/prospect-intelligence problem. They stay out of the dependency graph unless a future requirement creates a specific reason to use them.

- `codegraph`
- `TradingAgents`
- `Fooocus`
- `ComfyUI`
- `InvokeAI`
- `Deep-Live-Cam`
- `HunyuanVideo`
- `Wan2.1`
- `ml-agents`
- `opencv`
- `mediapipe`
- `ultralytics`
- `cvat`
- `ncnn`
- `LocalAI`
- `Swift-Agent-Skills`
- `claude-android-skill`
- `babysitter`
- `Sana`
- `dyad`
- `hyperframes`
- `hyperframes-student-kit`
- `skills-fable`
- `skills-claude-design`
- `Finn-loop`
- `awesome-llm-apps`
- `caveman`
- `gsap-skills`
- `RuView`
- `Game-Demo`
- `yfinance`
- `Loop-Trading-App`
- `Openaiplugins`
- `Scraper` (target repository; not an upstream source)
- `PhotoML`
- `flutter`
- `lottie-android`
- `prompts.chat`

## Count reconciliation

- Tier A: 29 repositories
- Tier B: 50 repositories
- Tier C: 38 repositories
- **Total: 117 repositories**

No repository is intentionally omitted from the reconciled account inventory.

## What we are deliberately *not* doing

### 1. No mega-merge

Pulling entire forks into one repository would create conflicting runtimes, licensing obligations, huge attack surface and impossible maintenance. We harvest primitives and keep providers behind interfaces.

### 2. No vendor dependency at the center

Firecrawl/Apify/Browserbase-style services can improve edge-case reliability, but the system's identity, data and learned capabilities remain ours.

### 3. No arbitrary self-writing production skills

Browser exploration may use model reasoning, but promoted capabilities are declarative and constrained. This retains the learning advantage of `browser-harness` while reducing supply-chain and self-modification risk.

### 4. No graph/vector database as a second truth store

Postgres is canonical. Graph/vector/search structures are derived and rebuildable.

### 5. No lead list without evidence

The prospecting system stores claim lineage, observation date and confidence. A “Hot” lead should be explainable and auditable.

## Licensing notes discovered during harvest

The inventory mixes permissive, copyleft, non-commercial, fair-code and mixed/proprietary components. Important examples:

- `OpenViking`: AGPLv3 — ideas are usable; copied/network-served derivative code has material obligations.
- `goclaw`: repository advertises CC BY-NC 4.0 — conceptual reference only for a commercial system.
- `n8n`: Sustainable Use/fair-code — use as an external integration where appropriate.
- `argent`: Apache-licensed source plus explicitly proprietary binary components — proprietary pieces stay out.
- `promptfoo`, `superpowers`, `social-media-skills`, `geo-seo-claude`, `codebase-memory-mcp`: permissive according to their current repository documentation, but notices still need to be preserved if source is copied.

Default implementation policy: **clean-room reimplementation of the useful primitive unless selective code reuse is clearly simpler and license-compatible.**

## The parts that create our moat

None of the upstream repositories owns the combined dataset Scraper can create:

```text
site
 + goal
 + successful capability
 + failure modes
 + change history
 + evidence
 + cost/latency
 + reliability
 + business entity
 + problem signal
 + offer
 + sales outcome
```

That joined history is the compounding asset. The browser/extraction technology is replaceable; the verified capability graph and outcome-labeled commercial intelligence are not.
