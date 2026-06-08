# Decisions

## Compare is read-only

Cross-run diff is an inspection action. It must not load, mutate, approve, reject, archive, delete, or rename either run.

## ID-level diff first

The file-backed ledger can reliably compare resource IDs across run categories. Deep semantic comparison of content can be added later behind a separate evaluator.

## Selector-local panel

The diff panel lives beside the run selector so operators can decide whether to load a different run without losing current context.
