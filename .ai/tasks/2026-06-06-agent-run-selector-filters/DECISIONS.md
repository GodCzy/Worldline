# Decisions

## Filters remain read-only

Selector filters only narrow the saved run list. Any future archive/delete/rename action must use a separate audited write contract.

## In-memory filtering first

The current run ledger is file-backed, so filtering is implemented in service memory over compact run summaries. No index or schema change is introduced.

## Compact controls

Filters live inside the existing selector panel to preserve the left rail as a dense operational surface.
