# Agent Artifact Rail Design

更新时间：2026-06-04

## 设计

Artifact Rail 是 Agent 工作台的产物索引面板，放在 Evidence Rail 之后、Tool Trace 之前。

## 数据来源

- 全量产物：从 `agentRun.toolTraces[].artifacts` 和 `artifactIds` 归一化。
- 分支产物：按当前 active branch 的 `activeToolTraces` 与 `activeEpisodes[].artifactIds` 过滤。
- 事件产物：优先读取 `selectedLedgerEvent.summary.artifactDetails`，必要时用 `artifactIds` 回查全量产物。

## 交互

- `Branch`：显示当前 active branch 相关产物。
- `Event`：显示当前 selected event 相关产物。
- `All`：显示当前 run 所有产物。
- 点击任一产物，设置 `inspectorFocus={ type: "artifact", id }`，复用 Focus Dossier。

## 兼容

- 如果后端只有 `artifactIds` 没有 `artifactDetails`，Rail 回退到本地 tool trace artifact 映射。
- 如果 artifact 没有独立 DOM 目标，滚动到 Dossier；Rail 自身条目提供 `data-inspector-target="artifact:<id>"`。
