# Alignment

## Goal

Improve Agent Workbench operations by adding bulk maintenance controls to the Run Selector.

## Scope

- Let operators select multiple visible saved runs.
- Allow bulk archive for selected non-archived runs.
- Allow bulk restore for selected archived runs.
- Keep the existing single-run archive/restore behavior.
- Validate with Vite build, diff check, and browser QA.

## Out Of Scope

- New backend batch endpoints.
- Database schema changes.
- Hard delete or purge actions.
- Pagination beyond the existing visible selector list.
- Cleaning unrelated dirty worktree files.

## Acceptance

- Each visible run can be selected with a checkbox.
- The selector shows how many runs are selected.
- Bulk archive calls the existing archive endpoint for selected non-archived runs.
- Bulk restore calls the existing restore endpoint for selected archived runs.
- The UI refreshes run summaries and clears selection after a completed bulk action.
- Browser QA proves bulk archive and bulk restore requests are issued and reflected in row state.
