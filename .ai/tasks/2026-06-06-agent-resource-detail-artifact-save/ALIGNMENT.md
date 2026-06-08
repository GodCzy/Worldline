# Alignment

## Goal

Let inspected Resource Detail become a replayable run artifact from the Agent Workbench.

## Scope

- Add a frontend action to save the currently loaded Resource Detail.
- Reuse existing `POST /api/worldline/runs/{run_id}/artifacts`.
- Preserve existing replay export and handoff artifact flows.
- Refresh artifact registry and loaded run events after save.

## Acceptance Criteria

- Resource Detail panel exposes a Save Detail action only when an inspect result is loaded.
- Clicking Save Detail posts a structured artifact payload to the backend run artifact endpoint.
- The saved artifact appears in the registry state returned by the backend.
- Run Events refreshes after save so the newly registered artifact event can appear.
- No backend API or schema changes.
- Build and Chrome CDP QA pass.

## Out Of Scope

- No new artifact storage backend.
- No schema migration.
- No binary content upload.
