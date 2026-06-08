# Design

## State

新增单一 `lastArtifactMcpCall` 状态，用于保存最近一次生成的 artifact MCP read call：

- source
- sourceLabel
- label
- tool
- uri
- args
- instruction

所有复制入口先生成并记录该结构，再调用 Clipboard API。即使复制失败，预览仍保留。

## UI

- `MCP READABLE` 面板追加 `LAST MCP CALL` 可视化块。
- Focus Dossier 对来源为 `focus-dossier` 的 call 显示本地 preview。
- 预览仅显示受控读取调用，不显示 artifact content。

## Governance

本阶段只提升 MCP 调用透明度，不放宽权限，不新增 direct database write，不增加外部 MCP 工具。
