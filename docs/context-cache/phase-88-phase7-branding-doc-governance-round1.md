# Phase 88 - Phase 7 Branding and Documentation Governance Round 1

## Summary
- 已将 Phase 7-10 重排后的总计划保存为 `docs/context-cache/phase-87-phase7-10-reordered-master-plan.md`，作为当前阶段宗旨文档。
- Phase 7 本轮主线已落地到活跃仓库：活跃源码、配置、构建、测试、主文档中的 legacy brand tokens 已退出主阅读面与活跃命名面。
- Worldline canonical naming 已冻结并落实到活跃构建面：Python package 为 `worldline`，Web package 为 `worldline-web`，Docker image 为 `worldline-api` / `worldline-web`，默认数据库为 `worldline_know`。
- 文档体系已完成第一轮压缩：早期编号文档与旧 context-cache 已归入 `docs/archive/legacy/` 和 `docs/archive/context-cache/`；当前 `docs/context-cache/` 只保留最近基线与当前阶段计划。
- `AGENTS.md` 保持长期稳定规则，`CODEX_WORKFLOW.md` 承担执行流程、验证门槛与 MCP/skill 触发规则，职责已分离。

## Actual Subagent Decomposition
本轮实际采用了子代理分波执行：
- 第一波只读映射：
  - `system_mapper`
    - 盘点 legacy brand token 活跃残留，区分源码、配置、构建、测试、文档与历史 evidence。
    - 明确历史证据不改写，只退出主阅读面。
  - `qa_release_auditor`
    - 给出 Phase 7 最小验收矩阵，核心包含 active-surface grep gate、docs/build、web build、system info/health 与 `/themes` `/worldline` `/agent` `/graph` 入口验证。
- 第二波实现：
  - `backend_worker`
    - 处理 env、docker、默认 DB 名、日志命名、server/src/scripts/test 的 Worldline 命名切换与兼容读取。
  - `knowledge_rag_engineer`
    - 处理 `src/knowledge/**` 的 delimiter、URL whitelist、默认 DB 名等知识层遗留命名。
  - `agent_architect`
    - 收敛 `AGENTS.md` / `CODEX_WORKFLOW.md` 的职责边界。
- `frontend_worker` 在执行中断开，但其目标范围内的前端与主文档品牌切换已由主控在工作树中完成并验证。
- `product_architect` 的最终边界冻结由主控综合既有输出完成：canonical naming、文档分层和历史 evidence 策略已固定。

## Scope Landed
### Naming and compatibility
- `WORLDLINE_*` 成为活跃环境变量前缀；活跃代码优先读取 canonical 变量。
- 对旧前缀保留一轮兼容回退，但通过动态拼接 legacy key 的方式避免继续在活跃面暴露旧品牌字符串。
- 活跃构建与运行命名已切换为 Worldline：包名、镜像名、默认数据库名、日志前缀、知识层内部常量全部统一。

### Documentation governance
- 早期编号文档从 `docs/` 主阅读面移出，集中归档到 `docs/archive/legacy/`。
- 旧 `docs/context-cache/*.md` 从活跃 cache 面移出，集中归档到 `docs/archive/context-cache/`。
- 当前活跃文档面收敛为：
  - `README.md`
  - `docs/index.md`
  - `docs/platform-architecture.md`
  - `docs/frontend-architecture.md`
  - `docs/backend-architecture.md`
  - `docs/module-extension.md`
  - `docs/operations-and-validation.md`
  - `AGENTS.md`
  - `CODEX_WORKFLOW.md`
- 当前 `docs/` 下共有 131 个 Markdown 文件，但活跃架构文档面已压缩到 6 个 `docs/*.md` 主文档；归档与 evidence 不再作为主阅读入口。

## Validation
已完成：
- Active-surface grep gate：
  - `git grep -n -I -E "Y[U]XI|y[u]xi" -- . ":(exclude)docs/archive/**" ":(exclude)docs/context-cache/**" ":(exclude)artifacts/**" ":(exclude)uv.lock" ":(exclude)node_modules/**" ":(exclude).git/**" ":(exclude).playwright-cli/**"`
  - 结果：无输出。
- Python 语法检查：
  - `python -m compileall server src scripts test`
- Frontend build：
  - `pnpm --dir web build`
- Docs build：
  - `npm run docs:build`
- Runtime API smoke：
  - `http://127.0.0.1:5050/api/system/info`
  - `http://127.0.0.1:5050/api/system/health`
- Playwright MCP 浏览器 smoke：
  - `/themes`
  - `/worldline`
  - `/agent`（登录重定向正常）
  - `/graph`（登录重定向正常）

## Remaining Risks
- 当前正在运行的本地 Docker 容器仍来自改名前的旧镜像标签；配置文件已切换为 `worldline-*`，但尚未做一轮基于新命名的容器重建验证。
- `docker-compose.prod.yml` 的完整配置校验仍受本地缺失 `.env.prod` 限制，生产侧 compose 路径尚未在本轮完全闭环。
- 历史归档内容保留原始事实记录，归档目录中仍会存在旧品牌字符串；这是审计保真要求，不是活跃面回退。

## Phase Judgment
- current phase: `Phase 7`
- readiness for next phase: `almost ready for Phase 8`
- main remaining gap: `需要补一轮基于新 compose/image naming 的容器重建或配置闭环验证，证明 Worldline 命名切换在本地运行面也完全落地`
