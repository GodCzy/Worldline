# Agent Ledger Dossier Contract Evidence

更新时间：2026-06-04

## 代码验证

- `wsl -d Debian -- bash -lc "cd /mnt/d/dev/Worldline && python3 -m py_compile src/services/worldline_run_ledger_service.py test/test_worldline_run_ledger_service.py"`：通过。
- `wsl -d Debian -- bash -lc "cd /mnt/d/dev/Worldline && python3 -m py_compile server/routers/worldline_run_router.py"`：通过。
- `wsl -d Debian -- bash -lc "cd /mnt/d/dev/Worldline && git diff --check -- src/services/worldline_run_ledger_service.py test/test_worldline_run_ledger_service.py web/src/views/worldline/WorldlineAgentWorkbenchView.vue web/src/data/worldline/agentWorkbench.js"`：通过。
- `wsl -d Debian -- bash -lc "cd /mnt/d/dev/Worldline/web && npm run build"`：通过，Vite 构建完成；仍有既有 large chunk warning。
- `wsl -d Debian -- bash -lc "cd /mnt/d/dev/Worldline && docker compose config --quiet"`：通过。

## 后端服务冒烟

- 使用系统 Python 注入轻量 `aiofiles` / `src.config` 替身，加载 `src/services/worldline_run_ledger_service.py` 并执行 `create_run` / `approve_branch`。
- 结果：`run.created` summary 包含 `requiredPermissions`、`gateResultIds`、`artifactIds`、`toolDetails`、`gateDetails`、`artifactDetails`。
- 结果：`branch.approved` summary 输出 `branch_gate_ids=["gate-permission"]`，`branch_artifact_ids=["artifact-plan", "artifact-tool-log"]`。

## 浏览器验证

- 页面：`http://127.0.0.1:5173/worldline/agent`。
- 事件列表：4 条 preview events。
- Link chips：已出现 `Gate 4`、`Artifact 4`，并保留 Evidence / Tool / Timeline / Permission / Run Evidence。
- Artifact token：点击 `artifact-workflow-plan` 后显示 Focus Dossier，标题 `Workflow plan`，badge `json`，包含 `Artifact ID`、`Path`、`Tool Call`、`Branch`。
- Gate token：点击 `gate-permission` 后显示 Focus Dossier，标题 `Permission risk`，badge `review`，并高亮 `Permission risk` gate 卡片。
- 截图：
  - `D:\dev\Worldline\.ai\tasks\2026-06-04-agent-ledger-dossier-contract\screenshots\agent-artifact-dossier.png`
  - `D:\dev\Worldline\.ai\tasks\2026-06-04-agent-ledger-dossier-contract\screenshots\agent-dossier-gate.png`

## 受限验证

- `uv run --group test pytest test/test_worldline_run_ledger_service.py`：未完成。WSL 新 `.venv` 需要下载依赖，清华 PyPI 镜像两次出现 TLS handshake EOF，失败项分别为 `grpcio-tools==1.78.0` 和 `sympy==1.14.0`。
- `uv run --no-sync --group test pytest test/test_worldline_run_ledger_service.py`：未完成。当前 `.venv` 未同步完整，`pytest` 不存在。
- `uv run --default-index https://pypi.org/simple --group test pytest test/test_worldline_run_ledger_service.py`：未完成。官方 PyPI 重试 304 秒超时，未产出 pytest 结果。
- Browser 插件当前不支持 `tab.playwright.setViewportSize`，未能切换到 390px 视口；在当前 1280px 视口下检查 `documentElement.scrollWidth`，无横向溢出。
