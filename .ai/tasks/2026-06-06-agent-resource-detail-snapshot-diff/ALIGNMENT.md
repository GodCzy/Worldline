# Alignment

## Goal

Let the Agent Workbench compare the currently inspected Resource Detail with a saved `resource_detail_snapshot` artifact.

## Scope

- Add a frontend-only diff action for saved Resource Detail snapshot artifacts.
- Reuse `GET /api/worldline/runs/{run_id}/artifacts/read` with `include_content=true`.
- Compare the current Resource Detail response against the saved snapshot response.
- Show added, removed, changed, and unchanged path counts plus a compact changed-path list.
- Preserve existing save, read replay, Registry focus, and MCP copy flows.

## Acceptance Criteria

- Saved `resource_detail_snapshot` Registry rows expose a `Diff Detail` action when a current Resource Detail is loaded.
- Clicking `Diff Detail` reads the saved snapshot artifact with `include_content=true`.
- The Resource Detail panel shows a diff summary and changed paths.
- The diff action is read-only and does not mutate backend state.
- No backend API or schema changes.
- Build and Chrome CDP QA pass.

## Out Of Scope

- No backend diff endpoint.
- No schema migration.
- No destructive restore behavior.
- No cross-run write or artifact creation.
