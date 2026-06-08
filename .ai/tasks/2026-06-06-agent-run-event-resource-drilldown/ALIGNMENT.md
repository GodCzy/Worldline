# Alignment

## Goal

Connect Run Event detail tokens to the existing backend resource drilldown so event audit can move from "what happened" to "inspect the referenced resource".

## Scope

- Keep existing event token focus behavior.
- When an event token references backend-inspectable resources, trigger the existing run resource inspector.
- Target resource kinds:
  - artifact
  - gate
  - evidence/source
  - wiki/graph/timeline knowledge resources
- Preserve unsupported token behavior for branch, episode, tool, permission, and skill as local focus only.

## Acceptance Criteria

- Clicking an artifact/gate/evidence/wiki/graph/timeline token focuses the local dossier and loads backend Resource Detail when admin ledger access is available.
- The Resource Detail panel shows the correct MCP tool and response payload.
- Unsupported tokens still focus locally without trying unsupported backend inspect calls.
- No backend API or schema changes.
- Build and Chrome CDP QA pass.

## Out Of Scope

- Server-side resource discovery changes.
- New MCP tools.
- Token-level inline previews inside each event card.
