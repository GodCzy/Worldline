# Decisions

## 2026-06-06 Use Existing Event Endpoint

The backend already exposes run event `limit` and `offset`, so the first event pagination iteration stays frontend-only and reuses the audited run ledger read endpoint.
