# P4 Operational Health Report Decisions

## Read-Only First

This slice establishes observability before adding write actions. Retry and cleanup execution will be scoped separately so they can be audited and tested.

## No Schema Change

The report uses existing `KnowledgeFile`, `DocumentVersion`, `WorldlineWorkflowRun`, and `QualityGateRun` records. This avoids migration risk while still producing useful operational evidence.

## Admin Endpoint

The route lives under the existing dashboard router because it is operational/admin data, not public Worldline content.
