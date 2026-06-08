# Agent Gate Run Panel Design

更新时间：2026-06-04

## 面板位置

Gate Run Panel 继续使用现有 `QUALITY GATES` 面板位置，位于 Tool Trace 后、Skill Genome 前。

## 数据来源

- 全量 Gate：`agentRun.gateResults`。
- Branch Gate：当前 active branch 的 `gateResultIds` 和 `activeEpisodes[].gateResults`。
- Event Gate：`selectedLedgerEvent.summary.gateDetails` 和 `gateResultIds`。

## 展示字段

- `label`
- `status`
- `value`
- `threshold`
- `input`
- `summary`
- `toolCallIds`
- `artifactIds`
- `failureReason`
- `remediation`

## 交互

- `Branch`：当前分支相关质量门。
- `Event`：当前事件相关质量门。
- `All`：当前 run 所有质量门。
- 点击 gate 条目：设置 `inspectorFocus.type="gate"`，滚动并打开 Focus Dossier。

## 兼容策略

- 如果后端 gate detail 不包含扩展字段，保留 label/status/value/summary。
- 如果只有 ID，则显示结构化 ID 的占位说明，避免空白面板。
