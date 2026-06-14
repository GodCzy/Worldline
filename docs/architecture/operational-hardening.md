# Operational Hardening

Updated: 2026-06-14

## Goal

P4 makes the evidence-backed Worldline slice reliable enough for repeated project use. Operational evidence must cover job failures, retry eligibility, queue state, budget pressure, cleanup readiness, and unavailable external services.

## Operational Health Report

`WorldlineOperationalHealthService` is the read-only contract for P4 operational readiness. It does not perform retries or cleanup directly. It reports:

- `queues`: Redis/ARQ availability, knowledge-file status counts, failed file records, active workflow runs, and failed workflow runs.
- `failure_evidence`: parsing, indexing, Wiki generation, graph rebuild, and quality-gate failure records.
- `retry_policy`: retryable statuses and evidence fields for parsing, indexing, Wiki rebuild, graph rebuild, and quality gate jobs.
- `budgets`: legacy flat budget fields plus scoped KB/run/branch/gate budgets, observed metrics, and violations.
- `cleanup_readiness`: controlled-routine availability for temporary file cleanup, deleted KB readiness, MinIO object cleanup, and archived artifact cleanup.
- `operation_controls`: the admin action endpoint, supported actions, required `db_id`, dry-run support, and action payload shape hints.

Admin endpoint:

```text
GET /api/dashboard/worldline/operational-health?db_id=<optional>&limit=10
```

The endpoint is admin-only through the dashboard router. It is read-only and returns JSON evidence for UI/admin surfaces.

## Controlled Actions

`WorldlineOperationalActionService` owns the controlled P4 write actions. The dashboard router exposes a single admin-only action endpoint:

```text
POST /api/dashboard/worldline/operational-health/actions
```

Payload:

```json
{
  "db_id": "kb_xxx",
  "action": "requeue | mark_source_stale | update_budgets | cleanup",
  "payload": {}
}
```

Supported actions:

- `requeue`: requeues failed parsing, indexing, Wiki generation, graph rebuild, and quality-gate stages. It updates failed records with operation history, creates a queued `WorldlineWorkflowRun`, and records `worldline.operational_requeue` audit evidence.
- `mark_source_stale`: marks a `SourceAsset` stale by `asset_id`, `file_id`, or `source_uri`, marks related `WikiPage` records as `stale_review`, and queues Wiki/graph/quality-gate rebuild work.
- `update_budgets`: persists scoped operational budgets under `KnowledgeBase.additional_params.worldline_operational.budgets`. Effective scopes are `kb`, `run`, `branch`, and `gate`.
- `cleanup`: handles safe temporary file cleanup, deleted-KB readiness reporting, MinIO object candidates with explicit `delete_minio`, and archived artifact pruning through `WorldlineRunLedgerService`.

All actions keep the same service-boundary rules as the rest of Worldline: admin-only entrypoint, explicit `db_id`, dry-run support where deletion or dispatch risk exists, and audit records for operational evidence.

## Dashboard Surface

The admin Dashboard includes a compact P4 panel, not a large configuration page. It shows Redis status, failure count, budget pressure, cleanup readiness, and the first recommended next action. Complex payloads live in an action drawer with templates for requeue, cleanup, budget update, and stale-source marking.

## Release Gate

`WorldlineReleaseGateService` includes `worldline_operational_readiness_contract`. The check fails if the operational health service, action service, dashboard read endpoint, or dashboard action endpoint is removed, or if the report no longer exposes queues, failure evidence, retry policy, budgets, cleanup readiness, and operation controls.
