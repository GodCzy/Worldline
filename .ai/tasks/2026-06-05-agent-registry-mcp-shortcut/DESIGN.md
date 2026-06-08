# Design

## UI

Registry item rendering changes from one full-row button to a row with:

- main focus button: artifact label and type/status.
- secondary `Copy MCP` button: copies the exact MCP read call for that artifact.

## MCP Payload

The copied shortcut includes:

- `Tool: worldline.inspect_run_artifacts`
- `URI: worldline-run-ledger://<run_id>/artifacts/<artifact_id>`
- JSON args:
  - `run_id`
  - `artifact_id`
  - `include_content: false`
  - `audit_db_id: ""`

## Safety

- The shortcut is read-only.
- Planned artifacts still show planned URIs, while saved artifacts use their saved `runId` where available.
- Clipboard failure falls back to visible status text.
