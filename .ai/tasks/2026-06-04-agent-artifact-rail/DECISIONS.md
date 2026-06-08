# Agent Artifact Rail Decisions

更新时间：2026-06-04

## 决策

- Artifact Rail 放在 Evidence Rail 与 Tool Trace 之间。原因：它是证据与工具执行之间的产物索引，位置上应连接 evidence 和 tool。
- 采用 Branch / Event / All 视角切换，而不是单一列表。原因：Agent 世界线需要同时支持当前分支检查和事件回放。
- 不新增下载/打开文件按钮。原因：当前 artifact 仍是结构化线索，不保证本地路径真实存在；先做可浏览和可定位的审计面板。
