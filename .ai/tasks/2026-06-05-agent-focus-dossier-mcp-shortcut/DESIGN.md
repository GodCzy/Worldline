# Design

## UI

Focus Dossier 原本把所有关联项渲染为同一种 pill button。本阶段改为一层 row 容器：

- 主按钮保留原 `focusDossierItem(item)` 行为。
- 仅当 `item.targetType === 'artifact'` 时显示 `Copy MCP`。
- 状态消息显示在当前 Focus Dossier 面板内部，避免误写到左侧 Registry 或右侧 Artifact Rail。

## MCP Boundary

复制内容继续使用：

- Tool: `worldline.inspect_run_artifacts`
- URI: `worldline-run-ledger://<run_id>/artifacts/<artifact_id>`
- Args: `run_id`, `artifact_id`, `include_content: false`, `audit_db_id: ""`

本阶段不扩展 tool 权限，不暴露 artifact content，保持只复制受控读取入口。

## Fallback

如果 Focus Dossier item 暂时找不到完整 artifact detail，则用 item 的 `targetId`、`label`、`branchId` 生成最小 artifact 详情，保证 planned/local preview 也能形成可读调用。
