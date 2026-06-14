# P4 Operational Hardening Completion Design

## Backend

- Keep `WorldlineOperationalHealthService` read-only.
- Add `WorldlineOperationalActionService` for controlled writes:
  - `requeue`: mark failed file/document/workflow records as queued/retrying and create queued `WorldlineWorkflowRun` records.
  - `mark_source_stale`: mark `SourceAsset` and related `WikiPage` records stale/review-required and enqueue wiki/graph/gate rebuild workflow.
  - `update_budgets`: persist scoped operational budgets in `KnowledgeBase.additional_params.worldline_operational`.
  - `cleanup`: perform safe temp-file deletion and record MinIO/deleted-KB/archived-artifact cleanup dispositions.
- Add `POST /api/dashboard/worldline/operational-health/actions`.
- Record every action through `WorldlineMcpAuditLog`.

## Frontend

- Add a compact Worldline P4 panel to `DashboardView.vue`.
- Keep first-level UI brief: status, Redis, failures, budget violations, cleanup blockers.
- Move complex inputs to an Ant Design drawer.

## Validation

- Focused pytest for health/action behavior.
- Existing P3/P4 release-gate tests.
- Vue SFC compile, Vite build, VitePress build, Docker compose config.
- Dashboard screenshot QA at desktop and mobile sizes with API stubs.
