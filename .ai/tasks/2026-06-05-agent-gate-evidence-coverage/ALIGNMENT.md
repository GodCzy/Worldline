# Gate Evidence Coverage Alignment

## Goal

Make Quality Gate decisions explainable inside the Agent Workbench. A reviewer should understand which branch evidence, graph entities, and temporal facts support a gate result, then jump directly to those supporting records.

## Scope

- Derive gate support from the gate branch's `evidenceIds` and `temporalFactIds`.
- Surface support counts in the Gate Run Panel.
- Add Gate Dossier metadata for evidence, graph, timeline, and support source.
- Add clickable Dossier chips from Gate to Evidence Rail evidence, graph, and timeline targets.

## Out Of Scope

- No backend API, storage, or router changes.
- No new quality gate execution logic.
- No dependency changes.
- No cleanup of unrelated reset worktree changes.

## Acceptance

- Focusing `gate-permission` shows support counts and support chips.
- `Gate -> Evidence` focuses the source EvidenceAnchor in Evidence Rail.
- `Gate -> Graph` focuses the derived Graph Entity in Evidence Rail.
- `Gate -> Time` focuses the temporal support in Evidence Rail.
- Build and screenshot QA evidence are recorded.
