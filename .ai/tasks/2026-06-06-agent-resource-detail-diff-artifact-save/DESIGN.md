# Design

## Current Behavior

The Resource Detail diff is transient UI state. It can compare the current inspected Resource Detail with a saved snapshot, but the comparison itself is not preserved as a ledger artifact.

## Proposed Behavior

After a successful diff, the Resource Detail panel shows `Save Diff Artifact`.

The action:

1. Requires `resourceDetailCompareResult`.
2. Builds a stable `resource_detail_diff` artifact id from run id and compared snapshot artifact id.
3. Saves structured JSON content and markdown through the existing artifact register endpoint.
4. Refreshes the current event window.
5. Re-merges the registered artifact so stale artifact-list responses do not hide it.
6. Keeps current Resource Detail and diff visible after save.

## Payload

The content schema is `worldline.resource_detail_diff.v0.1`:

- `run`
- `current`
- `saved`
- `summary`
- `preview`
- `source`

The markdown mirrors the summary and changed path preview for human review.

## Validation

Use a Chrome CDP QA script that mocks the run ledger APIs, performs current-vs-saved diff, clicks `Save Diff Artifact`, asserts the POST payload, and verifies the Registry shows the saved diff artifact.
