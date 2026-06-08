# Decisions

## API is read-only

The HTTP route is a read-only projection of the existing service manifest. It does not create runs, register artifacts, or mutate evidence.

## Service remains source of truth

The route delegates to `WorldlineAgentWorkflowService.inspect_run_manifest` so MCP and HTTP callers share one manifest contract.

## UI keeps copy path

The backend inspector adds confidence and observability but does not remove the existing MCP copy workflow, because external Agents still need an explicit tool-call handoff.
