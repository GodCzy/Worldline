# Worldline Agent Focus Dossier MCP Shortcut - Alignment

## Goal

在 Agent Workbench 的 Focus Dossier 中，为 artifact 类型关联项补齐 `worldline.inspect_run_artifacts` MCP read 快捷入口，让用户从当前聚焦档案可以直接复制外部 Agent 可用的受控读取调用。

## Scope

- 修改 `web/src/views/worldline/WorldlineAgentWorkbenchView.vue`。
- 仅在 Focus Dossier 的 artifact link 旁增加 `Copy MCP`。
- 复用现有 artifact registry / artifact rail 的 MCP URI 与 args 生成逻辑。
- 不改变后端接口、MCP tool contract 或 run ledger 持久化逻辑。

## Acceptance

- Focus Dossier 中 artifact link 仍可点击聚焦到 artifact rail。
- Artifact link 旁出现独立 `Copy MCP` 小按钮。
- 点击后在 Focus Dossier 本地显示 MCP read call 状态消息。
- 构建通过，浏览器截图确认 UI 不重叠、不出现按钮嵌套。
