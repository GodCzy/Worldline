# Design

## UI Placement

The capsule lives under `MCP READABLE` in the existing `REPLAY EXPORT` panel. This keeps export, registry, MCP readability, and external handoff in one operational surface.

## Capsule Shape

The generated JSON includes:

- `protocol`: `worldline-agent-handoff@0.1`
- `intent`: concise instruction for the receiving Agent
- `source`: run, event, dossier, and artifact URI metadata
- `mcp`: tool name, URI, args, write scope, and audit expectation
- `quality`: gate count, evidence count, replay step count, and rollback rule
- `checkpoints`: replay timeline checkpoint summaries

## Safety

- The capsule defaults to read-only MCP: `write_scope: none`.
- The MCP args keep `include_content: false`.
- The panel remains visible even when backend/admin save is unavailable, but labels the artifact as pending until saved.
- Clipboard failures fall back to showing the preview.
