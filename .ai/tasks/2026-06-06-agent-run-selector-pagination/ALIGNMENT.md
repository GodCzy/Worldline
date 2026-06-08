# Alignment

## Goal

Use the existing backend run list pagination contract from the Agent Workbench Run Selector.

## Scope

- Add frontend pagination state for saved backend runs.
- Load the first page with `limit` and `offset=0`.
- Add a `Load More` control that requests the next backend page using `offset`.
- Preserve selected rows that remain loaded after refresh.
- Keep existing filters, rename, compare, archive, restore, and bulk maintenance behavior.

## Out Of Scope

- New backend routes.
- Infinite scrolling.
- Virtualized rows.
- Database/schema changes.
- Cleaning unrelated dirty worktree files.

## Acceptance

- Refresh loads the first page and resets offset.
- Load More calls `/api/worldline/runs?limit=8&offset=<loaded_count>`.
- Loaded rows append without duplicating existing run ids.
- The selector displays loaded count vs backend total.
- Browser QA proves first-page load, second-page load, and bulk action against a row from page two.
