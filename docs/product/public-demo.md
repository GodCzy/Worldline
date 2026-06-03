# Worldline Public Demo

Updated: 2026-06-03

## Demo Positioning

Worldline is demoed as an Evidence-backed LLM Wiki + Temporal Knowledge Graph OS, not as a generic RAG chat page.

The first visible product surface is the Worldline workbench:

- A dark luminous worldline stage for branch inspection.
- Evidence, Wiki, graph, and temporal references visible beside each branch.
- Agent handoff context preserved as structured data.
- Quality gates shown as release and trust signals.

## Demo Entry Points

- Frontend hub: `/worldline`
- Frontend workbench: `/worldline/phase5-preview`
- Graph handoff: `/graph?theme=phase5-preview&module=phase5-preview&scene=graph_timeline&version=worldline-phase5-preview&graph=phase5-graph-focus`
- Docs: `docs/index.md`
- Release gate script: `scripts/worldline_phase6_7_release_gate.py`

## Demo Narrative

1. Start at `/worldline` and show that the product opens as a workbench, not a landing page.
2. Open the Phase 5 preview module and select a branch.
3. Point to the evidence rail, Wiki refs, entity refs, timeline refs, and quality panel.
4. Use Graph handoff to show graph-focused context.
5. Explain that RAG is auxiliary retrieval; the durable product assets are EvidenceAnchor, WikiPage, KnowledgeEntity, KnowledgeRelationship, TemporalFact, workflow plans, audit logs, and QualityGateRun.
6. Show the Phase 6/7 release gate report and screenshots as verification evidence.

## Required Evidence Before Sharing

- `python scripts/worldline_phase6_7_release_gate.py` returns `status=passed`.
- Focused pytest passes for knowledge models, evidence service, Phase 5-7 services, and Phase 6/7 release gate checks.
- Frontend build passes.
- Docs build passes.
- Docker compose config passes.
- Screenshot QA covers `/worldline`, `/worldline/phase5-preview`, and `/graph` at `1920x1080`, `1440x900`, and `390x844`.

## Non-Goals

- Do not present Worldline as a finished hosted SaaS.
- Do not claim live external MCP integrations are enabled by default.
- Do not expose secrets, database direct-write MCP, unrestricted filesystem MCP, or cloud write tools.
- Do not replace the evidence-backed workflow with a pure chat demonstration.
