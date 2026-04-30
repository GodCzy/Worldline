# Phase 67 - Phase 4b M2 secret precondition retry hardening

## Baseline

- Phase 66 had already closed the non-interactive M2 replay path around manifest-driven inputs and machine-readable main blocker output.
- The remaining operational gap was the behavior when admin/user secrets are missing or delayed in file-backed CI/local environments.

## This pass target

- Keep `scripts/qa_phase4_m2_replay.py` process-only.
- Make missing secrets easier to diagnose.
- Add the smallest useful retry for file-backed secret sources.
- Keep replay failure reporting machine-parseable and preserve the unique main blocker rule.

## Landed changes

1. `scripts/qa_phase4_m2_replay.py`
   - added a one-step retry for file-backed secret reads
   - kept CLI / manifest / env / file precedence intact
   - upgraded missing-secret errors to say which source chain was checked
   - preserved exit code `6` for precondition failures
   - kept business route logic untouched

## Validation executed

1. `python -m py_compile scripts/qa_phase4_m2_replay.py`
2. `retry_helper_ok` via import-time unit smoke on delayed file creation
3. CLI smoke with no admin/user secrets and a valid empty UI source dir
   - exit code: `6`
   - emitted `[m2-replay-error]` JSON
   - wrote `01-precondition-error.json`
   - wrote `02-main-blocker.json`
   - summary recorded `sources_checked`

## CI / workflow note

- No dedicated replay GitHub Actions workflow existed in this repo at the time of this pass.
- Therefore this pass only hardened the replay script itself and did not add a new workflow wrapper.
- Future CI wiring should continue to pass secrets via manifest or file-backed inputs to keep the replay non-interactive.

## Scope and risk

- Scope remains process/workflow hardening only.
- No backend route, permission semantics, or module-layer behavior changed.
- Residual operational risk:
  - if CI does not provide either a token value or a token file, replay still stops at the precondition gate by design.

## Phase judgment

- Current phase: `Phase 4b M2 secret-precondition hardening landed`
- Readiness for next phase: `ready for live M2 replay / CI wiring`
- Main remaining gap before advancing:
  - a dedicated replay CI workflow or runner job that supplies token files or a replay manifest consistently
