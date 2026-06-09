# Decisions

## D1. Use route query as the focus contract

Reason: `/graph` already uses query params for `db_id` and Worldline context. Adding `entity_id`, `fact_id`, and `evidence_id` preserves deep-linkability and avoids local-only state.

## D2. Keep canvas focus best-effort

Reason: Worldline graph review data and the legacy `/api/graph/subgraph` canvas can diverge. The focus banner and review cards are the authoritative trace surface for this slice.
