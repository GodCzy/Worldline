# Worldline Agent Branch Decision Replay Alignment

Date: 2026-06-05

## Goal

Complete the Agent Workbench branch decision loop by exposing both approve and reject actions in the frontend, backed by the existing Worldline run ledger API.

## Current Gap

- Backend `WorldlineRunLedgerService` already supports `approve_branch` and `reject_branch`.
- Frontend API wrapper already exposes `worldlineRunApi.rejectBranch`.
- Agent Workbench branch actions only expose approve and trace.
- `handleBranchAction` only handles `approve`, so users cannot reject or replay a branch decision from the workbench.

## Scope

- Add a reject action to local branch templates.
- Route reject actions through `worldlineRunApi.rejectBranch`.
- Record a clear decision reason and update the local handoff/message state.
- Keep the same admin-gated behavior as approve: if backend access is unavailable, the UI must say it remains local preview.
- Validate that branch rejection creates a `branch.rejected` ledger event when access is available through the existing contract.

## Out Of Scope

- No backend API change.
- No persistent DB schema change.
- No destructive cleanup of the dirty worktree.
- No staged commit.

## Acceptance

- Branch Inspector shows a reject/rollback action.
- Clicking reject calls the same ledger flow as approve, but through `rejectBranch`.
- Frontend build passes.
- Browser QA proves the action is visible and, in the current unauthenticated/local state, produces an explicit local-preview/admin-needed message instead of silently failing.
