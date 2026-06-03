# Evidence

Updated: 2026-06-03

## Scope

Phase 5 completed the Worldline UI workbench surface:

- `/worldline` command hub.
- `/worldline/phase5-preview` full-screen workbench.
- `/graph?theme=phase5-preview&module=phase5-preview&scene=graph_timeline&version=worldline-phase5-preview&graph=phase5-graph-focus` graph handoff surface.

## Commands

### Backend syntax

```powershell
wsl -d Debian -- /bin/bash -lc "cd /mnt/d/dev/Worldline && python3 -m py_compile src/services/worldline_workbench_service.py"
```

Result: pass.

### Focused backend tests

```powershell
wsl -d Debian -- /bin/bash -lc "cd /tmp && rm -rf /tmp/worldline-phase5-test-env /tmp/worldline-phase5-test-save && PYTHONPATH=/mnt/d/dev/Worldline WORLDLINE_SKIP_APP_INIT=1 SAVE_DIR=/tmp/worldline-phase5-test-save SILICONFLOW_API_KEY=dummy UV_PROJECT_ENVIRONMENT=/tmp/worldline-phase5-test-env uv run --no-project --with pytest --with pytest-asyncio --with sqlalchemy --with aiosqlite --with python-dotenv --with colorlog --with pydantic --with pyyaml --with tomli --with tomli-w --with httpx --with fastapi --with loguru --with aiofiles python -m pytest -p no:cacheprovider /mnt/d/dev/Worldline/test/test_knowledge_object_models.py /mnt/d/dev/Worldline/test/test_document_compiler.py /mnt/d/dev/Worldline/test/test_knowledge_object_repository.py /mnt/d/dev/Worldline/test/test_evidence_service.py /mnt/d/dev/Worldline/test/test_auto_wiki_service.py /mnt/d/dev/Worldline/test/test_worldline_phase5_7_services.py"
```

Result: `28 passed, 1 warning in 5.41s`.

### Frontend build

```powershell
wsl -d Debian -- /bin/bash -lc 'cd /mnt/d/dev/Worldline && rm -f .ai/tasks/2026-06-03-phase5-worldline-ui/web-build.log && set -o pipefail && timeout 600 npm --prefix web run build 2>&1 | tee .ai/tasks/2026-06-03-phase5-worldline-ui/web-build.log'
```

Result: pass in 5m54s. Build log saved to `.ai/tasks/2026-06-03-phase5-worldline-ui/web-build.log`.

Note: build emitted existing large chunk warnings for vendor bundles; no Phase 5 build failure.

### Docs build

```powershell
wsl -d Debian -- /bin/bash -lc 'cd /mnt/d/dev/Worldline && npm run docs:build'
```

Result: pass in 27.18s.

### Docker compose config

```powershell
wsl -d Debian -- /bin/bash -lc 'cd /mnt/d/dev/Worldline && docker compose config'
```

Result: pass.

Note: Windows-side `docker` was not available, so compose validation used WSL Docker.

### Markdown inventory

```powershell
rg --files -g '*.md' D:\dev\Worldline D:\document\Worldline
```

Result: current Markdown inventory remained within the reset/current-doc boundary.

### Screenshot QA

```powershell
wsl -d Debian -- /bin/bash -lc 'cd /mnt/d/dev/Worldline && rm -rf .ai/tasks/2026-06-03-phase5-worldline-ui/screenshots && node .ai/tasks/2026-06-03-phase5-worldline-ui/screenshot-phase5.cjs'
```

Result:

```json
{
  "reportPath": "/mnt/d/dev/Worldline/.ai/tasks/2026-06-03-phase5-worldline-ui/screenshots/phase5-screenshot-report.json",
  "screenshotCount": 9,
  "failureCount": 0
}
```

## Screenshot Artifacts

- `.ai/tasks/2026-06-03-phase5-worldline-ui/screenshots/worldline-hub-1920x1080.png`
- `.ai/tasks/2026-06-03-phase5-worldline-ui/screenshots/worldline-hub-1440x900.png`
- `.ai/tasks/2026-06-03-phase5-worldline-ui/screenshots/worldline-hub-390x844.png`
- `.ai/tasks/2026-06-03-phase5-worldline-ui/screenshots/worldline-workbench-1920x1080.png`
- `.ai/tasks/2026-06-03-phase5-worldline-ui/screenshots/worldline-workbench-1440x900.png`
- `.ai/tasks/2026-06-03-phase5-worldline-ui/screenshots/worldline-workbench-390x844.png`
- `.ai/tasks/2026-06-03-phase5-worldline-ui/screenshots/graph-1920x1080.png`
- `.ai/tasks/2026-06-03-phase5-worldline-ui/screenshots/graph-1440x900.png`
- `.ai/tasks/2026-06-03-phase5-worldline-ui/screenshots/graph-390x844.png`
- `.ai/tasks/2026-06-03-phase5-worldline-ui/screenshots/phase5-screenshot-report.json`

Manual visual check covered hub, workbench, graph, and mobile workbench screenshots. No stale error toast remained after the AgentStore route mocks were added.

## Contract Notes

- Existing `/worldline` and `/worldline/:themeId` routes remained compatible.
- `/worldline/generate` optional Phase 5 fields were added without breaking older payloads.
- Graph handoff uses route query context and does not require direct database writes from the frontend.
- RAG remains an auxiliary retrieval layer; the UI emphasizes LLM Wiki, evidence anchors, temporal graph focus, and quality gates.

## Residual Risk

- The current screenshot run uses a deterministic local preview adapter and mocked API responses. Live backend/browser QA should be repeated after Phase 6 MCP/agent orchestration is wired into real data.
- Mobile workbench keeps the wide worldline canvas inside its responsive shell; page-level horizontal overflow is absent, but a future v2 can add a compact mobile graph layout.
