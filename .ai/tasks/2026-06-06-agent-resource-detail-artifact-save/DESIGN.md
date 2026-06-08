# Design

## Current Behavior

Resource Detail can be inspected through existing Worldline run APIs, and replay exports can already be registered as artifacts. There is no direct way to preserve an inspect result as a reusable run artifact.

## Proposed Behavior

Add a compact "Save Detail" action to the Resource Detail panel. The payload should capture:

- Resource URI and tool.
- Inspect response.
- Selected resource id/label.
- Active event and focused dossier context.
- Run id and branch id where available.

The save action calls the existing `worldlineRunApi.registerRunArtifact`, then refreshes the artifact registry and loaded event window through existing helpers.

## Artifact Shape

Use kind `resource_detail_snapshot` with a JSON content payload. This stays compatible with the current run artifact registry without a schema change.

## Validation

Chrome CDP QA:

- Load a run.
- Click artifact token to inspect Resource Detail.
- Click Save Detail.
- Assert `POST /api/worldline/runs/{run_id}/artifacts`.
- Assert registry message and event refresh.
