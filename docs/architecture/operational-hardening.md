# Operational Hardening

Updated: 2026-06-09

## Goal

P4 makes the evidence-backed Worldline slice reliable enough for repeated project use. Operational evidence must cover job failures, retry eligibility, queue state, budget pressure, cleanup readiness, and unavailable external services.

## Operational Health Report

`WorldlineOperationalHealthService` is the read-only contract for P4 operational readiness. It does not perform retries or cleanup directly. It reports:

- `queues`: Redis/ARQ availability, knowledge-file status counts, failed file records, active workflow runs, and failed workflow runs.
- `failure_evidence`: parsing, indexing, Wiki generation, graph rebuild, and quality-gate failure records.
- `retry_policy`: retryable statuses and evidence fields for parsing, indexing, Wiki rebuild, graph rebuild, and quality gate jobs.
- `budgets`: default cost/latency budgets, observed latest quality-gate cost/latency, failed file counts, failed workflow counts, and budget violations.
- `cleanup_readiness`: temporary file tracking plus explicit follow-up requirements for deleted KB cleanup, MinIO object cleanup, and archived artifact cleanup.

Admin endpoint:

```text
GET /api/dashboard/worldline/operational-health?db_id=<optional>&limit=10
```

The endpoint is admin-only through the dashboard router. It is read-only and returns JSON evidence for UI/admin surfaces.

## Current Boundary

This slice establishes observability and release-gate coverage. Controlled requeue executors, cleanup routines, and dashboard visual panels remain follow-up work. Future write actions must go through existing Worldline service boundaries and record audit evidence.

## Release Gate

`WorldlineReleaseGateService` includes `worldline_operational_readiness_contract`. The check fails if the operational health service or dashboard endpoint is removed, or if the report no longer exposes queues, failure evidence, retry policy, budgets, and cleanup readiness.
