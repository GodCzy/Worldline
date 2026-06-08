# Decisions

## D1. Store conflict state in metadata first

Reason: the current schema already supports JSON metadata on `TemporalFact`. A metadata-only contract gives the UI and quality gate a stable review state without introducing migration risk.

## D2. Keep Neo4j projection read-only

Reason: P3-2 explicitly says Neo4j projection should remain read-only unless a later task scopes controlled writes.

## D3. Start with backend contract before `/graph` UI

Reason: the UI should consume a proven conflict contract. This slice creates that contract and focused tests first.
