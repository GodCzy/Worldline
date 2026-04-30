# Phase 69 - Phase 4b replay workflow precheck delegation

## Baseline

- `scripts/qa_phase4_m2_replay.py` already owns machine-readable precondition failures and retry-on-file-secret behavior.
- The remaining CI blocker was the workflow short-circuiting before replay execution when secrets or the tracked UI evidence file were missing.

## This pass target

- Keep replay orchestration in workflow/script scope only.
- Remove workflow-level early exits for secrets/UI evidence.
- Let the replay script emit the authoritative precondition failure, run dir, blocker JSON, and summary.

## Landed changes

1. `.github/workflows/phase4-replay.yml`
   - removed the workflow preflight `exit 6` for missing admin/user secrets
   - removed the workflow preflight `exit 6` for the tracked UI assertion file
   - kept manifest creation and script invocation intact
   - kept retry policy unchanged: retry only `exit_code=2/3`

## Validation executed

1. `python -m py_compile scripts/qa_phase4_m2_replay.py` (pass)
2. Replay-script precondition smoke still returns `EXIT=6`
3. Workflow text review confirms the early-exit secret/UI gate is gone

## Scope and risk

- Scope remains workflow/script only.
- No backend route, auth, or module-layer change was made.
- Residual operational risk:
  - if the workflow runner does not provide usable secrets or the tracked UI evidence directory, replay still fails by design, but now the failure is reported by the replay script with evidence artifacts instead of being short-circuited by workflow logic.

## Phase judgment

- Current phase: `Phase 4b replay CI stabilization`
- Readiness for next phase: `ready for CI admission replay`
- Main remaining gap before advancing:
  - run the workflow once in GitHub Actions with real secrets so the artifact path and exit-code mapping are proven end to end
