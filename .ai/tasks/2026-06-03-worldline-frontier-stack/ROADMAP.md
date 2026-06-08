# Worldline Frontier Stack Roadmap

更新时间：2026-06-03

## Phase 0 - Restart Stabilization

- 固定当前 dirty tree 事实，确保重启清理和新增关键文件可追踪。
- 增加编码/换行保护，减少 Windows CRLF 大面积 churn。
- 修正 Docker build context 忽略规则。
- 让本地单测不因 live API 管理员凭据缺失而在 collection 阶段失败。

## Phase 1 - Stack Decision

- 写入研究矩阵和项目书。
- 明确保留、引入、暂缓、禁止的技术栈。
- 把 LLM Wiki、STORM、Graphiti、KAG、HippoRAG 的借鉴点转化为 Worldline 原生架构。

## Phase 2 - Knowledge Compiler v1

- 用 Docling 结构化输出驱动 `SourceAsset`、`DocumentVersion`、`DocumentNode`、`EvidenceAnchor`。
- 保留 Markdown 作为输出格式之一，不作为唯一中间表示。
- 加入结构化 evidence bundle 和可回放 parse stats。

## Phase 3 - LLM Wiki Mainline

- 实现 STORM 风格 outline、章节、引用、争议点和待验证问题。
- `WikiPage` 增强人工审核、freshness、backlinks、evidence coverage。
- RAG 只负责补充 evidence candidates。

## Phase 4 - Temporal Evidence Graph

- 借鉴 Graphiti episode/provenance/validity-window。
- Neo4j 承载实体关系和时间事实，Milvus/LightRAG 辅助检索。
- KAG/HippoRAG 进入评估实验，不作为平台迁移。

## Worldline UI Workbench

- 重做 `/worldline` 和 `/worldline/:themeId` 为全屏世界线工作台。
- 实现青金发光线束、证据轨联动、时间 scrubber、图谱聚焦和 Agent handoff。
- 用 Browser/Playwright 记录桌面和移动截图证据。

## Phase 6 - Skills / MCP / Subagents

- 安装并验证本地 Worldline Codex skills。
- MCP 默认只保留受控 `worldline`、GitHub、Browser/Playwright。
- Firecrawl、Context7、Tavily 仅在密钥和权限审查后按需启用。
- 子代理默认只做研究、审查、测试报告；主控 Agent 决策和改文件。

## Phase 7 - Evaluation And Demo

- 建立引用覆盖率、图谱一致性、幻觉检查、成本/延迟、权限审计门禁。
- 输出公开演示数据、截图、docs 站点和项目介绍。
