# Decisions

## Knowledge refs are read-only

`worldline.inspect_run_knowledge` only reads run ledger metadata. It does not rebuild wiki pages, update graph records, or rewrite temporal facts.

## Preserve frontend fixture shape

The workbench already has `wikiRefs`, `entityRefs`, and `timelineRefs`. The ledger stores that shape compatibly instead of defining a new domain schema.

## Use one tool for three knowledge layers

Wiki, graph, and timeline are separate `kind` values under one run-scoped read tool. This keeps the MCP manifest smaller while preserving explicit URI segments and args.
