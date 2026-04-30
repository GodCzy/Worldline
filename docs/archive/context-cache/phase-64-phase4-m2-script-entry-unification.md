# Phase 64 - 4b M2 script entry unification baseline

## Baseline

- Prior state:
  - `4b-P0` graph/auth permission boundary tests were already locked.
  - `scripts/qa_graph_auth_readonly_check.py` already produced an M1-compatible evidence package.
- This pass target:
  - unify script entry parameters and environment variables
  - make exit-code contract explicit
  - keep business route logic untouched

## Scope Changed

- Updated `scripts/qa_graph_auth_readonly_check.py` only.
- Added CLI aliases:
  - `--output-dir` for `--out-dir`
  - `--artifact-prefix` for `--package-prefix`
  - `--timeout` for `--timeout-seconds`
- Added environment-variable aliases:
  - `WORLDLINE_QA_API_BASE`
  - `WORLDLINE_QA_FRONTEND_BASE`
  - `WORLDLINE_QA_OUT_DIR`
  - `WORLDLINE_QA_PREFIX`
  - `WORLDLINE_QA_ADMIN_TOKEN`
  - `WORLDLINE_QA_USER_TOKEN`
  - `WORLDLINE_QA_TIMEOUT_SECONDS`
  - `WORLDLINE_QA_ALLOW_TEMP_USER`
  - `WORLDLINE_QA_SELF_CHECK`
- Made exit-code contract explicit in output metadata and console output.

## Validation Executed

- `python -m py_compile scripts/qa_graph_auth_readonly_check.py`
- Self-check via env alias:
  - `WORLDLINE_QA_PREFIX=qa-phase4-m2-entry`
  - `WORLDLINE_QA_OUT_DIR=artifacts`
  - `WORLDLINE_QA_SELF_CHECK=1`
  - result: pass, exit code `0`
- Self-check via CLI alias:
  - `--self-check --output-dir artifacts --artifact-prefix qa-phase4-m2-cli`
  - result: pass, exit code `0`

## Residual Risk

- Live API verification still requires a running `api-dev` service and available auth tokens.
- This pass intentionally avoided all `/api/graph/*` business route changes.

## Phase Judgment

- Current phase: `Phase 4b M2 script-entry hardening`
- Readiness for next step: `ready for live M2 replay when API service is available`
- Main remaining gap: `real service-backed replay of the unified entry contract`
