# Decisions

## Manifest is a discovery layer

`worldline.inspect_run_manifest` does not replace detailed read tools. It gives external Agents a single entry point to discover run resources and then call the detailed tools.

## Keep run-scoped and read-only

The manifest is derived from the run ledger and includes only read URI/args. It does not compile knowledge, query live databases, or write audit records unless `audit_db_id` is explicitly provided.

## Preserve existing UI surface

The front-end uses the existing Last MCP Call preview rather than adding a separate modal or new global store.
