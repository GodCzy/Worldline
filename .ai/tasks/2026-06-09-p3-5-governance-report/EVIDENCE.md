# P3-5 Governance Report Evidence

## Status

Completed.

## Commands

```powershell
wsl -d Debian -- bash -lc "cd /mnt/d/dev/Worldline && uv run python -m ruff check src/services/mcp_service.py src/services/worldline_release_gate_service.py test/test_worldline_phase6_7_release_gate.py"
```

Result: passed.

```powershell
wsl -d Debian -- bash -lc "cd /mnt/d/dev/Worldline && PYTHONPATH=. uv run --group test pytest test/test_worldline_phase6_7_release_gate.py"
```

Result: 5 passed. Warnings were existing dependency/deprecation warnings from SQLAlchemy and requests dependency versions.

```powershell
wsl -d Debian -- bash -lc "cd /mnt/d/dev/Worldline && PYTHONPATH=. uv run python scripts/worldline_phase6_7_release_gate.py > /tmp/worldline-release-gate-p3-5.json && uv run python - <<'PY'
import json
p='/tmp/worldline-release-gate-p3-5.json'
report=json.load(open(p, encoding='utf-8'))
print(report['status'])
print(report['summary'])
print([c['name'] for c in report['checks'] if c['name'].startswith('mcp') or c['name'].startswith('connector')])
PY"
```

Result: passed; summary `{'check_count': 8, 'passed_count': 8, 'failed_count': 0}`; governance checks `mcp_default_governance`, `mcp_disabled_tool_policy`, `connector_rollback_policy`.

```powershell
git diff --check
```

Result: passed. Git printed the existing CRLF normalization warning for `src/services/mcp_service.py`.

```powershell
wsl -d Debian -- bash -lc "cd /mnt/d/dev/Worldline && docker compose config >/tmp/worldline-compose-config-p3-5.txt && wc -l /tmp/worldline-compose-config-p3-5.txt"
```

Result: passed; compose config output had 473 lines.

## Artifacts

- `.ai/tasks/2026-06-03-phase6-7-governance-release/release-gate-report.json`
- `docs/architecture/mcp-skill-governance.md`
- `docs/architecture/evaluation-gates.md`
- `docs/architecture/codex-plugin-inventory.md`
- `docs/product/worldline-completion-matrix.md`
