# Evidence

日期：2026-06-08

## 初始审计

- `server/routers/worldline_run_router.py` 已提供 `/api/worldline/runs` router。
- `server/routers/__init__.py` 已注册 `worldline_runs`。
- `src/services/worldline_run_ledger_service.py` 已提供 file-backed Stage 2 ledger。
- `src/services/worldline_agent_workflow_service.py` 已提供 run artifacts/gates/evidence/knowledge/manifest inspectors，并包含 `audit_db_id` 审计路径。
- `web/src/apis/worldline_api.js` 已封装 `worldlineRunApi`。
- 子代理只读审计结论：不要重复做 Stage 1 preview；最小高价值缺口是补 `audit_db_id` 真实写审计日志的 focused test。

## 修改

- 新增 `test/test_worldline_run_audit_contract.py`：
  - 使用 SQLite `pg_manager` fixture 和临时 `KnowledgeBase`。
  - 创建 file-backed run ledger 记录和 replay artifact。
  - 调用 `inspect_run_manifest`、`inspect_run_artifacts`、`inspect_run_gates`、`inspect_run_evidence`、`inspect_run_knowledge`。
  - 每次调用都传入 `audit_db_id` 和 `actor="qa"`。
  - 断言 `worldline_mcp_audit_logs` 写入 6 条日志，其中包含 5 类 inspector 和 1 条 not_found resource read。
- 修改 `web/src/data/worldline/agentWorkbench.js`：
  - 将 `Persistent run ledger remains future work` 改为 `Persistent run ledger API is available`。
  - 将 `future_api/backend_required` 改为 `backend_api/backend_available/preview_fallback`。
  - 将显示提示改为“当前可保存到 /api/worldline/runs；未登录或后端不可用时保留本地预览。”

## 验证

### focused pytest

- 命令：`wsl -d Debian -- bash -lc 'cd /mnt/d/dev/Worldline && timeout 180s env PYTHONPATH=. WORLDLINE_SKIP_APP_INIT=1 .venv/bin/pytest test/test_worldline_run_audit_contract.py -q -vv'`
- 结果：通过。
- 摘要：`1 passed, 1 warning in 10.71s`。
- warning：SQLAlchemy `declarative_base()` deprecation warning，非本次行为失败。

### 前端 build

- 命令：`wsl -d Debian -- bash -lc 'cd /mnt/d/dev/Worldline && /home/joy/.local/bin/npm --prefix web run build'`
- 结果：通过。
- 摘要：Vite `built in 4m 17s`。
- 备注：保留既有大 chunk warning。

### 过期文案检查

- 命令：`rg -n "Persistent run ledger remains future work|future_api|backend_required|Stage 1 local ledger preview|Stage 1 Preview|Agent Workbench Stage 1" web\src\data\worldline\agentWorkbench.js`
- 结果：无匹配。

### diff check

- 命令：`git diff --check -- web/src/data/worldline/agentWorkbench.js .ai/tasks/2026-06-08-agent-run-ledger-audit-contract`
- 结果：通过。
- 备注：新增测试文件当前是未跟踪文件，语法和行为由 focused pytest 覆盖。

### 旧大测试限制

- 命令：`wsl -d Debian -- bash -lc 'cd /mnt/d/dev/Worldline && timeout 180s env PYTHONPATH=. .venv/bin/pytest test/test_worldline_run_ledger_service.py -q -vv'`
- 结果：180 秒内停在 collection 阶段，无有效测试结果。
- 命令：`wsl -d Debian -- bash -lc 'cd /mnt/d/dev/Worldline && timeout 80s env PYTHONPATH=. WORLDLINE_SKIP_APP_INIT=1 .venv/bin/pytest --collect-only test/test_worldline_run_ledger_service.py -q'`
- 结果：80 秒内无 collection summary。
- 处理：未把该旧大文件作为本阶段验收证据，改用 focused test 直接验证新增审计契约。
- 残留进程检查：`wsl -d Debian -- bash -lc 'pgrep -af pytest || true'`，无 pytest 残留。

## 子代理审计摘要

- `/api/worldline/runs` 已有 router、service、前端 API 封装和 focused tests，不应再当作尚未实现。
- 早期 Agent Workbench 本地 preview、事件时间线、artifact rail、dossier、copy MCP、selector/filter/pagination 属于 UI 表层，不应重复堆。
- 最小高价值缺口是证明 `audit_db_id` 下 run inspector 会真实写 `worldline_mcp_audit_logs`，本阶段已补。

## 后续仍未完成

- 管理员登录态下 `/agent` 或 Agent Workbench 的真实浏览器 E2E：保存 run、审批/拒绝、读取 manifest/resource、截图 QA。
- 旧 `test/test_worldline_run_ledger_service.py` collection 超时的根因仍未修复。
- Run mutation 的外部写审计仍只进入 ledger event，没有升级为 DB audit log；后续要决定是否继续保持 file-backed event，或为 mutation 增加单独审计。
- 工作树仍然非常脏，本阶段未分组提交。
