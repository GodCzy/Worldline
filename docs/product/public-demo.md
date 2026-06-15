# Worldline Public Demo

Updated: 2026-06-15

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
- P5 read-only branch share: `/worldline/share/demo-branch-evidence`
- P5 safe dataset API: `/api/worldline/public-demo/dataset`
- P5 JSON evidence bundle: `/api/worldline/public-demo/evidence-bundle?share_id=demo-branch-evidence&format=json`
- P5 Markdown evidence bundle: `/api/worldline/public-demo/evidence-bundle?share_id=demo-branch-evidence&format=markdown`
- Agent redirect check: `/agent` while unauthenticated
- Docs: `docs/index.md`
- Release gate script: `scripts/worldline_phase6_7_release_gate.py`

## Demo Narrative

1. Start at `/` and show that the product opens as a usable console, not a landing page.
2. Show the embedded login panel and explain that Agent/admin surfaces require authenticated access.
3. Open `/themes` and show the empty custom module entry.
4. Open `/worldline` and show the empty real-module state.
5. Explain that RAG is auxiliary retrieval; durable assets are EvidenceAnchor, WikiPage, KnowledgeEntity, KnowledgeRelationship, TemporalFact, workflow plans, audit logs, and QualityGateRun.
6. Open `/worldline/share/demo-branch-evidence` and show a read-only branch with evidence, Wiki, graph, timeline, quality gates, and replay steps.
7. Export the JSON or Markdown evidence bundle and compare the checksum before sharing.
8. Show the release gate report and screenshots as verification evidence.

## P5 Public Demo

The P5 public demo is intentionally deterministic and read-only. `WorldlinePublicDemoService` owns the safe demo dataset, branch share payload, and evidence bundle export. The service does not read live KB data, does not accept write payloads, and does not require external accounts.

Public viewers can:

- inspect the curated branch at `/worldline/share/demo-branch-evidence`;
- review source, evidence, Wiki, graph, timeline, and quality-gate references;
- download a JSON evidence bundle;
- download a Markdown evidence bundle;
- replay the documented inspection steps locally.

Public viewers cannot:

- mutate KBs, runs, branches, quality gates, MCP settings, or operational actions;
- access admin dashboards or live run ledgers;
- use GitHub, Firecrawl, Tavily, or other external connectors through this route.

## Required Evidence Before Sharing

- `python scripts/worldline_phase6_7_release_gate.py` returns `status=passed`.
- Focused pytest passes for knowledge models, evidence service, live Worldline services, and release gate checks.
- Frontend build passes.
- Docs build passes.
- Docker compose config passes.
- Screenshot QA covers `/`, `/themes`, `/worldline`, unauthenticated `/agent` redirect, and authenticated Joy superadmin sidebar at `1920x1080`, `1440x900`, and `390x844`.
- P5 screenshot QA covers `/worldline/share/demo-branch-evidence` at desktop and `390x844`.
- Public demo secret hygiene scan reports zero token-like, password-like, or personal credential findings for the P5 public-demo surface.
- Evidence bundle export includes branch, evidence, Wiki, graph, timeline, gate, replay, rollback, and checksum sections.

## Rollback

If the public demo route must be removed:

1. Remove `server.routers.worldline_public_demo_router` from `server/routers/__init__.py`.
2. Remove `^/api/worldline/public-demo(?:/.*)?$` from `server/utils/auth_middleware.py`.
3. Remove `worldlinePublicDemoApi` from `web/src/apis/worldline_api.js`.
4. Remove `/worldline/share/:shareId` from `web/src/router/index.js`.
5. Remove `web/src/views/worldline/WorldlinePublicShareView.vue`.
6. Re-run focused backend tests, frontend build, docs build, and release gate.

## Non-Goals

- Do not present Worldline as a finished hosted SaaS.
- Do not claim live external MCP integrations are enabled by default.
- Do not expose secrets, database direct-write MCP, unrestricted filesystem MCP, or cloud write tools.
- Do not replace the evidence-backed workflow with a pure chat demonstration.
- Do not treat GitHub PR/issue integration or optional ingestion tools as enabled until Joy authorizes connector scope and secret handling.
