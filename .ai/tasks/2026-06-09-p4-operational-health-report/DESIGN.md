# P4 Operational Health Report Design

## Service

`WorldlineOperationalHealthService` queries existing tables only:

- `KnowledgeFile`
- `DocumentVersion`
- `SourceAsset`
- `WorldlineWorkflowRun`
- `QualityGateRun`

It also checks Redis availability through an injectable health provider so unit tests do not require a live Redis service.

## Endpoint

`GET /api/dashboard/worldline/operational-health` is mounted in the existing admin dashboard router. It accepts optional `db_id` and `limit` query params.

## Release Gate

`WorldlineReleaseGateService` includes `worldline_operational_readiness_contract`, which checks the service and route for queues, failure evidence, retry policy, budgets, cleanup readiness, and endpoint exposure.

## Follow-Up Boundary

The report identifies retry candidates and cleanup gaps. Later P4 slices should add controlled requeue commands and cleanup routines behind service boundaries.
