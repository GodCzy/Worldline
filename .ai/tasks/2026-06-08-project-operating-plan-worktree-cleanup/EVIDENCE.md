# Evidence

日期：2026-06-08

## 初始事实源

- 活跃根目录：`D:\dev\Worldline`
- 分支：`codex/worldline-recovery-refactor`
- 事实源：`AGENTS.md`、`README.md`、`docs/index.md`
- 当前定位：Evidence-backed LLM Wiki + Temporal Knowledge Graph OS

## 初始 git 状态

命令：`git status --short --branch`

结果摘要：

- 分支：`codex/worldline-recovery-refactor`
- 工作树包含已跟踪修改、已跟踪删除和大量未跟踪 `.ai/tasks` 证据目录。
- 不能直接 `git add .`。

## Skills

本任务使用/对齐：

- `worldline-orient`
- `worldline-eval-release`
- `worldline-mcp-governance`
- `worldline-knowledge-pipeline`
- `worldline-frontend-workbench`

## 子代理

- 规划/工作流文档缺口审查子代理：只读。
- 工作树清理与提交边界审查子代理：只读。

## 子代理结果摘要

规划审查子代理结论：

- 已有 P3 路线图基本满足目标。
- 缺口是路线图没有进入核心入口文档，且多子代理、skills、MCP、Browser、GitHub 的使用缺少执行矩阵。
- 建议更新 `docs/index.md`、`README.md`、`AGENTS.md`、`docs/product/worldline-project-book.md`、`docs/architecture/mcp-skill-governance.md`、`docs/architecture/evaluation-gates.md`。

工作树审查子代理结论：

- `.ai/tasks` 中多数未跟踪文件是有效任务证据，不应当当作垃圾删除。
- 可清理候选主要是 ignored 的 `__pycache__`、`.pytest_cache`、临时 logs 和 build output。
- 不要 blanket 使用 `git clean -fdX`，因为 ignored 路径包含 `.env`、`docker/volumes/`、`models/`、`saves/` 等高风险路径。
- 推荐按 8 个 logical commit 包显式 stage，不要 `git add .`。

## 文档落点

新增：

- `docs/product/worldline-next-roadmap.md`
- `docs/architecture/agent-operating-workflow.md`

更新：

- `docs/index.md`
- `AGENTS.md`
- `README.md`
- `docs/product/worldline-project-book.md`
- `docs/architecture/mcp-skill-governance.md`
- `docs/architecture/evaluation-gates.md`

## 敏感内容扫描

命令范围：当前 tracked diff 和 untracked 文本文件。

结果：

- 检查文本文件：537。
- 常见 API key、GitHub token、AWS key、private key、明显 password assignment 命中：0。
- 路径级 `token` 命中来自 `agent-event-token-drilldown` 任务名，不是凭据。

## 可再生产物清理

删除前逐项解析路径并限制范围：

- `.ai/tasks/**/__pycache__`
- 根 `.pytest_cache`

实际删除：

- `.ai/tasks/2026-06-08-agent-workbench-real-e2e/__pycache__`：2 文件，19518 字节。
- `.ai/tasks/2026-06-08-content-kb-full-chain/__pycache__`：3 文件，32536 字节。
- `.ai/tasks/2026-06-08-dashboard-admin-real-qa/__pycache__`：2 文件，9301 字节。
- `.ai/tasks/2026-06-08-upload-parse-query-params-linkage/__pycache__`：1 文件，10963 字节。
- `.pytest_cache`：5 文件，4069 字节。

没有删除 `.env`、`docker/volumes/`、`models/`、`saves/`、`node_modules`、`.venv` 或任务截图证据。

验证后再次清理：

- 删除 `docs/.vitepress/dist`：57 文件，1362885 字节。
- 删除 `web/dist`：77 文件，6060815 字节。
- 删除重新生成的 `.pytest_cache`：5 文件，2196 字节。
- 删除仓库内非 `.venv` / `node_modules` 的 `__pycache__`：38 个目录。
- 删除 ignored 任务日志：10 个文件，13702 字节。

复核：

- 仓库内非 `.venv` / `node_modules` 的 `__pycache__` 目录：0。
- `git clean -ndX` 剩余高风险/本地环境目录包括 `.env`、`.venv`、`docker/volumes/`、`models/`、`node_modules/`、`saves/`、`web/node_modules/`，未自动删除。

## 验证命令

- `git diff --check`：通过，无 whitespace error；仅有既有 CRLF/LF warning。
- `wsl -d Debian -- bash -lc 'cd /mnt/d/dev/Worldline && docker compose config >/tmp/worldline-compose-config.out && echo docker-compose-config-ok'`：通过。
- `wsl -d Debian -- bash -lc 'cd /mnt/d/dev/Worldline && npm run docs:build'`：通过，VitePress build complete。
- `wsl -d Debian -- bash -lc 'cd /mnt/d/dev/Worldline && PYTHONPATH=/mnt/d/dev/Worldline uv run --group test pytest test/test_worldline_run_ledger_service.py test/test_worldline_run_audit_contract.py test/test_theme_module_contract.py test/test_graph_router_adapter.py test/test_worldline_live_services.py'`：17 passed, 1 warning。
- `wsl -d Debian -- bash -lc 'cd /mnt/d/dev/Worldline && npm --prefix web run build'`：通过，Vite build complete；保留既有大 chunk warning。

说明：

- WSL 中 `pnpm` 不存在，改用 `npm --prefix web run build`。
- Windows PowerShell 中 `npm` 不在 PATH，前端构建使用 WSL 的 `/home/joy/.local/bin/npm`。

## 提交边界

本次将脏工作树按逻辑边界整理为以下提交：

- `53a95d6 docs: add Worldline roadmap and operating workflow`
- `5a54164 feat: add Worldline backend contracts`
- `f0e8015 feat: refine Worldline frontend workbench`
- `a55476a chore: update Worldline runtime and reset evidence`
- `b70c9c0 docs: add Agent run evidence archive`
- `79f6dea chore: remove superseded phase previews`

说明：

- 提交前未使用 `git add .` 进行 blanket stage。
- 旧 Phase 5 预览数据、重复截图证据和已替代测试已通过 `79f6dea` 移除。
- `test/api/test_unified_graph_router.py` 最终没有内容差异；`git status` 已清洁。

## 最终工作树复核

命令：`git status --short --branch`

结果：

```text
## codex/worldline-recovery-refactor
```

命令：`git clean -ndX`

结果摘要：

- 剩余 ignored 项仅为本地环境或高风险数据目录：`.env`、`.venv/`、`docker/volumes/`、`models/`、`node_modules/`、`saves/`、`web/node_modules/`。
- 这些目录未删除，也未入仓。

## OutputMD 总结

已写入：

- `D:\document\OutputMD\2026-06-08-Worldline-Project-Operating-Plan-Worktree-Cleanup.md`
