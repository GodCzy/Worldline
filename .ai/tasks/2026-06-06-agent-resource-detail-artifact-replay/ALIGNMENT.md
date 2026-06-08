# Alignment

## Goal

Let saved `resource_detail_snapshot` artifacts become replayable from the Agent Workbench registry.

## Scope

- Add a frontend-only replay/read path for saved Resource Detail snapshot artifacts.
- Reuse the existing `GET /api/worldline/runs/{run_id}/artifacts/read` contract.
- Populate the Resource Detail panel from saved snapshot content when available.
- Preserve existing registry focus, MCP copy, replay export, and handoff flows.

## Acceptance Criteria

- Registry rows for saved `resource_detail_snapshot` artifacts expose a clear replay/read action.
- Clicking a saved Resource Detail snapshot calls the existing artifact read endpoint with `include_content=true`.
- The Resource Detail panel shows the snapshot response, source URI/tool, and a replay-loaded message.
- Registry state remains visible after replay.
- No backend API or schema changes.
- Build and Chrome CDP QA pass.

## Out Of Scope

- No artifact storage changes.
- No new backend route.
- No schema migration.
- No destructive replay/restore writes.
