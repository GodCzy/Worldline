# Worldline Completion Matrix

Updated: 2026-06-09

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
| Codex plugin inventory and workflow | Done | `.ai/tasks/2026-06-08-codex-plugin-completion-workflow/`, `docs/architecture/codex-plugin-inventory.md` |
| Worktree cleanup and commits | Done | `D:\document\OutputMD\2026-06-08-Worldline-Project-Operating-Plan-Worktree-Cleanup.md` |

## P3 Completion Matrix

| Slice | Current Status | Still Needed | Recommended Plugins / Tools |
|---|---|---|---|
| P3-1 Evidence-backed LLM Wiki | Done | Keep expanding stale/review workflow in later slices; current reading surface is implemented and QA evidence exists. | Browser, OpenAI Developers as needed |
| P3-2 Temporal Knowledge Graph | Done | Current acceptance is covered: backend conflict review, compact `/graph` conflict surface, graph/timeline/evidence focus links, relationship focus regression, read-only projection checks, and `/graph` plus `/worldline/:themeId` screenshots. Future canvas parity can expand if `/api/graph/subgraph` starts returning the same node ids as the Worldline review payload. | Build Web Data Visualization, Browser |
| P3-3 Worldline Branch Canvas | Partial | RouteTrace, quality status, insufficient-evidence hints, and mobile interaction regression. | Browser, Product Design, Data Visualization |
| P3-4 Agent Run Ledger And Replay | Verified Baseline | Continue productizing replay, pagination, artifact registry, and cross-run knowledge reads. | GitHub, Browser |
| P3-5 MCP And Skill Governance | Done | Current acceptance is covered: MCP defaults governance report, disabled-tool release gate, connector policy, rollback checklist, focused pytest, and release-gate fixture regression. | GitHub, OpenAI Developers |
| P3-6 Quality Gate Replay | Done | Current acceptance is covered: intentional failed gate payload stores reasons, replay thresholds, Evidence/Wiki/Graph/Timeline/Run refs, Branch Inspector replay panel, Strict Replay action, focused pytest, production build, and desktop/390px Browser QA screenshots. | Browser, Data Visualization |
| P3-7 Compact Console UX | Verified Baseline | Continue desktop plus 390px screenshot QA for every new feature. | Browser, Product Design |

## P4 Completion Matrix

| Area | Current Status | Work To Complete | Recommended Plugins / Tools |
|---|---|---|---|
| Backend task retry/failure evidence | Partial | Failure records and retry evidence for parsing/indexing/wiki/graph/gate jobs. | GitHub CI, Browser |
| Source versioning and stale rebuild | Partial | Source changes trigger stale Wiki, graph/timeline rebuild queue, and review state. | Browser, Spreadsheets |
| Cost/latency budgets | Not Started | KB/run/branch/gate budget tracking and dashboard surface. | Spreadsheets, Dashboard QA |
| Admin observability | Partial | Queue health, failed jobs, and external service unavailable surface. | Browser, Data Viz |
| Data cleanup routines | Partial | Temporary files, deleted KBs, MinIO objects, and archived artifact cleanup. | GitHub CI |

## P5 Completion Matrix

| Area | Current Status | Work To Complete | Recommended Plugins / Tools |
|---|---|---|---|
| Public demo dataset | Partial | Safe dataset, reproducible screenshots, no secrets. | Browser, Documents |
| Read-only shared branch views | Not Started | Read-only Worldline branch share view. | Browser, Product Design |
| Evidence bundle export | Not Started | Exportable evidence/replay capsule. | Documents, Spreadsheets |
| GitHub PR/issue integration | External | Requires user authorization before remote project management integration. | GitHub |
| Optional ingestion tools | External | Firecrawl/Tavily-style tools require source, permission, and secret evaluation. | MCP governance |

## Next Concrete Work

Do not repeat "new KB compact creation"; it is already done. Continue in this order:

1. P4 operational hardening: retry, queue health, cleanup, and budget surfaces.
2. P5 demo/share/export: safe public dataset, read-only branch view, evidence bundle export.
3. P3-3 Branch Canvas hardening: routeTrace, insufficient-evidence hints, and mobile interaction regression.

## Workflow Rule

Each slice must have:

- An independent `.ai/tasks/<YYYY-MM-DD-slice>/` directory.
- Clear acceptance evidence.
- Focused pytest, API QA, or Browser QA.
- An OutputMD summary.
- If an external connector is used, a record of authorization scope, write target, and rollback path.
