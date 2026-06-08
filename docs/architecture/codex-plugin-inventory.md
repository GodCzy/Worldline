# Codex Plugin Inventory For Worldline

更新时间：2026-06-08

本文件记录 Joy 本机 Codex 插件缓存与 Worldline 项目的使用边界。它不是插件安装指令；安装、连接账号、创建 API key 或授权外部工作区前，必须先确认权限、写入范围、密钥路径和回滚方式。

## Inventory Scope

- 缓存根目录：`C:\Users\Joy\.codex\plugins\cache`
- 顶层缓存组：`openai-bundled`、`openai-curated`、`openai-curated-remote`、`openai-primary-runtime`
- 文件数：1710
- 总大小：27052748 bytes
- `.codex-plugin` manifest：15
- 当前额外可发现 connector：Figma、Notion、Linear、OpenAI Platform、GitHub、Canva

`openai-bundled\chrome\26.527.60818` 有 `control-chrome` skill，但没有独立 `.codex-plugin` manifest；它按本地浏览器 QA 能力管理。

## Plugin Matrix

| 插件 | 版本 | 技能数 | App/Connector | Worldline 适配 | 默认策略 |
|---|---:|---:|---|---|---|
| Browser | 26.527.60818 | 1 | no | 本地页面、localhost、截图、点击、表单、控制台 QA | 默认使用 |
| Computer Use | 26.527.60818 | 1 | no | Windows GUI 操作、非浏览器桌面验证 | 按需，权限面较大 |
| Build Web Apps | 0.1.1 | 6 | no | 前端 app 构建、测试、调试、React/shadcn/Supabase/Stripe 参考 | 条件使用，Worldline 当前是 Vue |
| Build Web Data Visualization | 0.1.20 | 18 | no | 图谱、仪表盘、D3、Canvas、UML、可视化 QA | 建议用于 Graph/Timeline/Branch Canvas |
| Canva | 1.0.1 | 3 | yes | 品牌展示、社交素材、演示视觉 | 不优先 |
| CodeRabbit | 1.1.2 | 1 | no | AI code review 辅助 | 按需；不能替代本地 review |
| Expo | 1.0.1 | 13 | no | React Native / Expo | 当前不适用 |
| GitHub | 0.1.1 | 4 | yes | PR、issue、CI、review、draft PR | 建议连接，远程写入前确认 |
| OpenAI Developers | 1.2.1 | 5 | yes | OpenAI API、Agents SDK、ChatGPT Apps、API key setup | 条件使用，不自动写 key |
| Vercel | 0.21.1 | 47 | yes | 部署、env、observability、Next/Vercel agent | 仅部署阶段评估 |
| Creative Production | 0.1.22 | 9 | empty app map | 广告、logo、moodboard、素材探索 | 不优先 |
| Product Design | 0.1.43 | 11 | no | 产品原型、设计审计、URL to code、image to code | 建议用于 UI 评审 |
| Documents | 26.601.10930 | 1 | no | DOCX、正式报告、交付文档 | 按需 |
| Presentations | 26.601.10930 | 1 | no | PPTX、汇报 deck | 按需 |
| Spreadsheets | 26.601.10930 | 1 | no | 评估矩阵、测试结果、成本表 | 按需 |

## Skill Highlights

### Highest Value For Worldline

- `browser:control-in-app-browser`：本地 `/database`、`/graph`、`/worldline`、`/dashboard` 等页面 QA。
- `github:github`、`github:gh-fix-ci`、`github:gh-address-comments`、`github:yeet`：远程仓库、CI、PR 流程。
- `openai-developers:agents-sdk`、`openai-developers:openai-platform-api-key`：P4/P5 需要真实 OpenAI API 或 Agent SDK 时再启用。
- `build-web-data-visualization:*`：P3-2 Temporal KG、P3-3 Branch Canvas、P3-7 screenshot QA。
- `product-design:design-qa`、`product-design:prototype`、`product-design:url-to-code`：UI 工作台审计和原型补强。

### Conditional

- `vercel:*`：只有要把 Worldline 部署到 Vercel 或做 Vercel agent/app workflow 时使用。
- `coderabbit-review`：作为额外代码审查意见源，不作为最终验收。
- `documents`、`spreadsheets`、`presentations`：只用于交付物，不进入核心服务写路径。

### Low Priority

- `expo:*`：Worldline 不是 Expo/React Native 项目。
- `canva:*` 和 `creative-production:*`：偏营销/创意素材，不是当前工程主线。

## Connector Policy

| Connector | 何时启用 | 风险边界 |
|---|---|---|
| GitHub | 需要 PR、issue、CI、review、远程发布 | 远程写入前确认 branch、commit、PR 文案 |
| Figma | 需要 UI 原型、设计系统、设计稿回代码 | 只处理指定文件和节点；避免写远程设计文件前未确认 |
| Linear | 需要把 P3/P4/P5 变成项目/issue | 不把项目私密内容写入外部 workspace，除非 Joy 同意 |
| Notion | 需要外部 PRD、周报、知识库 | 仓库 docs 仍是工程事实源；Notion 是镜像或管理视图 |
| OpenAI Platform | 需要创建项目 API key | key 只写入确认过的 env 路径，绝不写入仓库 |
| Canva | 需要品牌或演示素材 | 不承载工程事实源 |
| Vercel | 需要部署或预览 | env、域名、日志和计费影响先确认 |

## Worldline Workflow Mapping

1. Orient：`worldline-orient` + `AGENTS.md` + `README.md` + `docs/index.md`。
2. Implement：主控 Agent 改代码；Browser、Data Viz、Product Design 只在对应任务需要时辅助。
3. Verify：pytest、docs build、frontend build、Browser/Playwright screenshot QA。
4. Govern：`worldline-mcp-governance` 确认 connector 和 MCP 不绕过服务边界。
5. Record：`.ai/tasks/<date-task>/EVIDENCE.md` 和 `D:\document\OutputMD`。
6. Publish：GitHub/Vercel/Notion/Linear 只在 Joy 选择并授权后使用。

## Do Not Enable By Default

- database direct-write MCP
- unrestricted filesystem MCP
- shell/admin/Docker/Kubernetes write MCP
- external communication write tools
- any connector that requires secrets before destination and scope are confirmed
