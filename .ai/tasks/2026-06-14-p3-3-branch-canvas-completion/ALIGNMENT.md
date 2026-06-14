# P3-3 Branch Canvas Completion Alignment

Date: 2026-06-14

## Goal

Complete P3-3 Worldline Branch Canvas so generated branches are comparable, evidence-bound, inspectable, and covered by focused backend plus frontend QA evidence.

## Non-Goals

- Do not change database schema.
- Do not replace the existing `/worldline/generate` payload or `worldlineStore.hydrate` contract.
- Do not introduce new frontend dependencies.
- Do not work on P4 retry, cleanup, or P5 sharing/export in this slice.

## Acceptance Evidence

- `/worldline/generate` keeps existing fields and adds branch-level `routeTrace`, `gateRefs`, `quality.hints`, and evidence-required policy data.
- Evidence-free knowledge bases do not produce default conclusion branches.
- Branch inspector shows source support, Wiki/entity/timeline refs via the rail, gate refs, route trace, and insufficient-evidence hints.
- Canvas hover/select/focus updates the inspector and remains contained on `390x844` mobile.
- Focused pytest and frontend build pass.
- Browser QA captures desktop and mobile Worldline Branch Canvas evidence when a preview server is available.

## Risk Boundary

- This slice adds optional response fields and UI readouts only.
- Existing route names, action names, and hydrate behavior must stay compatible.
