# Worldline Next Roadmap

更新时间：2026-06-08

## North Star

Worldline is an Evidence-backed LLM Wiki + Temporal Knowledge Graph OS.

The product compiles documents, web pages, code, evidence, Wiki pages, graph facts, temporal changes, Agent runs, MCP tools, and quality gates into a workbench that can be browsed, verified, reasoned over, and safely called by external Agents.

Worldline is not a generic RAG chat shell. RAG is a supporting recall layer for candidate evidence; the durable product assets are evidence anchors, Wiki pages, temporal graph facts, quality gate runs, worldline branches, and Agent run ledgers.

## Current Baseline

The project has a restarted fact base under `D:\dev\Worldline` with these current sources:

- `AGENTS.md`
- `README.md`
- `docs/index.md`
- `docs/product/worldline-project-book.md`
- `docs/architecture/`
- Current `.ai/tasks/<date-task>/` evidence directories

Recent completed capabilities include:

- Compact knowledge-base creation UI with advanced backend configuration in drawers.
- Graph and timeline backend chain with real API verification.
- Theme module contract and Worldline workbench handoff.
- Agent Run Ledger minimum audit contract.
- Agent Workbench real backend E2E.
- Dashboard authenticated QA.
- Content knowledge-base full chain.
- Full-site UI screenshot QA.
- Upload, parse, and query params linkage verification.
- Agent/run task directory audit.
- Temporary QA profile/cache/log cleanup.
- Worktree staging boundary report.

## Roadmap Principles

- Start from evidence, not generated answers.
- Preserve structured parse data from Docling; Markdown is an export surface, not the only intermediate representation.
- Keep LLM Wiki as the primary reading surface.
- Model time explicitly with `TemporalFact`, validity windows, conflict state, and provenance.
- Keep branch canvases evidence-bound; unsupported claims must be visible as unsupported.
- Let external Agents write only through Worldline service boundaries and audit logs.
- Make quality gates part of the product runtime, not a final report only.
- Keep the console compact: complex configuration belongs in drawers, command panels, detail panes, and payload previews.

## Phase P3: Evidence-Backed Product Slice

### P3-1 Evidence-Backed LLM Wiki

Goal: a real content knowledge base generates readable, citable, reviewable Wiki pages.

Backend scope:

- Ensure `WikiPage` exposes outline, sections, claims, citations, disputes, open questions, review state, and evidence coverage.
- Require every claim to reference `EvidenceAnchor` ids or be marked unsupported.
- Preserve source uri, page, line, bbox, char span, parser version, and content hash.
- Detect stale Wiki pages when source versions change.

Frontend scope:

- Show Wiki refs in the Worldline evidence rail.
- Let users focus an evidence anchor from a Wiki claim or citation.
- Show unsupported claims and open questions explicitly.

Acceptance evidence:

- Focused pytest for Wiki metadata contract.
- One live content KB with at least one Wiki page containing claims, citations, review state, and evidence coverage.
- Desktop and `390x844` screenshot QA.

### P3-2 Temporal Knowledge Graph

Goal: entities, relationships, and temporal facts become traceable, conflict-aware graph assets.

Backend scope:

- Preserve evidence ids on `KnowledgeEntity`, `KnowledgeRelationship`, and `TemporalFact`.
- Store validity windows, invalidations, conflict state, and provenance.
- Add contract tests for conflict detection and graph/timeline refs.
- Keep Neo4j projection read-only unless a later task explicitly scopes controlled writes.

Frontend scope:

- Route Worldline context into `/graph`.
- Let graph focus link back to Wiki claims, evidence anchors, and timeline events.
- Present conflict facts as reviewable state, not silent replacement.

Acceptance evidence:

- Focused pytest for graph conflict and timeline contract.
- Live KB graph rebuild with entities, relationships, temporal facts, and conflicts when applicable.
- `/graph` and `/worldline/:themeId` screenshots.

### P3-3 Worldline Branch Canvas

Goal: user questions generate comparable, evidence-bound worldline branches instead of a single answer paragraph.

Backend scope:

- Keep `/worldline/generate` compatible with `worldlineStore.hydrate`.
- Add `wikiRefs`, `entityRefs`, `timelineRefs`, `quality`, and `routeTrace` to branches.
- Disallow evidence-free default conclusions.

Frontend scope:

- Left-to-right root question, branch, inspection, and convergence layout.
- Branch hover/select updates inspector, evidence rail, timeline scrubber, and graph focus.
- Complex branch generation options live in a command panel or drawer.

Acceptance evidence:

- Nonblank canvas at desktop and mobile widths.
- No page-level horizontal overflow at `390x844`.
- Inspector shows source, Wiki, entity, timeline, and gate refs.

### P3-4 Agent Run Ledger And Replay

Goal: Agent tool calls, evidence reads, decisions, artifacts, gates, and handoffs form a replayable ledger.

Backend scope:

- Maintain `/api/worldline/runs` list, detail, events, artifacts, gates, evidence, and knowledge reads.
- Audit MCP reads, failed reads, branch decisions, artifact saves, archive/restore, and bulk maintenance.
- Link run events to branch ids and quality gates.

Frontend scope:

