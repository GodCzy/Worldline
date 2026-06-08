# Evidence

## 2026-06-05

- `git diff --check -- src/services/worldline_agent_workflow_service.py src/mcp/worldline_server.py test/test_worldline_run_ledger_service.py test/test_worldline_live_services.py .ai/tasks/2026-06-05-agent-replay-artifact-mcp-read`
  - Result: no whitespace error output.
  - Note: Git reported existing line-ending normalization warning for `src/mcp/worldline_server.py`: `CRLF will be replaced by LF the next time Git touches it`.
- `wsl -d Debian -- bash -lc "cd /mnt/d/dev/Worldline && .venv/bin/python -m pytest test/test_worldline_run_ledger_service.py test/test_worldline_live_services.py::test_worldline_manifest_and_workflow_plan"`
  - Result: passed; 4 tests passed in 161.56s.
  - Coverage: run ledger artifact registry, read-only MCP artifact inspection service, manifest contract.
  - Notes: existing SQLAlchemy/Pydantic/requests dependency warnings remain.
- `wsl -d Debian -- bash -lc "cd /mnt/d/dev/Worldline && .venv/bin/python -m pytest test/test_worldline_phase6_7_release_gate.py"`
  - Result: passed; 3 tests passed in 100.43s.
  - Coverage: MCP defaults remain controlled and static release gate still accepts the manifest.

## Key Assertions

- Manifest contains `worldline.inspect_run_artifacts`.
- The tool has `write_scope: none` and `dispatch_backend: inline`.
- The input schema includes optional `audit_db_id`.
- `WorldlineAgentWorkflowService.inspect_run_artifacts()` returns logical `worldline-run-ledger://...` artifact URIs and omits full content unless `include_content=true`.
- Without `audit_db_id`, the service returns `audit.recorded=false` instead of writing to a fake knowledge-base id.
