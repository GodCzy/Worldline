# P4 Operational Health Report Evidence

## Status

Completed.

## Commands

```powershell
wsl -d Debian -- bash -lc "cd /mnt/d/dev/Worldline && uv run python -m ruff check src/services/worldline_operational_health_service.py src/services/worldline_release_gate_service.py server/routers/dashboard_router.py test/test_worldline_operational_health_service.py test/test_worldline_phase6_7_release_gate.py"
```

Result: passed.

```powershell
wsl -d Debian -- bash -lc "cd /mnt/d/dev/Worldline && PYTHONPATH=. uv run --group test pytest test/test_worldline_operational_health_service.py test/test_worldline_phase6_7_release_gate.py"
```

Result: 7 passed. Warnings were existing SQLAlchemy deprecation and requests dependency-version warnings.

```powershell
wsl -d Debian -- bash -lc "cd /mnt/d/dev/Worldline && PYTHONPATH=. uv run python scripts/worldline_phase6_7_release_gate.py > /tmp/worldline-release-gate-p4-health.json && uv run python - <<'PY'
import json
p='/tmp/worldline-release-gate-p4-health.json'
report=json.load(open(p, encoding='utf-8'))
print(report['status'])
print(report['summary'])
print([c['name'] for c in report['checks'] if 'operational' in c['name'] or c['name'].startswith('mcp') or c['name'].startswith('connector')])
PY"
```

Result: passed; summary `{'check_count': 9, 'passed_count': 9, 'failed_count': 0}`; operational check `worldline_operational_readiness_contract` passed.

```powershell
git diff --check
```

Result: passed. Git printed the existing CRLF normalization warning for `server/routers/dashboard_router.py`.

```powershell
wsl -d Debian -- bash -lc "cd /mnt/d/dev/Worldline && docker compose config >/tmp/worldline-compose-config-p4-health.txt && wc -l /tmp/worldline-compose-config-p4-health.txt"
```

Result: passed; compose config output had 473 lines.

```powershell
wsl -d Debian -- bash -lc "cd /mnt/d/dev/Worldline && npm run docs:build"
```

Result: passed; VitePress build completed.

## Artifacts

- `src/services/worldline_operational_health_service.py`
- `server/routers/dashboard_router.py`
- `test/test_worldline_operational_health_service.py`
- `docs/architecture/operational-hardening.md`
- `.ai/tasks/2026-06-03-phase6-7-governance-release/release-gate-report.json`
