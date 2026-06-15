# Worldline Completion Matrix

Updated: 2026-06-15

This matrix breaks "finish all Worldline work" into verifiable slices. The current source of truth is `D:\dev\Worldline`, current `.ai/tasks` evidence, OutputMD summaries, and runnable validation results. `D:\document\Worldline` is only a pointer.

## Status Legend

- Done: code plus tests, screenshots, or task evidence cover the current acceptance target.
- Verified Baseline: strong evidence exists, but the slice is expected to keep expanding in later phases.
- Partial: implementation or evidence exists, but coverage is not complete enough.
- Not Started: no current implementation or evidence.
- External: needs an account, permission, service, or user-selected integration.

## Current Baseline

| Area | Status | Current Evidence |
|---|---|---|
| New KB compact creation | Done | `DataBaseView.vue`, `.ai/tasks/2026-06-08-database-create-compact-modal/EVIDENCE.md`, screenshot QA |
| Theme module closure | Done | `.ai/tasks/2026-06-08-theme-module-closure/EVIDENCE.md` |
| Agent Workbench real E2E | Done | `.ai/tasks/2026-06-08-agent-workbench-real-e2e` |
| Dashboard admin real QA | Done | `.ai/tasks/2026-06-08-dashboard-admin-real-qa` |
| Content KB full chain | Verified Baseline | `.ai/tasks/2026-06-08-content-kb-full-chain/EVIDENCE.md` |
| Full-site UI QA | Done | `.ai/tasks/2026-06-08-full-site-ui-qa` |
| Upload/parse/query params | Done | `.ai/tasks/2026-06-08-upload-parse-query-params-linkage` |
| Graph backend first pass | Verified Baseline | `.ai/tasks/2026-06-08-graph-backend-data-chain` |
| Graph conflict review surface | Done | `.ai/tasks/2026-06-08-p3-2-graph-conflict-surface/EVIDENCE.md`, desktop and `390x844` screenshots |
| Graph/timeline focus links | Done | `.ai/tasks/2026-06-09-p3-2-graph-focus-links/EVIDENCE.md`, `.ai/tasks/2026-06-09-p3-2-focused-regression-hardening/EVIDENCE.md` |
| P3-2 focused graph regression | Done | Shared graph focus utility tests, focused backend pytest, `/graph` and `/worldline/:themeId` desktop plus `390x844` screenshots |
| P3-3 branch canvas completion | Done | `.ai/tasks/2026-06-14-p3-3-branch-canvas-completion/EVIDENCE.md`, focused backend pytest, production build, Edge CDP desktop and `390x844` screenshots |
| Codex plugin inventory and workflow | Done | `.ai/tasks/2026-06-08-codex-plugin-completion-workflow/`, `docs/architecture/codex-plugin-inventory.md` |
| Worktree cleanup and commits | Done | `D:\document\OutputMD\2026-06-08-Worldline-Project-Operating-Plan-Worktree-Cleanup.md` |

## P3 Completion Matrix

| Slice | Current Status | Still Needed | Recommended Plugins / Tools |
|---|---|---|---|
| P3-1 Evidence-backed LLM Wiki | Done | Keep expanding stale/review workflow in later slices; current reading surface is implemented and QA evidence exists. | Browser, OpenAI Developers as needed |
| P3-2 Temporal Knowledge Graph | Done | Current acceptance is covered: backend conflict review, compact `/graph` conflict surface, graph/timeline/evidence focus links, relationship focus regression, read-only projection checks, and `/graph` plus `/worldline/:themeId` screenshots. Future canvas parity can expand if `/api/graph/subgraph` starts returning the same node ids as the Worldline review payload. | Build Web Data Visualization, Browser |
| P3-3 Worldline Branch Canvas | Done | Current acceptance is covered: branch-level routeTrace, gate refs, evidence-required policy, support/quality hints, evidence-free branch blocking, Inspector surfacing, hover/focus preview, keyboard selection, production build, and desktop plus `390x844` CDP QA. | Browser, Product Design, Data Visualization |
| P3-4 Agent Run Ledger And Replay | Done | Current acceptance is covered: run ledger API, event/artifact/gate/evidence pagination, run selector filters/pagination, bulk archive/restore, replay manifest, artifact registry, resource drilldown/diff, cross-run knowledge reads, audit logs, and real API/Browser E2E evidence. Future phases can expand retention and multi-user operations. | GitHub, Browser |
| P3-5 MCP And Skill Governance | Done | Current acceptance is covered: MCP defaults governance report, disabled-tool release gate, connector policy, rollback checklist, focused pytest, and release-gate fixture regression. | GitHub, OpenAI Developers |
| P3-6 Quality Gate Replay | Done | Current acceptance is covered: intentional failed gate payload stores reasons, replay thresholds, Evidence/Wiki/Graph/Timeline/Run refs, Branch Inspector replay panel, Strict Replay action, focused pytest, production build, and desktop/390px Browser QA screenshots. | Browser, Data Visualization |
| P3-7 Compact Console UX | Done | Current acceptance is covered: compact KB creation modal, Agent Workbench compact detail drawer, full-site desktop and `390x844` UI QA, and P3-3 desktop/mobile canvas QA. Continue screenshot QA for future features. | Browser, Product Design |

