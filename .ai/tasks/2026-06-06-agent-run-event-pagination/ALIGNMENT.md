# Alignment

## Goal

Use the existing backend run event pagination contract in the Agent Workbench Run Events rail.

## Scope

- Add frontend event pagination state.
- Load the first event page with `limit` and `offset=0`.
- Add a `Load More Events` control using `offset=<loaded_event_count>`.
- Keep event filters and selected event detail behavior.
- Preserve the existing preview event fallback when no backend run is loaded.

## Out Of Scope

- Backend event ordering changes.
- New event filter API params.
- Virtualized event list.
- Database/schema changes.
- Cleaning unrelated dirty worktree files.

## Acceptance

- Refresh Events requests the first event page using backend `limit/offset`.
- Load More Events requests the next event page.
- Loaded event pages append without duplicate event ids.
- The rail displays loaded event count vs backend total.
- Browser QA proves first-page load, second-page load, and filter counts over the loaded event window.
