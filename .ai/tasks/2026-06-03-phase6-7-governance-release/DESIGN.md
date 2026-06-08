# Design

Date: 2026-06-03

## Phase 6 Governance

The application uses a strict default MCP stance:

- `worldline`: enabled by default.
- `sequentialthinking`: conditional, disabled by default.
- `mcp-server-chart`: conditional, disabled by default.
- Database write MCP, unrestricted filesystem MCP, shell MCP, Docker/Kubernetes admin MCP, and external communication write MCP are not defaults.

`WorldlineAgentWorkflowService.tool_manifest()` defines:

- Controlled MCP server metadata.
- Admin-required write tools.
- Audit table.
- Subagent governance lanes.

## Subagent Lanes

- `research_reviewer`: read-only research and review.
- `knowledge_operator`: controlled Worldline service-boundary writes.
- `frontend_qa`: localhost Browser/Playwright screenshot QA.
- `release_auditor`: deterministic release gates and evidence recording.

Only one main writer edits project files at a time.

## Phase 7 Release Gate

`WorldlineReleaseGateService` is a static project readiness gate.

It checks:

- Required docs.
- Required task evidence directories.
- Local Codex Worldline skills.
- MCP governance report.
- Worldline manifest contract.
- Current Worldline UI screenshot report coverage.

`scripts/worldline_phase6_7_release_gate.py` writes a JSON report into this task directory.

## Data And API Impact

- No database schema change.
- No breaking route change.
- No MCP tool removal.
- Default MCP enablement changes only apply to built-in system configs still owned by `system`.
