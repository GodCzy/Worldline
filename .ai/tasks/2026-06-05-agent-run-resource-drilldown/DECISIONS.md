# Decisions

## Delegate to service methods

HTTP drilldown routes call existing `WorldlineAgentWorkflowService.inspect_run_*` methods so MCP and API read behavior remains consistent.

## Keep route reads admin-gated

The Agent Workbench route is public for local preview, but backend run ledger reads remain admin-only and use existing permission checks.

## Show compact JSON detail

The UI renders selected resources as compact JSON rather than building many bespoke detail components. This gives broad coverage across artifacts, gates, evidence, sources, wiki, graph, and timeline without multiplying UI surface.
