# Worldline 产品/工程升级路线图

日期：2026-06-08

## 北极星

Worldline 是 Evidence-backed LLM Wiki + Temporal Knowledge Graph OS。它的核心体验是把来源材料编译成可追溯证据、可阅读 Wiki、可推理时序图谱、可比较世界线、可审计 Agent 账本和可回放质量门禁。

它不是普通 RAG 聊天页。聊天、向量检索和长尾召回只是进入知识系统的辅助方式。

## 当前基线

已经具备的基础：

- 新建知识库页面紧凑化，复杂后端配置进入按钮/抽屉。
- Graph/Timeline 后端链路可通过真实 API 验证。
- 主题模块 metadata contract 和前端闭环完成。
- Run Ledger 最小后端审计契约完成。
- Agent Workbench、Dashboard、内容 KB、全站 UI QA 完成真实验证。
- 上传/解析/query params 链路复核完成。
- Agent/run 任务目录审计完成。
- 临时 QA profile/log/cache 已清理。
- 工作树分组与提交边界已形成。

## P3 推荐优先级

### P3-1 Evidence-backed LLM Wiki 垂直切片

目标：单个真实内容知识库能够生成可阅读、可引用、可审查的 Wiki 页面。

后端重点：

- 保证 `WikiPage` 顶层字段暴露 `outline`、`sections`、`claims`、`citations`、`open_questions`、`disputes`、`review`、`evidence_coverage`。
- 每个 claim 至少包含 `evidence_ids`。
- 每个 citation 能回到 source uri、page、line、bbox 或 char span。
- Source 更新后能标记 stale Wiki。

UI 落点：

- `/worldline/:themeId` 的 evidence rail 展示 Wiki refs。
- Wiki section 点击后能聚焦 evidence anchor。
- unsupported claim 必须可见，不隐藏在正文里。

验收证据：

- focused pytest 覆盖 Wiki metadata contract。
- 真实内容 KB 生成 Wiki 后，至少 1 个页面包含 claim/citation/review/evidence coverage。
- 浏览器截图覆盖桌面和 390px 移动端。

### P3-2 Temporal Knowledge Graph 垂直切片

目标：把实体、关系和时间事实变成可追溯、可冲突检测、可投影到图谱视图的知识层。

后端重点：

- `KnowledgeEntity`、`KnowledgeRelationship`、`TemporalFact` 必须保留 evidence ids。
- temporal fact 显式记录 valid time、invalidated facts、conflict status。
- graph/timeline endpoint 能返回与 Wiki claim 可互相跳转的 refs。
- Neo4j projection 继续只读，不默认直写外部图数据库。

UI 落点：

- `/graph` 支持从 Worldline route context 聚焦实体/关系/时间事实。
- Timeline scrubber 支持 Source/Wiki/Graph/Gate snapshot 切换。
- conflict facts 以审查状态呈现，不直接覆盖旧事实。

验收证据：

- focused pytest 覆盖 graph conflict contract。
- 真实 KB 至少生成实体、关系和 temporal facts。
- `/graph` 和 `/worldline/:themeId` 截图覆盖聚焦态。

### P3-3 Worldline Branch Canvas

目标：把 Wiki、Evidence、Graph、Timeline 和 Quality Gate 编译成可比较世界线分支，而不是只输出一段答案。

后端重点：

- `/api/knowledge/databases/{db_id}/worldline/generate` payload 继续兼容 `worldlineStore.hydrate`。
- branch payload 添加 `wikiRefs`、`entityRefs`、`timelineRefs`、`quality`、`routeTrace`。
- branch 生成必须绑定 evidence anchors，不允许无证据结论进入默认分支。

UI 落点：

- 世界线画布左侧是 root question，中间是 branch/inspection nodes，右侧是 action/convergence。
- hover/select branch 更新 inspector、evidence rail、timeline、graph focus。
- 复杂配置通过命令面板/抽屉，第一屏保留操作密度。

验收证据：

- Desktop + mobile screenshot 无空白画布、无横向溢出、无文字重叠。
- branch inspector 能显示 source、Wiki、entity、timeline 和 gate refs。

### P3-4 Agent Run Ledger 与 Replay

目标：Agent 的工具调用、证据读取、决策、分支审批、artifact 和 handoff 都能形成可复盘账本。

后端重点：

- `/api/worldline/runs` 支持 run list/detail/events/artifacts/gates/evidence/knowledge。
- MCP resource reads 和 not_found reads 写 audit log。
- artifact registry 与 branch decision 绑定。
- run archive/restore/bulk maintenance 保留审计记录。

