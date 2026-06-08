# Design

## Current Behavior

Saved Resource Detail snapshots can be registered as run artifacts, but clicking them in the Registry only focuses the artifact rail. The user cannot directly replay the saved inspect result into the Resource Detail panel.

## Proposed Behavior

Resource Detail snapshot registry rows get a replay/read action. The action calls `worldlineRunApi.inspectRunArtifact(runId, { artifact_id, include_content: true })`, extracts the stored snapshot content, then repopulates:

- `resourceDrilldownTarget`
- `resourceDrilldownResult`
- `resourceDrilldownMessage`
- last MCP call context

If the backend response does not include a snapshot payload, the UI still shows the raw artifact read result as Resource Detail.

## Contract

The frontend only reads from the existing run artifact read endpoint. The saved snapshot schema remains `worldline.resource_detail_snapshot.v0.1`.

## Validation

Chrome CDP QA will mock a run with a saved `resource_detail_snapshot`, click the registry replay action, assert the artifact read request, and assert Resource Detail contains the stored inspect response content.
