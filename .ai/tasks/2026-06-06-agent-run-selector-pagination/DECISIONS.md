# Decisions

## 2026-06-06 Use Existing Offset Contract

The backend already supports `offset`, so this task adds no backend route. Frontend Load More reuses the same filtered list route and keeps every run mutation behind the existing audited single-run endpoints.
