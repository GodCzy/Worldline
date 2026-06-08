# Agent Ledger Dossier Contract Design

更新时间：2026-06-04

## 后端

- 在 file-backed ledger 中保留 `toolTraces` 和 `gateResults`。
- 事件 summary 追加兼容字段：
  - `requiredPermissions`
  - `gateResultIds`
  - `artifactIds`
  - `toolDetails`
  - `gateDetails`
  - `artifactDetails`
- 所有新增字段都是 optional additive，不替换现有 `evidenceIds`、`toolCallIds`、`temporalFactIds`。

## 前端

- `eventLinkChips` 和 `eventDetailSections` 新增 Gate / Artifact。
- Dossier 目标解析优先使用本地 run 数据，其次使用当前事件 summary detail arrays。
- Artifact 没有单独页面目标时，点击 token 只打开 Dossier，不强行滚动到不存在的目标。

## 风险

- file-backed ledger 仍是 Stage 2 过渡方案，不等价于最终 Postgres schema。
- artifact metadata 当前来自 payload，若调用方没有提供 artifact details，只能展示 ID。
