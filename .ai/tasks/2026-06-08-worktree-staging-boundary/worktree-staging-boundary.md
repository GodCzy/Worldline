# Worldline 工作树分组与提交边界

日期：2026-06-08

## 总览

当前分支是 `codex/worldline-recovery-refactor`。工作树仍然很脏，但已经可以按功能域拆分。当前不要直接 `git add .`。

当前状态规模：

- 190 个 `git status --short` 入口。
- 69 个已跟踪修改。
- 33 个已跟踪删除。
- 88 个未跟踪入口。
- 实际未跟踪文件 621 个，其中 75 个未跟踪 `.ai/tasks` 任务目录。

## 推荐提交顺序

### 1. 工程事实源与重启文档

用途：单独固定 Worldline 重启后的事实源、项目身份和文档入口。

建议路径：

```powershell
git add -- AGENTS.md README.md docs/architecture/evaluation-gates.md docs/architecture/worldline-ui.md docs/product/public-demo.md
git add -- .ai/tasks/2026-06-03-worldline-reset .ai/tasks/2026-06-03-worldline-frontier-stack
```

复核点：

- 确认这些修改没有恢复旧 PoE/demo 事实源。
- 确认 `D:\dev\Worldline` 仍是活跃工程根。

### 2. Docker/runtime 配置

用途：容器、API compose、镜像构建相关变更独立审查。

建议路径：

```powershell
git add -- docker-compose.yml docker-compose.override.yml docker/api.Dockerfile uv.lock
```

复核点：

- `uv.lock` 应确认确实来自依赖变更，而不是环境噪音。
- Docker 配置应运行 `docker compose config`。

### 3. Run Ledger 与 router lazy import 后端闭环

用途：P0/P1 Run Ledger、router import 超时修复、Agent Workbench 真实后端能力。

建议路径：

```powershell
git add -- server/routers/__init__.py server/routers/chat_router.py server/routers/worldline_run_router.py
git add -- src/services/worldline_run_ledger_service.py src/services/worldline_agent_workflow_service.py
git add -- test/test_worldline_run_ledger_service.py test/test_worldline_run_audit_contract.py scripts/ensure_superadmin.py
git add -- .ai/tasks/2026-06-08-router-lazy-import-run-ledger .ai/tasks/2026-06-08-agent-run-ledger-audit-contract .ai/tasks/2026-06-08-agent-workbench-real-e2e
```

复核点：

- 运行 focused pytest。
- 确认临时管理员脚本没有写入账号密码。

### 4. Knowledge/Graph/Theme/Query Params 后端合约

用途：P1-3、P2-1 和主题模块闭环相关后端链路。

建议路径：

```powershell
git add -- server/routers/graph_router.py server/routers/knowledge_router.py server/routers/system_router.py
git add -- src/__init__.py src/knowledge/__init__.py src/knowledge/manager.py src/services/theme_module_contract.py
git add -- test/api/test_knowledge_router.py test/test_graph_router_adapter.py test/test_theme_module_contract.py test/test_worldline_live_services.py
git add -- .ai/tasks/2026-06-08-graph-backend-data-chain .ai/tasks/2026-06-08-theme-module-closure .ai/tasks/2026-06-08-content-kb-full-chain .ai/tasks/2026-06-08-upload-parse-query-params-linkage
```

复核点：

- Query params 的持久源应仍是 Postgres `knowledge_bases.query_params.options`。
- 主题模块 contract 应兼容旧 metadata。

### 5. MCP/Quality Gate/Release 相关后端

用途：MCP 审计、quality gate、release gate 服务独立审查。

建议路径：

```powershell
git add -- src/mcp/worldline_server.py src/services/worldline_release_gate_service.py src/services/worldline_workbench_service.py
git add -- test/test_worldline_phase6_7_release_gate.py test/test_kb_minio_cleanup.py
git add -- .ai/tasks/2026-06-03-phase6-7-governance-release
```

复核点：

- 外部 Agent 写入必须仍走受控接口和审计边界。
- 不把 MCP 治理写成不受控数据库直写。

### 6. 前端工作台、Dashboard、Database、Graph、主题与全站 QA

用途：前端 UX、紧凑化弹窗/抽屉、Dashboard 深色统一、全站截图 QA。

建议路径：

