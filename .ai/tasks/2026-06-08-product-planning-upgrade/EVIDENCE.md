# P2-5 证据

日期：2026-06-08

## 已读取事实源

- `D:\dev\Worldline\docs\product\worldline-project-book.md`
- `D:\dev\Worldline\docs\architecture\knowledge-compiler.md`
- `D:\dev\Worldline\docs\architecture\llm-wiki.md`
- `D:\dev\Worldline\docs\architecture\temporal-evidence-graph.md`
- `D:\dev\Worldline\docs\architecture\worldline-ui.md`
- `D:\dev\Worldline\docs\architecture\mcp-skill-governance.md`
- `D:\dev\Worldline\docs\architecture\evaluation-gates.md`

## 已对齐 skill 约束

- `worldline-knowledge-pipeline`
  - 从 evidence 出发，所有 claim 回到 `EvidenceAnchor`。
  - 保留 Docling 结构，不提前压成纯 Markdown。
  - Wiki 是主阅读面，RAG 是辅助召回层。
  - 显式建模 temporal facts。
  - 管线变化需要 quality gates。
- `worldline-mcp-governance`
  - 默认使用受控 `worldline` MCP 边界。
  - 不默认启用数据库直写 MCP、全盘 filesystem MCP、shell MCP。
  - 写入需要 service boundary、权限和 audit logs。
- `worldline-frontend-workbench`
  - 第一屏是可用控制台，不是 landing page。
  - 世界线视觉优先 SVG/Canvas/G6。
  - evidence rail、timeline scrubber、graph focus、Agent handoff 是操作控件。

## 输出

- `D:\dev\Worldline\.ai\tasks\2026-06-08-product-planning-upgrade\ROADMAP.md`
- `D:\document\OutputMD\2026-06-08-Worldline-Product-Planning-Upgrade.md`
