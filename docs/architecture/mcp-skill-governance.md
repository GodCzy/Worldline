# MCP And Skill Governance

更新时间：2026-06-08

## Principle

Worldline 允许 Agent 调用工具，但不允许外部 Agent 直接写数据库。所有写入必须通过 Worldline service boundary、权限检查和审计日志。

## Recommended MCP

- `worldline`：项目内受控工具入口，默认保留。
- GitHub：只读或半自动 PR/issue/CI 协作，写入前人工确认。
- Browser/Playwright：本地 UI smoke 和截图 QA，仅允许 localhost/127.0.0.1。

## Conditional MCP

- Firecrawl：网页摄取，需要 API key、域名范围、数据外传审查。
- Context7：文档查询，只作为只读参考。
- Tavily：研究任务可用，密钥只放环境变量或官方凭据位置。
- Figma/Notion/Linear：只在明确任务需要远程设计或文档写入时启用。

## Not Default

- Postgres/Neo4j/Milvus/Redis 直连写 MCP。
- unrestricted filesystem MCP。
- shell/command MCP。
- Docker/Kubernetes 高权限 MCP。
- Slack/Email/Calendar 等外部沟通写入 MCP。

## Codex Plugin Boundary

本机 Codex 插件缓存的完整适配矩阵见 `docs/architecture/codex-plugin-inventory.md`。这些插件是工作流辅助，不是默认生产依赖：

- Browser 是 Worldline 本地路由 QA 的默认工具。
- GitHub 只用于远程 PR、issue、CI 和发布协作，远程写入前必须确认。
- Build Web Data Visualization 和 Product Design 可辅助 P3 graph、branch canvas 和 compact console QA。
- OpenAI Developers 只在 API key、Agents SDK 或 ChatGPT Apps 任务需要时启用；不得把 secrets 写入仓库。
- Vercel、Canva、Creative Production、Expo、Documents、Presentations、Spreadsheets 都是情境工具，不进入默认服务写路径。

任何会写入 `D:\dev\Worldline` 与 `D:\document\OutputMD` 之外位置的 connector 或插件，都必须在当前 `.ai/tasks` 目录记录 scope、rollback 和 evidence。

## Codex Skills

本地 Worldline skills 放在 `C:\Users\Joy\.codex\skills\worldline-*`，用于 Codex 任务执行，不等同于 Worldline 应用内 skills 管理系统。

## Review Checklist

- 来源、license、维护状态、issue/security 状态。
- 完整 command/args/env/header。
- 文件目录、网络域名、OAuth scope、toolsets、write scope。
- 是否会外传源码、文档、数据库内容、日志、密钥或个人信息。
- 禁用高风险 tools，只启用任务必需工具。
- 记录禁用、撤 token、删除配置的回滚路径。

## Phase 6 Executable Policy

- Application MCP defaults enable only `worldline`.
- `sequentialthinking` and `mcp-server-chart` remain available as conditional configs but are disabled by default.
- GitHub and Browser/Playwright are Codex-side task tools, not application MCP defaults.
- Direct database-write MCP, unrestricted filesystem MCP, shell MCP, Docker/Kubernetes admin MCP, and external communication write MCP are not default.
- `WorldlineAgentWorkflowService.tool_manifest()` declares subagent lanes for research review, knowledge operation, frontend QA, and release audit.
- All write tools remain behind the Worldline service boundary and require admin intent in the manifest.
- `scripts/worldline_phase6_7_release_gate.py` checks these defaults before public demo.

## P3-5 Governance Report Gate

`get_mcp_governance_report()` is the executable source for MCP and connector governance evidence. It must return:

- `review_checklist`: source, license, command/args/env/header, token handling, network reach, write scope, data exposure, disabled tools, and rollback review items.
- `disabled_tool_policy`: conditional servers disabled by default, high-risk tool markers, task-required enablement review, and per-server `disabled_tools` evidence.
- `connector_policy`: Browser/Playwright, GitHub, OpenAI Platform, Figma, Notion, Linear, Canva, and Vercel usage boundaries.
- `rollback_checklist`: disable conditional MCP servers, restore disabled tools, remove secrets, delete unneeded local configs, revoke remote authorization, archive/delete remote drafts, and record rollback evidence.

`WorldlineReleaseGateService` fails the release gate if these structures are removed from `src/services/mcp_service.py`. This keeps the plugin inventory in `docs/architecture/codex-plugin-inventory.md` connected to a deterministic project check instead of leaving it as a passive document.

## P3 Tool And Subagent Matrix

| Slice | Main Agent | Sidecar subagents | Local skills | MCP/tools | Write boundary | Evidence |
|---|---|---|---|---|---|---|
| P3-1 Evidence-backed Wiki | Owns backend contract, UI handoff, tests | Knowledge pipeline reviewer, release audit | `worldline-orient`, `worldline-knowledge-pipeline`, `worldline-backend-contract`, `worldline-eval-release` | Browser only if UI changes | Worldline service/repository APIs only | pytest, `EVIDENCE.md`, OutputMD |
| P3-2 Temporal KG | Owns graph/timeline service and UI focus | Knowledge graph reviewer, frontend QA | `worldline-knowledge-pipeline`, `worldline-backend-contract`, `worldline-frontend-workbench` | Browser for `/graph` and `/worldline/:themeId` QA | Postgres graph tables through services; Neo4j projection read-only | graph tests, screenshots |
| P3-3 Branch Canvas | Owns `/worldline/generate` contract and workbench UI | Frontend QA, release audit | `worldline-frontend-workbench`, `worldline-knowledge-pipeline` | Browser/Playwright local QA | Existing API payload compatibility | desktop/mobile screenshots |
| P3-4 Agent Run Ledger | Owns run ledger service, audit contract, workbench | Code explorer, release audit | `worldline-backend-contract`, `worldline-mcp-governance`, `worldline-eval-release` | Internal `worldline` MCP only | Audited Worldline service boundary | run pytest, audit records |
| P3-5 MCP/Skill Governance | Owns tool manifest and governance report | Security/governance reviewer | `worldline-mcp-governance`, `worldline-eval-release` | Conditional MCP only after review | No direct DB/filesystem/shell writes | governance report, rollback notes |
| P3-6 Quality Gate Replay | Owns gate service and replay UI contract | Release audit, frontend QA | `worldline-knowledge-pipeline`, `worldline-backend-contract`, `worldline-frontend-workbench` | Browser for replay UI | QualityGateRun service boundary | intentional failure replay |
| P3-7 Compact Console UX | Owns UI layout and screenshot QA | Frontend QA | `worldline-frontend-workbench`, `worldline-eval-release` | Browser/Playwright | No backend contract changes unless scoped | screenshot report, build |

Subagents are read-only by default. A worker subagent may edit only when given a disjoint file set and an explicit patch scope.
