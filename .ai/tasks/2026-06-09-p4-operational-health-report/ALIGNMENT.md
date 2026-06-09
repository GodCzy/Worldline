# P4 Operational Health Report Alignment

## Goal

Start P4 production hardening by adding a read-only operational health contract for queue state, failure evidence, retry policy, budget pressure, and cleanup readiness.

## Acceptance

- Backend service returns a deterministic report with queues, failure evidence, retry policy, budgets, cleanup readiness, and next actions.
- Admin dashboard exposes the report through a read-only endpoint.
- Release gate checks that the operational readiness contract exists.
- Focused tests cover failed parsing/indexing/document/workflow/gate evidence, budget violations, and Redis unavailable state.

## Not In This Slice

- No automatic retry execution.
- No destructive cleanup routine.
- No frontend dashboard panel yet.
