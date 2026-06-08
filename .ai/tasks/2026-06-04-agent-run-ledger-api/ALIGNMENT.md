# Alignment

## Goal

Move the Agent Workbench from a local preview toward a backend-backed run ledger by implementing the `/api/worldline/runs` contract that the frontend already wraps.

## Scope

- Add a durable file-backed `WorldlineRunLedgerService`.
- Add protected FastAPI routes for create/get/events/approve/reject/skill proposal.
- Avoid database migrations in this stage.
- Preserve existing `/api/knowledge/databases/{db_id}/worldline/*` contracts.

## Acceptance Criteria

- Backend can create a run, persist it, approve/reject branches, list events, and add skill proposals.
- New tests cover service behavior and route wiring.
- Focused checks pass or failures are documented.
