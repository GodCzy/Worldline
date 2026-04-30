# Phase 65 - Phase 4b M2.5 replay credential hardening

## Baseline

- M1 readonly QA package is already stable.
- M2 unified replay entry already exists in `scripts/qa_phase4_m2_replay.py`.
- The remaining gap before this pass was stable, reusable, non-interactive credential input for replay.

## This pass target

- Add a reusable replay manifest so CI/local can run replay without ad-hoc interactive setup.
- Keep the existing CLI/env compatibility path intact.
- Define a single main-blocker rule so every failure reports one primary blocker only.

## Landed changes

1. `scripts/qa_phase4_m2_replay.py`
   - added `--replay-manifest`
   - added manifest-first non-interactive input resolution
   - kept CLI/env/file compatibility
   - added `main_blocker` metadata and `02-main-blocker.json`
   - kept business logic untouched

2. `docs/22-phase4-m2-unified-replay.md`
   - documented manifest format
   - documented replay precedence
   - documented output contract
   - documented the unique main blocker rule

3. `.github/workflows/phase4-replay.yml`
   - added a manual CI replay path
   - creates a temp manifest from GitHub secrets
   - starts `graph` and `api` dependencies
   - archives the replay run dir as one artifact

## Validation

- `python -m py_compile scripts/qa_phase4_m2_replay.py`
- `python scripts/qa_phase4_m2_replay.py --help`
- manifest smoke confirms UTF-8 BOM JSON manifests are accepted and precondition failures emit `main_blocker`
- workflow file reviewed for failure-code mapping and artifact upload strategy

## Scope and risk

- Scope remains process hardening only.
- No route, permission, graph, or module behavior changed.
- Main residual operational risk:
  - replay still depends on externally provided admin/user credentials and a valid UI evidence directory.
  - the manifest reduces friction, but the secrets still need a stable supply path in CI/local.

## Phase judgment

- Current phase: `Phase 4b M2.5 CI replay hardening landed`
- Readiness for next phase: `ready for repeatable CI replay execution`
- Main remaining gap:
  - stable availability of `WORLDLINE_QA_ADMIN_TOKEN`, `WORLDLINE_QA_USER_TOKEN`, and a valid `ui_source_dir` artifact or path in the CI environment

- workflow now defers UI evidence validation to `qa_phase4_m2_replay.py`, so precondition failures still yield `run_dir` and `main_blocker`.
