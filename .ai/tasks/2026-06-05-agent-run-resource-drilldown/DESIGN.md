# Design

## Backend

Add routes to `server/routers/worldline_run_router.py`:

- `/artifacts/read`: delegates to `inspect_run_artifacts`.
- `/gates`: delegates to `inspect_run_gates`.
- `/evidence`: delegates to `inspect_run_evidence`; supports `evidence_id` and `source_id`.
- `/knowledge`: delegates to `inspect_run_knowledge`; supports `kind` and `item_id`.

All routes:

- use `get_admin_user`;
- accept `limit` and optional `audit_db_id`;
- return `404` when the service result is `not_found`;
- preserve service response shape.

## Frontend

Add `worldlineRunApi` helpers:

- `inspectRunArtifact`
- `inspectRunGates`
- `inspectRunEvidence`
- `inspectRunKnowledge`

Extend `WorldlineAgentWorkbenchView.vue`:

- parse backend manifest resource args;
- render `Inspect` button per backend manifest sample resource;
- call matching helper based on `resource.tool` or manifest section;
- show selected result status, tool, URI, selected label, and compact JSON.

## Validation

- Focused pytest for route contracts.
- Frontend build.
- CDP browser QA with mocked API responses to prove frontend request and render path.
