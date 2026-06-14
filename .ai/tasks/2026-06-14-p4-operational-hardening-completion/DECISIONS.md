# P4 Operational Hardening Completion Decisions

## No schema migration for P4 closeout

P4 operational controls use existing durable tables and JSON metadata fields. This keeps the blast radius small while still producing auditable action records.

## Health report remains read-only

Write operations are separated into `WorldlineOperationalActionService` and a dedicated dashboard action endpoint.

## Cleanup is controlled

Temporary local files can be removed only when they resolve under known temp directories. MinIO/deleted-KB/archive cleanup records controlled dispositions and can be wired to deeper destructive deletion later with explicit operator approval.
