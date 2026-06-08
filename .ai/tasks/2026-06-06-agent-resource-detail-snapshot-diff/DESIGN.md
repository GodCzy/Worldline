# Design

## Current Behavior

The Agent Workbench can save Resource Detail as a `resource_detail_snapshot` and read the saved snapshot back into the Resource Detail panel. It cannot yet compare a live/current inspect result against a saved snapshot.

## Proposed Behavior

Add a `Diff Detail` action to saved Resource Detail snapshot Registry rows. The action:

1. Requires a current `resourceDrilldownResult`.
2. Reads the saved snapshot artifact through the existing artifact read endpoint.
3. Extracts `selected.content.response` or `selected.content` from the saved artifact.
4. Flattens current and saved JSON into path/value pairs.
5. Produces counts and a compact changed-path list.
6. Renders the result in the Resource Detail panel.

## Data Contract

No new backend contract. The frontend consumes the existing artifact read shape:

- `selected.content.schema === "worldline.resource_detail_snapshot.v0.1"`
- `selected.content.response`
- `selected.content.selected`

Fallback behavior compares raw selected content when the snapshot wrapper is missing.

## Validation

Chrome CDP QA will mock one current artifact inspect response and one saved snapshot artifact, run `Diff Detail`, assert the artifact read request, and verify the UI shows added/removed/changed counts and changed paths.