- Agent Workbench defaults to real backend runs.
- Local preview remains a clearly marked fallback only.
- Details drawer exposes manifest, resources, gates, artifacts, and decision replay.

Acceptance evidence:

- Focused pytest for run ledger and audit contract.
- Browser E2E with a temporary admin, followed by cleanup verification.

### P3-5 MCP And Skill Governance

Goal: tools and external Agents are useful but cannot bypass governance.

Backend scope:

- Default application MCP enables only the controlled `worldline` server.
- Tool manifests declare read/write scope, admin intent, audit behavior, and subagent lanes.
- Direct database-write MCP, unrestricted filesystem MCP, shell MCP, Docker/Kubernetes admin MCP, and external communication write MCP stay disabled by default.

Codex-side workflow:

- Use local Worldline skills for orientation, backend contracts, knowledge pipeline, frontend workbench, MCP governance, and eval release.
- Use Browser/Playwright for local UI QA.
- Use GitHub for PR/issue/CI work only when the task needs remote repository context.
- Use conditional research tools only after source, license, permissions, network reach, data exposure, and rollback are reviewed.

Acceptance evidence:

- Governance report passes the release gate.
- Tool manifest has subagent lanes and audit log fields.
- Evidence records any newly enabled tool and rollback path.

### P3-6 Quality Gate Replay

Goal: quality gates explain why a branch, Wiki page, graph fact, or Agent run passed or failed.

Backend scope:

- Gate evidence coverage, citation accuracy, graph consistency, Wiki freshness, retrieval quality, hallucination, MCP permission, cost, and latency.
- Store failure reasons with refs to evidence, Wiki, graph, timeline, branch, and run events.
- Support replay by KB, theme, branch, and run.

Frontend scope:

- Gate panel in the branch inspector.
- Failure items can jump to evidence anchors, Wiki sections, graph nodes, timeline events, or Agent run events.

Acceptance evidence:

- At least one intentional failure replay in UI.
- Release gate covers new quality gate contract.

### P3-7 Compact Console UX

Goal: keep backend capability complete while the user interface stays compact and operational.

Rules:

- First screen is a console, not a marketing page.
- Use drawers, command panels, detail panes, and payload previews for complex options.
- Cards are for repeated items, modals, and framed tools only.
- Prefer existing Vue 3, Vite, Pinia, Ant Design Vue, G6, D3, Sigma, Graphology, and ECharts assets before adding dependencies.
- Do not default to Three.js or broad new visual dependencies.

Acceptance evidence:

- Screenshot QA for `/`, `/themes`, `/worldline`, `/worldline/:themeId`, `/graph`, `/database`, `/dashboard`, and `/extensions`.
- Desktop and `390x844` mobile coverage.
- No console error/warn and no page-level horizontal overflow.

## Phase P4: Production Hardening

Goal: make the evidence-backed product slice reliable enough for repeated project use.

Scope:

- Background job retry and failure evidence for parsing, indexing, Wiki generation, graph rebuild, and quality gates.
- Source versioning, stale asset detection, rebuild queues, and rollback.
- Cost and latency budgets per KB, run, branch, and quality gate.
- Admin observability for failed jobs, blocked queues, and unavailable external services.
- Data cleanup routines for temporary files, deleted KBs, MinIO objects, and archived run artifacts.

Acceptance evidence:

- Integration tests for retry, failure records, and cleanup.
- Dashboard or admin surface for job health and queue state.
- Release gate includes operational readiness checks.

## Phase P5: Collaboration And Public Demo

Goal: support controlled external use without weakening the service boundary.

Scope:

- Public demo dataset with safe source material.
- Read-only shared Worldline branch views.
- Exportable evidence bundles and replay capsules.
- GitHub PR/issue integration for project work only after connector scope review.
- Optional research ingestion tools such as Firecrawl/Tavily only after source and data exposure review.

Acceptance evidence:

- Public demo release gate.
- No secrets or personal credentials in repo, Markdown, URLs, screenshots, or task evidence.
- Demo route has reproducible screenshots and rollback instructions.

## Default Execution Order

1. Orient: read `AGENTS.md`, `README.md`, `docs/index.md`, and the active task directory.
2. Align: define scope, non-goals, acceptance evidence, and risk boundary.
3. Design: map data objects, APIs, UI surfaces, tools, and rollback.
4. Atomize: break into vertical slices with focused verification.
5. Implement: one main agent owns writes; subagents do bounded review or disjoint work.
6. Validate: run the smallest tests that cover the changed surface plus screenshot QA when UI changes.
7. Record: update `.ai/tasks/<date-task>/EVIDENCE.md` and `D:\document\OutputMD`.
8. Commit: stage by logical package, inspect cached diff, then commit when the package is coherent.

## Do Not Do

- Do not turn Worldline into a normal RAG chat page.
- Do not use old PoE/demo/archive planning as current truth.
- Do not default-enable database-write MCP, unrestricted filesystem MCP, shell MCP, or Docker/Kubernetes admin MCP.
- Do not hide unsupported claims in generated prose.
- Do not let mock/local preview data masquerade as real backend capability.
- Do not commit temporary profiles, caches, credentials, local env files, or generated dependency directories.
