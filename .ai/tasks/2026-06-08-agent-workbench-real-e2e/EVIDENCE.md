# Evidence

日期：2026-06-08

## 初始状态

- `http://127.0.0.1:5050/api/system/info` 返回 `success: true`。
- `http://127.0.0.1:5173/worldline/agent` 当前无法连接，Vite dev server 未运行。

## Dev Server

- 启动命令：
  `cd /mnt/d/dev/Worldline && PATH=/home/joy/.local/bin:$PATH npm --prefix web run dev -- --host 0.0.0.0 --port 5173`
- 日志：
  - `.ai/tasks/2026-06-08-agent-workbench-real-e2e/vite-dev-stdout.log`
  - `.ai/tasks/2026-06-08-agent-workbench-real-e2e/vite-dev-stderr.log`
- 验证：
  - `http://127.0.0.1:5173/worldline/agent` 返回 HTTP 200。

## 管理员准备

- 使用 `scripts/ensure_superadmin.py` 在 `api` compose 服务内创建/更新本地临时账号：`codex_temp_admin`。
- 执行环境：`docker compose exec -T -e PYTHONPATH=/app ... api python3 scripts/ensure_superadmin.py`。
- 结果：`action=updated`，`role=superadmin`，`password_verified=true`。
- 密码未写入文件或总结，仅用于本轮本地 QA。

## 真实 API E2E

- QA 脚本：`.ai/tasks/2026-06-08-agent-workbench-real-e2e/run_agent_workbench_real_e2e.py`。
- API base：`http://127.0.0.1:5050`。
- 临时 run：`codex-e2e-agent-workbench-1780914667`。
- 覆盖接口：
  - `POST /api/auth/token`
  - `POST /api/worldline/runs`
  - `POST /api/worldline/runs/{run_id}/branches/branch-tool/approve`
  - `POST /api/worldline/runs/{run_id}/branches/branch-plan/reject`
  - `POST /api/worldline/runs/{run_id}/artifacts`
  - `GET /api/worldline/runs/{run_id}`
  - `GET /api/worldline/runs?query=...&status=approved`
  - `GET /api/worldline/runs/{run_id}/events`
  - `GET /api/worldline/runs/{run_id}/manifest?include_resources=true`
  - `GET /api/worldline/runs/{run_id}/artifacts/read`
  - `GET /api/worldline/runs/{run_id}/gates`
  - `GET /api/worldline/runs/{run_id}/evidence`
  - `GET /api/worldline/runs/{run_id}/knowledge`
- 结果摘要：
  - `status=ok`
  - `admin_role=superadmin`
  - `run_status=approved`
  - `event_total=4`
  - manifest resource counts：`artifacts=1`，`gates=2`，`evidence=2`，`sources=2`，`wiki=1`，`graph=2`，`timeline=1`
  - selected artifact/gate/evidence/knowledge：`e2e-replay-export`，`gate-permission`，`ev-tool`，`entity-worldline-run`

## 浏览器 E2E

- 浏览器目标：`http://127.0.0.1:5173/worldline/agent`。
- 页面状态：
  - `保存到后端账本`、`刷新任务` 等管理员控件处于可用状态。
  - 点击 `刷新任务` 后显示 `1 个已保存任务`。
  - 后端 run 行显示：`codex-e2e-agent-workbench-1780914667 / approved / 2 分支 / 4 事件 / 1 证据`。
  - 点击 `data-run-selector-load="codex-e2e-agent-workbench-1780914667"` 后页面显示 `Active backend run: codex-e2e-agent-workbench-1780914667`。
  - 加载后端清单后显示：`11 backend resources from 5 read tools`，并列出 `worldline.inspect_run_manifest`、`worldline.inspect_run_artifacts`、`worldline.inspect_run_gates`、`worldline.inspect_run_evidence`、`worldline.inspect_run_knowledge`。
- 控制台日志：
  - 未发现 error/warning。
  - 仅有 Vite 连接日志和现有调试输出：`Condition FALSE: Persisted selected agent is valid. Keeping it.`、`config Object`。

## 截图 QA

- 桌面截图：
  `D:\dev\Worldline\.ai\tasks\2026-06-08-agent-workbench-real-e2e\screenshots\agent-workbench-real-e2e-desktop-1280x720.jpg`
- 390px 移动端截图：
  `D:\dev\Worldline\.ai\tasks\2026-06-08-agent-workbench-real-e2e\screenshots\agent-workbench-real-e2e-mobile-390x844.jpg`
- 观察结果：
  - 两张截图均非空白，可渲染。
  - 移动端 Manifest 区域未见明显文本重叠。
  - 桌面截图位于内部滚动容器的 Manifest 区域；右侧大片深色区域来自当前滚动切片中的工作区背景，不是文档宽度溢出。DOM 检查显示 `agent-workbench` 宽度约 `1092px`，`body` 宽度 `1280px`，无横向溢出。

## 清理

- 清理脚本：`.ai/tasks/2026-06-08-agent-workbench-real-e2e/cleanup_agent_workbench_real_e2e.py`。
- 通过真实 API 归档 run：
  - `run_id=codex-e2e-agent-workbench-1780914667`
  - `run_status=archived`
  - `latest_event=run.archived`
- 临时管理员清理：
  - `admin_login=codex_temp_admin`
  - 数据库记录已标记 `is_deleted=1`

## 残余说明

- Vite dev server 仍在本地运行，供后续前端 QA 继续使用。
- 本任务未整理无关脏工作树。
