# P3-5 Governance Report Design

## Backend Report

`src/services/mcp_service.py` remains the source of truth for built-in MCP defaults. The governance report is extended with compatible optional keys:

- `review_checklist`
- `disabled_tool_policy`
- `connector_policy`
- `rollback_checklist`

The existing `status`, `policy`, `servers`, `violations`, and `warnings` shape is preserved.

## Release Gate

`WorldlineReleaseGateService._mcp_checks()` returns three required checks:

- `mcp_default_governance`
- `mcp_disabled_tool_policy`
- `connector_rollback_policy`

The static gate checks source fragments so fixture-based regression tests can validate the contract without requiring live connector access.

## Rollback

This slice is code/docs only. Rollback is a git revert of the touched files. If future tasks use an external connector, the report requires evidence for secret removal, remote authorization revocation, and remote draft cleanup.
