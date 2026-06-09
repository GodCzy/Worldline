# P3-6 Decisions

## 2026-06-09

- Use existing JSON `quality_gate_runs.failure_replay` for replay refs; no schema migration is needed.
- Keep backend additions compatible by preserving existing `check`, `observed`, `expected`, and `replay` fields.
- Keep the UI compact by rendering replay only for failed latest gates and putting intentional failure behind a small action instead of a threshold form.
