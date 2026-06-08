# Worldline Public Demo

Updated: 2026-06-03

## Demo Positioning

Worldline is demoed as an Evidence-backed LLM Wiki + Temporal Knowledge Graph OS, not as a generic RAG chat page.

The first visible product surface is the Worldline console:

- A dark cyan/gold visual system across home, sidebar, module registry, and Worldline hub.
- An embedded login panel for Agent and admin surfaces.
- A deliberately empty module registry with a `+` entry for custom knowledge modules.
- Evidence, Wiki, graph, temporal references, Agent handoff, and quality gates as the next live-module path.

## Demo Entry Points

- Home console: `/`
- Module registry: `/themes`
- Worldline hub: `/worldline`
- Agent redirect check: `/agent` while unauthenticated
- Docs: `docs/index.md`
- Release gate script: `scripts/worldline_phase6_7_release_gate.py`

## Demo Narrative

1. Start at `/` and show that the product opens as a usable console, not a landing page.
2. Show the embedded login panel and explain that Agent/admin surfaces require authenticated access.
3. Open `/themes` and show the empty custom module entry.
4. Open `/worldline` and show the empty real-module state.
5. Explain that RAG is auxiliary retrieval; durable assets are EvidenceAnchor, WikiPage, KnowledgeEntity, KnowledgeRelationship, TemporalFact, workflow plans, audit logs, and QualityGateRun.
6. Show the Phase 6/7 release gate report and screenshots as verification evidence.

## Required Evidence Before Sharing

- `python scripts/worldline_phase6_7_release_gate.py` returns `status=passed`.
- Focused pytest passes for knowledge models, evidence service, live Worldline services, and release gate checks.
- Frontend build passes.
- Docs build passes.
- Docker compose config passes.
- Screenshot QA covers `/`, `/themes`, `/worldline`, unauthenticated `/agent` redirect, and authenticated Joy superadmin sidebar at `1920x1080`, `1440x900`, and `390x844`.

## Non-Goals

- Do not present Worldline as a finished hosted SaaS.
- Do not claim live external MCP integrations are enabled by default.
- Do not expose secrets, database direct-write MCP, unrestricted filesystem MCP, or cloud write tools.
- Do not replace the evidence-backed workflow with a pure chat demonstration.
