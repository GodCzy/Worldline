# Worldline Completion Matrix

更新时间：2026-06-08

本矩阵把“完成所有内容”拆成可验证的当前状态。判定以当前仓库、`.ai/tasks` 证据、OutputMD 总结和可运行验证为准；旧 `D:\document\Worldline` 只作指针，不作当前事实源。

## Status Legend

- Done：代码、测试、截图或任务证据已经覆盖当前验收。
- Verified Baseline：已有强证据，但后续阶段会继续扩展。
- Partial：已有实现或证据，但覆盖范围不足。
- Not Started：没有当前实现或证据。
- External：需要外部账号、权限、服务或用户选择。

## Current Baseline

| 区域 | 状态 | 当前证据 |
|---|---|---|
| 新建知识库紧凑化 | Done | `DataBaseView.vue`、`.ai/tasks/2026-06-08-database-create-compact-modal/EVIDENCE.md`、对应截图 QA |
| 主题模块闭环 | Done | `.ai/tasks/2026-06-08-theme-module-closure/EVIDENCE.md` |
| Agent Workbench real E2E | Done | `.ai/tasks/2026-06-08-agent-workbench-real-e2e` |
| Dashboard admin real QA | Done | `.ai/tasks/2026-06-08-dashboard-admin-real-qa` |
| 有内容知识库完整链路 | Verified Baseline | `.ai/tasks/2026-06-08-content-kb-full-chain/EVIDENCE.md` |
| 全站 UI QA | Done | `.ai/tasks/2026-06-08-full-site-ui-qa` |
| Upload/parse/query params | Done | `.ai/tasks/2026-06-08-upload-parse-query-params-linkage` |
| Graph backend first pass | Verified Baseline | `.ai/tasks/2026-06-08-graph-backend-data-chain` |
| Worktree cleanup and commits | Done | `2026-06-08-Worldline-Project-Operating-Plan-Worktree-Cleanup.md` |

## P3 Completion Matrix

| 切片 | 当前状态 | 仍需证明或实现 | 推荐插件/工具 |
|---|---|---|---|
| P3-1 Evidence-backed LLM Wiki | Verified Baseline | 进一步把 Wiki 页面作为独立阅读面暴露并做 Wiki-focused UI QA；继续扩展 stale/review workflow | Browser、OpenAI Developers 按需 |
| P3-2 Temporal Knowledge Graph | Partial | DB 级 graph/timeline 实体、关系、冲突、Neo4j projection、timeline fact 的持续回归和 UI focus | Build Web Data Visualization、Browser |
| P3-3 Worldline Branch Canvas | Partial | 分支 canvas 的 routeTrace、质量状态、证据不足提示和 mobile 交互持续回归 | Browser、Product Design、Data Visualization |
| P3-4 Agent Run Ledger And Replay | Verified Baseline | replay、pagination、artifact registry、cross-run knowledge reads 持续产品化 | GitHub、Browser |
| P3-5 MCP And Skill Governance | Partial | tool manifest governance report、禁用项 release gate、connector rollback 记录 | GitHub、OpenAI Developers |
| P3-6 Quality Gate Replay | Partial | intentional failure replay UI、failure refs 跳转到 Evidence/Wiki/Graph/Timeline/Run | Browser、Data Visualization |
| P3-7 Compact Console UX | Verified Baseline | 每次新增功能继续做 desktop + 390px screenshot QA | Browser、Product Design |

## P4 Completion Matrix

| 区域 | 当前状态 | 要完成什么 | 推荐插件/工具 |
|---|---|---|---|
| 后台任务 retry/failure evidence | Partial | parsing/indexing/wiki/graph/gate 的失败记录和重试证据 | GitHub CI、Browser |
| Source versioning and stale rebuild | Partial | source 变化触发 stale Wiki、graph/timeline rebuild queue | Browser、Spreadsheets |
| Cost/latency budgets | Not Started | KB/run/branch/gate 级预算和 Dashboard surface | Spreadsheets、Dashboard QA |
| Admin observability | Partial | queue health、failed jobs、external service unavailable surface | Browser、Data Viz |
| Data cleanup routines | Partial | temp files、deleted KBs、MinIO objects、archived artifacts cleanup | GitHub CI |

## P5 Completion Matrix

| 区域 | 当前状态 | 要完成什么 | 推荐插件/工具 |
|---|---|---|---|
| Public demo dataset | Partial | 安全数据集、可复现截图、无 secrets | Browser、Documents |
| Read-only shared branch views | Not Started | 只读世界线 branch 分享视图 | Browser、Product Design |
| Evidence bundle export | Not Started | 可导出的 evidence/replay capsule | Documents、Spreadsheets |
| GitHub PR/issue integration | External | 用户授权后接入远程项目管理 | GitHub |
| Optional ingestion tools | External | Firecrawl/Tavily 等需来源、权限、密钥评估 | MCP governance |

## Next Concrete Work

当前不再重复“新建知识库紧凑化”。下一批应按以下顺序推进：

1. P3-1 Wiki-focused vertical QA：验证 Wiki 页面阅读面、claims、citations、review、open questions、stale state。
2. P3-2 DB graph/timeline focused regression：实体、关系、冲突、projection、timeline 和前端 focus。
3. P3-6 Quality Gate Replay：制造一次可解释失败并从 UI 跳回证据链。
4. P3-5 Governance report：把本文件的插件矩阵纳入 release gate。
5. P4 operational hardening：retry、queue、cleanup、budget。

## Workflow Rule

每个切片必须有：

- 独立 `.ai/tasks/<YYYY-MM-DD-slice>/`
- 明确验收证据
- focused pytest 或 API/Browser QA
- OutputMD 总结
- 如果使用外部 connector，记录授权范围、写入对象和回滚方式