```powershell
git add -- web/src/apis/system_api.js web/src/apis/worldline_api.js
git add -- web/src/assets/css/extensions.less web/src/assets/css/worldline-design.css
git add -- web/src/components/AgentChatComponent.vue web/src/components/GraphCanvas.vue web/src/components/KnowledgeGraphSection.vue web/src/components/SearchConfigModal.vue web/src/components/StatusBar.vue web/src/components/UserInfoComponent.vue
git add -- web/src/components/dashboard/CallStatsComponent.vue
git add -- web/src/components/worldline/WorldlineBranchDetailPanel.vue web/src/components/worldline/WorldlineEvidenceRail.vue web/src/components/worldline/WorldlineGraphFocusPanel.vue web/src/components/worldline/WorldlineTimelineScrubber.vue web/src/components/worldline/WorldlineLiveOpsPanel.vue
git add -- web/src/data/worldline/index.js web/src/data/worldline/agentWorkbench.js web/src/utils/worldlineCapabilities.js
git add -- web/src/layouts/AppLayout.vue web/src/router/index.js web/src/stores/info.js web/src/stores/theme.js web/src/stores/themeContext.js
git add -- web/src/views/DashboardView.vue web/src/views/DataBaseView.vue web/src/views/ExtensionsView.vue web/src/views/GraphView.vue web/src/views/HomeView.vue
git add -- web/src/views/themes/ThemeDetailView.vue web/src/views/themes/ThemeHubView.vue
git add -- web/src/views/worldline/WorldlineHubView.vue web/src/views/worldline/WorldlineWorkbenchView.vue web/src/views/worldline/WorldlineAgentWorkbenchView.vue
git add -- web/vite.config.js
git add -- .ai/tasks/2026-06-07-agent-workbench-compact-detail-drawer .ai/tasks/2026-06-07-dashboard-dark-unification .ai/tasks/2026-06-07-database-create-backend-capabilities .ai/tasks/2026-06-07-database-query-params-linkage .ai/tasks/2026-06-07-knowledge-graph-state-ux .ai/tasks/2026-06-07-navigation-capability-visibility .ai/tasks/2026-06-07-theme-module-capability-console .ai/tasks/2026-06-07-vite-api-proxy-local-default
git add -- .ai/tasks/2026-06-08-database-create-compact-modal .ai/tasks/2026-06-08-dashboard-admin-real-qa .ai/tasks/2026-06-08-full-site-ui-qa
```

复核点：

- 运行 `pnpm --dir web build`。
- 保留 `/dashboard` 未登录跳转事实，不伪造管理员截图。
- 移动端 390px 不应出现页面级横向溢出。

### 7. Agent/run 历史任务证据

用途：把 2026-06-04 至 2026-06-06 Agent/run 任务证据作为独立证据提交，不与功能代码混在一起。

建议路径：

```powershell
git add -- .ai/tasks/2026-06-04-agent* .ai/tasks/2026-06-05-agent* .ai/tasks/2026-06-06-agent*
git add -- .ai/tasks/2026-06-08-agent-run-directory-audit
```

复核点：

- 参考 `D:\dev\Worldline\.ai\tasks\2026-06-08-agent-run-directory-audit\agent-run-directory-audit.md`。
- 不把 mocked/frontend-only 证据描述成真实后端能力。

### 8. P2 清理与规划证据

用途：收尾证据独立提交。

建议路径：

```powershell
git add -- .ai/tasks/2026-06-08-temp-qa-artifact-cleanup .ai/tasks/2026-06-08-worktree-staging-boundary
```

等 P2-5 完成后再补：

```powershell
git add -- .ai/tasks/2026-06-08-product-planning-upgrade
```

### 9. 旧阶段删除

用途：明确删除旧 phase 证据和旧 preview 数据。

建议路径：

```powershell
git add -- .ai/tasks/2026-06-03-frontend-style-unification .ai/tasks/2026-06-03-phase5-worldline-ui
git add -- web/src/data/worldline/phase5Preview.js test/test_worldline_phase5_7_services.py
```

复核点：

- 必须单独提交或至少单独 staged review。
- 删除语义应写清楚：旧 phase preview 被新 Worldline/Agent/QA 证据替代。

## 风险路径

这些路径后续 stage 前应逐项确认：

- `uv.lock`：确认不是工具刷新造成的无关锁文件变化。
- `docker-compose.yml`、`docker-compose.override.yml`、`docker/api.Dockerfile`：确认容器配置变更必要。
- `test/api/test_unified_graph_router.py`：`git status` 显示 `M`，但文本 diff 为空，仅有 CRLF/LF warning，应避免混入功能提交。
- `.ai/tasks/2026-06-03-frontend-style-unification` 与 `.ai/tasks/2026-06-03-phase5-worldline-ui`：旧阶段删除必须单独说明。

## 后续 stage 检查模板

每次只 stage 一个包：

```powershell
git status --short -- <paths>
git add -- <paths>
git diff --cached --name-status
git diff --cached --check
```

如果发现 staged 内容跨包，先用非破坏性方式取消暂存对应路径：

```powershell
git restore --staged -- <path>
```

不要使用 `git reset --hard` 或 `git checkout --`。
