# Worldline Agent Decision Snapshot Alignment

Date: 2026-06-05

## Goal

Make branch approval/rejection events replayable in the Agent Workbench by surfacing the structured decision summary that the run ledger already emits.

## Current Gap

- Backend branch decision events include `status`, `reason`, `branch_title`, `branch_type`, `quality_status`, `score`, and linked evidence/tool/gate/artifact ids.
- Frontend Event Detail currently shows only generic Event ID, Actor, Branch, Run, then linked tokens.
- `formatEventSummary` compresses the decision into a plain inline string, so the replay does not clearly show why a branch was approved or rejected.

## Scope

- Add a Decision Snapshot section in Event Detail when event summary has branch decision fields.
- Improve event summary text to include branch title and quality status.
- Keep existing Evidence/Tool/Timeline/Gate/Artifact token focus behavior.
- Do not change backend service, router, storage, or API contract.

## Out Of Scope

- No live admin login setup.
- No backend ledger mutation in browser QA.
- No new dependency.
- No unrelated UI refactor.

## Acceptance

- Event Detail can render a structured decision snapshot for branch decision events.
- Snapshot includes decision status, branch title, branch type, quality status, score, and reason.
- Existing link chips and focus tokens still render.
- Frontend build and screenshot QA pass.
