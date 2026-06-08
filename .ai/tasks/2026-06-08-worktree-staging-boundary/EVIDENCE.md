# P2-4 证据

日期：2026-06-08

## 当前状态

命令：`git status --short --branch`

- 分支：`codex/worldline-recovery-refactor`
- status 入口总数：190
- 已跟踪修改：69
- 已跟踪删除：33
- 未跟踪入口：88

顶层分布：

| 顶层路径 | status 入口数 |
|---|---:|
| `.ai` | 118 |
| `web` | 36 |
| `test` | 11 |
| `src` | 9 |
| `server` | 6 |
| `docs` | 3 |
| `docker` / `docker-compose*` | 3 |
| `AGENTS.md` | 1 |
| `README.md` | 1 |
| `uv.lock` | 1 |

## 未跟踪文件

命令：`git ls-files --others --exclude-standard`

- 未跟踪文件总数：621
- 未跟踪任务目录：75

未跟踪路径桶：

| 路径桶 | 文件数 | 示例 |
|---|---:|---|
| 2026-06-04 至 2026-06-06 Agent/run 任务证据 | 382 | `.ai/tasks/2026-06-04-agent-artifact-rail/...` |
| 2026-06-08 当前目标任务证据 | 119 | `.ai/tasks/2026-06-08-agent-run-directory-audit/...` |
| 2026-06-07 前端/数据库/Dashboard 任务证据 | 54 | `.ai/tasks/2026-06-07-database-query-params-linkage/...` |
| 其他任务证据 | 53 | `.ai/tasks/2026-06-03-home-theme-auth-fix/...` |
| 新增后端 router | 1 | `server/routers/worldline_run_router.py` |
| 新增后端 service | 2 | `src/services/theme_module_contract.py`, `src/services/worldline_run_ledger_service.py` |
| 新增测试 | 5 | `test/test_worldline_run_ledger_service.py` 等 |
| 新增前端文件 | 4 | `web/src/views/worldline/WorldlineAgentWorkbenchView.vue` 等 |
| 新增脚本 | 1 | `scripts/ensure_superadmin.py` |

## 已跟踪 diff 分组

命令：`git diff --name-status`

| 路径桶 | 数量 | 状态 |
|---|---:|---|
| backend routers | 5 | `M:5` |
| backend services | 3 | `M:3` |
| knowledge pipeline | 2 | `M:2` |
| MCP contract | 1 | `M:1` |
| tests | 5 | `M:4, D:1` |
| frontend | 32 | `M:31, D:1` |
| docs | 3 | `M:3` |
| root docs | 2 | `M:2` |
| Docker/runtime | 3 | `M:3` |
| dependency lock | 1 | `M:1` |
| tracked task docs | 12 | `M:12` |
| old phase task deleted | 31 | `D:31` |
| other | 1 | `M:1` |

说明：`test/api/test_unified_graph_router.py` 在 `git status` 中显示 `M`，但 `git diff --name-status -- test/api/test_unified_graph_router.py` 没有文本 diff，只输出 CRLF/LF warning。后续 stage 前应单独复核，避免把纯换行状态混入功能提交。

## 不应直接执行

不要执行：

```powershell
git add .
git commit -am "..."
```

原因：会混入旧阶段删除、任务证据、业务代码、Docker/lock 修改和 line-ending-only 状态。