## P4 Completion Matrix

| Area | Current Status | Work To Complete | Recommended Plugins / Tools |
|---|---|---|---|
| Backend task retry/failure evidence | Done | Operational health exposes parsing/indexing/document/workflow/gate failures, retry policy, and controlled `requeue` action coverage with audit evidence. Keep real queue-worker replay in routine regression once production workers are attached. | GitHub CI, Browser |
| Source versioning and stale rebuild | Done | `mark_source_stale` marks source assets and Wiki pages stale, records review metadata, and queues Wiki/graph/quality-gate rebuild workflow evidence. | Browser, Spreadsheets |
| Cost/latency budgets | Done | KB-scoped operational budgets persist through admin action payloads; health reports expose legacy flat and scoped KB/run/branch/gate observations plus violations; Dashboard shows compact budget pressure. | Spreadsheets, Dashboard QA |
| Admin observability | Done | Admin-only health and action endpoints are wired into a compact Dashboard P4 panel with refresh, metrics, action drawer, payload editor, and result preview. | Browser, Data Viz |
| Data cleanup routines | Done | Controlled cleanup covers safe temporary files, deleted-KB readiness, MinIO candidates with explicit delete flag, and archived run artifact pruning through the run ledger. | GitHub CI |

## P5 Completion Matrix

| Area | Current Status | Work To Complete | Recommended Plugins / Tools |
|---|---|---|---|
| Public demo dataset | Done | Safe deterministic dataset is served by `WorldlinePublicDemoService`; P5 QA covers reproducible screenshots and no-secret scan. | Browser, Documents |
| Read-only shared branch views | Done | `/worldline/share/demo-branch-evidence` renders a read-only Worldline branch share view backed by public demo API. | Browser, Product Design |
| Evidence bundle export | Done | JSON and Markdown evidence/replay capsules export branch, evidence, Wiki, graph, timeline, gate, replay, rollback, and checksum sections. | Documents, Spreadsheets |
| GitHub PR/issue integration | External | Requires Joy authorization before remote project management integration; connector scope and rollback remain gated. | GitHub |
| Optional ingestion tools | External | Firecrawl/Tavily-style tools require source, permission, and secret evaluation before enablement. | MCP governance |

## Next Concrete Work

Do not repeat "new KB compact creation"; it is already done. Continue in this order:

1. Treat local P5 demo/share/export as complete; only external connector authorization remains outside repo control.
2. Keep P5 release checks in the release path: public-demo focused tests, production build, share-route static QA, docs build, and release gate.
3. Keep P4 regression checks in the release path: focused backend tests, production build, dashboard static QA, and docs build.
4. Keep P3 regression checks in the release path: focused backend tests, production build, and desktop plus `390x844` screenshots for future UI changes.

## Workflow Rule

Each slice must have:

- An independent `.ai/tasks/<YYYY-MM-DD-slice>/` directory.
- Clear acceptance evidence.
- Focused pytest, API QA, or Browser QA.
- An OutputMD summary.
- If an external connector is used, a record of authorization scope, write target, and rollback path.
