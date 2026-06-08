# Evidence

Updated: 2026-06-03

## Implementation Summary

- Tightened application MCP defaults so only `worldline` is enabled by default.
- Kept `sequentialthinking` and `mcp-server-chart` as conditional app MCP configs, disabled by default.
- Added `get_mcp_governance_report()` for deterministic Phase 6 policy checks.
- Added subagent lanes to `WorldlineAgentWorkflowService.tool_manifest()`.
- Added `WorldlineReleaseGateService` and `scripts/worldline_phase6_7_release_gate.py`.
- Added public demo documentation at `docs/product/public-demo.md`.
- Added tests for MCP governance and release gate readiness.

## Release Gate

Initial note: a first direct script attempt failed before the script was made lightweight because importing through `src` required project dependencies. The script was refactored to load the static release gate service by file path, avoiding full app initialization.

Final command:

```powershell
wsl -d Debian -- /bin/bash -lc "cd /mnt/d/dev/Worldline && python3 scripts/worldline_phase6_7_release_gate.py --output .ai/tasks/2026-06-03-phase6-7-governance-release/release-gate-report.json"
```

Result:

```json
{
  "status": "passed",
  "check_count": 6,
  "passed_count": 6,
  "failed_count": 0,
  "next_step": "ready_for_phase6_7_demo"
}
```

Report:

- `.ai/tasks/2026-06-03-phase6-7-governance-release/release-gate-report.json`

## Backend Tests

Command:

```powershell
wsl -d Debian -- /usr/bin/env UV_DEFAULT_INDEX=https://pypi.org/simple PYTHONPATH=/mnt/d/dev/Worldline WORLDLINE_SKIP_APP_INIT=1 SAVE_DIR=/tmp/worldline-release-test-save SILICONFLOW_API_KEY=dummy UV_PROJECT_ENVIRONMENT=/tmp/worldline-release-test-env /home/joy/.local/bin/uv run --no-project --with pytest --with pytest-asyncio --with sqlalchemy --with aiosqlite --with python-dotenv --with colorlog --with pydantic --with pyyaml --with tomli --with tomli-w --with httpx --with fastapi --with loguru --with aiofiles --with langchain-mcp-adapters --with mcp python -m pytest -p no:cacheprovider /mnt/d/dev/Worldline/test/test_knowledge_object_models.py /mnt/d/dev/Worldline/test/test_evidence_service.py /mnt/d/dev/Worldline/test/test_worldline_phase6_7_release_gate.py /mnt/d/dev/Worldline/test/test_worldline_live_services.py
```

Result:

- `21 passed, 1 warning in 4.72s`.
- Warning: existing SQLAlchemy `declarative_base()` deprecation warning in `src/storage/postgres/models_business.py`.

## Frontend Build

Command:

```powershell
wsl -d Debian -- /bin/bash -lc 'cd /mnt/d/dev/Worldline && rm -f .ai/tasks/2026-06-03-phase6-7-governance-release/web-build.log && set -o pipefail && timeout 600 npm --prefix web run build 2>&1 | tee .ai/tasks/2026-06-03-phase6-7-governance-release/web-build.log'
```

Result:

- Pass in 4m52s.
- Build log: `.ai/tasks/2026-06-03-phase6-7-governance-release/web-build.log`.
- Existing large chunk warnings remained for vendor bundles.

## Docs Build

Command:

```powershell
wsl -d Debian -- /bin/bash -lc 'cd /mnt/d/dev/Worldline && npm run docs:build'
```

Result:

- Pass in 26.53s.

## Docker Compose Config

Command:

```powershell
wsl -d Debian -- /bin/bash -lc 'cd /mnt/d/dev/Worldline && docker compose config'
```

Result:

- Pass.

## Screenshot QA

Command:

```powershell
wsl -d Debian -- /bin/bash -lc 'cd /mnt/d/dev/Worldline && node .ai/tasks/2026-06-03-home-theme-auth-fix/screenshot-ui.cjs'
```

Result:

```json
{
  "reportPath": "/mnt/d/dev/Worldline/.ai/tasks/2026-06-03-home-theme-auth-fix/screenshots/ui-screenshot-report.json",
  "screenshotCount": 9,
  "failureCount": 0
}
```

Visual spot-check:

- `.ai/tasks/2026-06-03-home-theme-auth-fix/screenshots/home-1440x900.png`
- `.ai/tasks/2026-06-03-home-theme-auth-fix/screenshots/themes-1440x900.png`
- `.ai/tasks/2026-06-03-home-theme-auth-fix/screenshots/worldline-hub-1440x900.png`

## Static Checks

Commands:

```powershell
git diff --check
rg --files -g '*.md' D:\dev\Worldline D:\document\Worldline
git status --short -- uv.lock pyproject.toml package-lock.json pnpm-lock.yaml web\pnpm-lock.yaml web\package-lock.json web\package.json
wsl -d Debian -- /bin/bash -lc "ps -eo pid,comm,args | grep -E 'npm run build|vite build|vitepress build' | grep -v grep || true"
```

Results:

- `git diff --check`: no whitespace errors; Git reported a CRLF-to-LF warning for `src/services/mcp_service.py`.
- Markdown inventory stayed inside reset/current-doc boundaries.
- Lock files and package manifests had no changes.
- No leftover build process was found.

## Residual Risk

- Phase 6/7 release gate is a local deterministic readiness gate, not remote hosting or CI deployment.
- Conditional external MCPs remain disabled by default; enabling them later still requires source, license, permission, token, and rollback review.
- Screenshot QA uses deterministic preview/mocked API data for visual demo readiness. Live backend data QA should be repeated when a real knowledge base is connected.
