# Decisions

## Read-only first

Gate read is added as `write_scope: none`; the existing `worldline.run_quality_gate` remains the write/compute path for deterministic quality-gate runs.

## No schema churn

The run ledger already stores normalized `gateResults`; this stage reads that structure instead of introducing new tables or migrations.

## Audit optional

Like artifact inspect, gate inspect records MCP audit only when `audit_db_id` is provided. This keeps local run preview usable while preserving audit support for real knowledge DB contexts.