UI 落点：

- Agent Workbench 默认显示真实后端 run。
- 本地 preview 只作为 fallback，并清楚标记。
- 详情抽屉展示 manifest、resources、gates、artifacts、decision replay。

验收证据：

- focused pytest 覆盖 run ledger service 和 audit contract。
- 浏览器 E2E 使用临时管理员，结束后清理账号和临时 run。

### P3-5 MCP / Skill Governance

目标：外部 Agent 可以安全协作，但不能绕过 Worldline 服务边界直接写数据库或文件系统。

后端重点：

- 默认只启用受控 `worldline` application MCP。
- tool manifest 标明 subagent lanes、read/write 权限、admin intent 和 audit log。
- 条件 MCP 必须记录来源、license、command、args、env、write scope 和 rollback。
- direct database-write MCP、unrestricted filesystem MCP、shell MCP 不进入默认配置。

UI 落点：

- 管理界面展示 enabled/disabled toolsets、权限范围、最近审计事件和撤销入口。
- 高风险工具默认禁用，启用需要显式任务理由。

验收证据：

- governance report 通过 release gate。
- MCP 权限 gate 覆盖默认启用项和禁用项。

### P3-6 Quality Gate Replay

目标：质量门禁不只是 pass/fail，而是能回放为什么失败、关联哪些证据、哪些 Wiki/Graph/Timeline 节点需要修复。

后端重点：

- Gate 覆盖 evidence coverage、citation accuracy、graph consistency、wiki freshness、retrieval quality、hallucination、MCP permission、cost/latency。
- `QualityGateRun` 记录 gate payload、失败原因、相关 evidence/wiki/entity/timeline refs。
- 支持按 KB、theme、branch、run 回放。

UI 落点：

- Gate panel 在 Worldline branch inspector 中显示。
- 失败项可跳转到 evidence anchor、Wiki section、graph node 或 Agent run event。

验收证据：

- `scripts/worldline_phase6_7_release_gate.py` 或后续 gate 脚本覆盖新增 contract。
- 至少一个 intentional failure replay 可在 UI 中定位原因。

### P3-7 Compact Console UX

目标：保持复杂后端能力完整，但主页面简洁、密集、可操作。

原则：

- 第一屏是控制台，不是营销页。
- 复杂配置进入抽屉、详情窗、命令面板和 payload preview。
- 卡片只用于重复项、modal 或真正需要框定的工具，不把页面章节做成嵌套卡片。
- 使用现有 Vue 3、Vite、Pinia、Ant Design Vue、G6/D3/Sigma/Graphology/ECharts 能力，暂不默认 Three.js。

验收证据：

- `/`、`/themes`、`/worldline`、`/worldline/:themeId`、`/graph`、`/database`、`/dashboard`、`/extensions` desktop/mobile QA。
- 390px 无页面级横向溢出。
- 控制台无 error/warn。

## 推荐 P3 垂直切片顺序

1. 单文档 evidence-backed Wiki：上传/解析 -> EvidenceAnchor -> WikiPage -> citation UI -> gate。
2. Wiki + Temporal Graph：Wiki claim -> entity/relation/fact -> conflict/timeline -> graph focus。
3. Branch Canvas：root question -> evidence-backed branches -> inspector refs -> mobile QA。
4. Agent Replay：branch handoff -> run ledger -> artifact/gate/evidence reads -> replay drawer。
5. Governance + Release：MCP defaults -> permission gates -> release gate -> public demo smoke。

## 不做事项

- 不把 Worldline 改成普通 RAG chat shell。
- 不整体迁移到 Dify、RAGFlow、DeepWiki、Graphiti、KAG 或 HippoRAG。
- 不默认启用数据库直写 MCP、全盘 filesystem MCP、shell MCP。
- 不把 unsupported claim 混在正文里当作已证实结论。
- 不让 local preview/mock 数据冒充真实后端能力。
- 不让第一屏成为大表单或营销 hero。

## 下一次目标模式建议

如果进入 P3，建议第一句话：

```text
请读取 D:\dev\Worldline\.ai\tasks\2026-06-08-product-planning-upgrade\ROADMAP.md，并从 D:\dev\Worldline 继续。先做 P3-1 Evidence-backed LLM Wiki 垂直切片：单个真实内容知识库生成可阅读、可引用、可审查的 Wiki 页面，并完成 focused pytest 与桌面/390px 截图 QA。
```
