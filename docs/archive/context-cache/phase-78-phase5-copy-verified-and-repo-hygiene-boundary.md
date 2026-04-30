# Phase 78 - Phase 5 Copy Verified And Repo Hygiene Boundary

## Summary

Phase 5 round 5 started from a suspected “shared-page Chinese mojibake” problem.
That suspicion was verified and narrowed:

1. The shared Vue files are UTF-8 and render normal Chinese source text.
2. The visible mojibake seen in terminal reads was a shell display issue, not a page-source corruption issue.
3. The real remaining work for this round is repo/docs hygiene tightening, not shared-page logic or wording repair.

## Subagent Decomposition

Read-only wave actually used:

1. `system_mapper`
   - rescanned `AgentView.vue`, `ThemeDetailView.vue`, `GraphView.vue`
   - confirmed the next architectural target is not PoE field coupling anymore
   - judged that shared-page logic branches can stay, and only text-layer cleanup would be worth touching if source text were actually broken

2. `product_architect`
   - confirmed shared pages should continue reading wording and semantics from facade view-models
   - judged that archive is still slightly overexposed in docs entry surfaces and should be demoted further

3. `qa_release_auditor`
   - defined minimum validation and repo-hygiene boundaries
   - separated authoritative evidence from disposable smoke output

4. `backend_worker`
   - confirmed no backend change is required for this round

5. `frontend_worker`
   - was assigned for read-only review but did not return in time
   - controller completed the final implementation judgment locally after encoding verification

## Verified Findings

Encoding verification was done directly against:

- `web/src/views/AgentView.vue`
- `web/src/views/themes/ThemeDetailView.vue`
- `web/src/views/GraphView.vue`
- `docs/archive/index.md`

Result:

- all four files decode as UTF-8 successfully
- the source text is normal Chinese when read with UTF-8
- no shared-page source rewrite was required for mojibake repair

## Changes

Changed files:

- `.gitignore`
- `docs/index.md`
- `docs/operations-and-validation.md`

Stable outcome:

- repo noise rules now explicitly ignore:
  - `.playwright-cli/`
  - `test-results/`
  - temporary `artifacts/_tmp-*`
  - precondition smoke artifacts
  - disposable playwright smoke artifacts
- docs homepage no longer promotes archive as the main secondary CTA
- operations/validation doc now records which evidence must be kept and which transient output should stay outside version focus

## Validation

Validated successfully:

```powershell
pnpm --dir D:\worldline\web build
npm --prefix D:\worldline run docs:build
```

Route preview checks passed:

```powershell
http://127.0.0.1:4173/agent  -> 200
http://127.0.0.1:4173/graph  -> 200
http://127.0.0.1:4173/themes -> 200
```

Additional judgment:

- shared Vue files are not source-level mojibake
- backend remains unchanged
- authoritative `artifacts/qa-*` evidence is still preserved as a repository-side asset class

## Remaining Risk

Still not closed:

- large frontend build chunk warnings
- general repo documentation/history volume is still high even after entry tightening
- if future terminal-side inspections continue to rely on a mismatched shell encoding, the same false mojibake alarm may reappear

## Phase Judgment

- current phase: `Phase 5 / repo-doc hygiene and final quality tightening`
- readiness for next phase: `not ready yet`
- main remaining gap before advancing:
  - final pass on docs/history volume and frontend build-size hygiene
