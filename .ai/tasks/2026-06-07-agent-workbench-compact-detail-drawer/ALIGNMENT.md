# Alignment

## Goal

Make the Agent Workbench Resource Detail area clearer and less cluttered while preserving access to complete backend payloads.

## Scope

- Keep backend-required data accessible: response JSON, MCP args, manifest args, and last MCP call args.
- Move large JSON/pre blocks behind Chinese detail buttons and a lightweight modal.
- Keep the main page focused on status, tool, URI, counts, and primary actions.
- Localize the affected controls and summaries into concise Chinese.

## Acceptance Criteria

- The main Resource Detail panel no longer renders the full backend response by default.
- Users can open a modal to inspect the full backend response.
- Users can open the modal for MCP readable args, run manifest args, and last MCP call args.
- The diff panel still shows concise counts, changed paths, and save action.
- Existing diff artifact save QA still passes.

## Out Of Scope

- No backend changes.
- No schema changes.
- No full-page redesign.
- No removal of backend evidence content.
