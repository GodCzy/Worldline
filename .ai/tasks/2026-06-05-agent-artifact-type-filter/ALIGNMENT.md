# Alignment

## Goal

Make the Replay Export registry distinguish planned and saved artifact types so users can tell replay exports from Agent handoff capsules before and after backend save.

## Scope

- Show a combined registry list for planned local artifacts and saved run ledger artifacts.
- Add type filters for `All`, `Replay`, `Handoff`, and `Other`.
- Add compact type/status labels on registry items.
- Keep existing focus behavior and MCP read-only boundary.

## Non-Goals

- No backend route change.
- No database schema change.
- No new MCP tool.
- No automatic Agent execution.

## Acceptance

- Local preview shows a Registry with planned replay and handoff artifacts.
- Users can filter to `Replay` and `Handoff`.
- Registry items expose type/status without text overflow.
- Build and browser QA pass.
