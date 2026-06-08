# Alignment

## Goal

Let the Agent Workbench persist a Resource Detail diff result as a run-ledger artifact after comparing a current Resource Detail with a saved snapshot.

## Scope

- Add a `Save Diff Artifact` action to the Resource Detail diff panel.
- Reuse the existing `POST /api/worldline/runs/{run_id}/artifacts` contract.
- Save a structured `resource_detail_diff` payload with markdown.
- Merge the registered artifact back into the frontend Registry after event refresh.
- Preserve the current Resource Detail and visible diff after saving.

## Acceptance Criteria

- A completed Resource Detail diff exposes `Save Diff Artifact` when the run ledger can be used.
- Clicking the action posts one artifact with `kind: resource_detail_diff`.
- The saved artifact includes current/saved labels, summary counts, preview paths, and source artifact id.
- The Registry shows the saved diff artifact without requiring a full page reload.
- Existing snapshot save, replay, and diff flows continue to pass.

## Out Of Scope

- No backend route changes.
- No schema migration.
- No artifact-to-artifact diff selector yet.
- No destructive mutation or restore behavior.
