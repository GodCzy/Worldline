# Decisions

## 2026-06-06 Reuse Single-Run Endpoints

Bulk maintenance intentionally calls the existing audited single-run archive/restore endpoints instead of adding batch routes. This preserves one audit event per run and avoids introducing a backend batch contract before the operator workflow is proven.
