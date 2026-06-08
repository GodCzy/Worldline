# Alignment

## Goal

Keep the Agent Workbench Run Events rail synchronized after backend run mutations while preserving the event pagination model introduced in the previous step.

## Scope

- Reuse the existing backend `GET /api/worldline/runs/{run_id}/events?limit=&offset=` contract.
- Refresh the currently loaded event window after successful run mutations such as rename, archive/restore, artifact registration, branch decisions, and skill proposals.
- Preserve local preview behavior when no backend run is active.
- Keep the change frontend-only unless current evidence shows a backend contract gap.

## Acceptance Criteria

- A mutation that returns `latestEvent` updates the active run and then refreshes Run Events with a limit at least as large as the currently loaded page window.
- The event rail reflects backend ordering, total count, and new event content after a mutation.
- Existing run selector pagination and event pagination behavior remain intact.
- Build and Chrome CDP QA pass.

## Out Of Scope

- No database schema changes.
- No new backend endpoints.
- No redesign of event cards or event detail semantics.
