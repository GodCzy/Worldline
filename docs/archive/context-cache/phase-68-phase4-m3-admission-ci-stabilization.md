# Phase 68 - Phase 4b M3 admission CI stabilization

## Baseline

- Prior state:
  - M2.5 non-interactive replay already landed with manifest + token-file support.
  - Replay script returns machine-readable failure and unique main blocker.
- This pass target:
  - stabilize replay execution path for CI admission checks
  - keep changes strictly in workflow/script/docs layer

## Subagent decomposition (actually executed)

1. `qa_release_auditor`
   - added CI workflow path for replay execution
   - mapped exit codes to CI status labels and artifact upload strategy
2. `backend_worker`
   - hardened secret precondition error clarity
   - added minimal file-secret retry in replay script
3. `frontend_worker`
   - confirmed `30/31/32` evidence chain remains reusable for headless CI
4. `system_mapper`
   - confirmed no graph/auth/router runtime semantics drift
5. `product_architect`
   - confirmed no PoE leakage to platform fixed layer and no runtime dependency on QA artifacts

## Landed changes in this pass

1. `.github/workflows/phase4-replay.yml`
   - workflow_dispatch CI entry for replay
   - default `ui_source_dir` points to tracked baseline evidence directory
   - explicit precondition fail handling for missing secrets/UI evidence file
   - one-time retry policy for `exit_code=2/3`
   - archives full replay run directory as artifact

2. `docs/22-phase4-m2-unified-replay.md`
   - documented CI default `ui_source_dir`
   - documented retry policy and non-retry precondition behavior

## Validation

- Reviewed workflow syntax and key branches:
  - precondition failure path (`exit 6`)
  - replay run and run_dir extraction
  - retry branch for `2/3` only
  - artifact upload path
- Replay script and evidence chain already validated by prior non-interactive successful run:
  - `artifacts/qa-phase4-m2-harden-20260403-083818/`

## M3 admission view

- CI secrets supply path is now explicit:
  - `WORLDLINE_QA_ADMIN_TOKEN`
  - `WORLDLINE_QA_USER_TOKEN`
- Replay is automation-ready with clear failure typing and artifact retention.
- Unique blocker can now be read from:
  - `00-run-metadata.json`
  - `02-main-blocker.json`
  - `99-evidence-summary.md`

## Phase judgment

- Current phase: `Phase 4b M3 admission preparation complete`
- Readiness for next phase: `ready to execute formal M3 admission replay in CI`
- Main remaining gap before advancing:
  - run one full CI replay with real secrets and retain artifact as the admission evidence of record
