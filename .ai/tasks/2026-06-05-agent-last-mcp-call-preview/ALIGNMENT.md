# Worldline Agent Last MCP Call Preview - Alignment

## Goal

让 Agent Workbench 中所有 artifact MCP read 快捷入口不仅可以复制，还能在界面内核验最近一次生成的 Tool、URI 和 Args，避免剪贴板不可用或外部 Agent 交接时缺少可见依据。

## Scope

- 修改 `web/src/views/worldline/WorldlineAgentWorkbenchView.vue`。
- 覆盖 Registry、MCP Readable、Artifact Rail、Focus Dossier 的 artifact read call。
- 保持 `worldline.inspect_run_artifacts` 工具名、URI 结构和 args 不变。
- 不改后端、MCP server、run ledger service 或数据库 schema。

## Acceptance

- 任一 artifact MCP copy 入口触发后，`MCP READABLE` 面板显示 `LAST MCP CALL`。
- `LAST MCP CALL` 包含来源、artifact label、Tool、URI、Args。
- Focus Dossier 触发时，dossier 内也出现本地 MCP preview，避免只依赖左侧面板。
- 构建通过，浏览器 QA 能点击 Focus Dossier artifact `Copy MCP` 并看到 last-call 预览。
