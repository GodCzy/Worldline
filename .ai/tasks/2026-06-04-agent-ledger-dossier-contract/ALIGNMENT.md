# Agent Ledger Dossier Contract Alignment

更新时间：2026-06-04

## 目标

把 Agent 工作台的 Focus Dossier 与后端 run ledger 事件摘要对齐，让真实后端事件不只返回 evidence/tool/timeline ID，也能携带权限、质量门和 artifact 等可审查线索。

## 范围

- 扩展 `WorldlineRunLedgerService` 的兼容 summary 字段。
- 保留现有 `/api/worldline/runs*` API shape，不移除已有字段。
- 让前端 `EVENT DETAIL` 能识别 `gateResultIds`、`artifactIds`、`toolDetails`、`gateDetails`、`artifactDetails`。
- 给 Quality Gate 和 Artifact 增加 Dossier 支持。

## 不做

- 不新增数据库 schema。
- 不新增外部依赖。
- 不改变 protected knowledge/worldline routes。
- 不要求管理员真实登录完成 E2E 写入；以服务单测、OpenAPI/health 和本地前端预览验证为主。

## 验收

- run created / branch approved / skill proposed 事件 summary 保留旧字段。
- run/branch 事件 summary 增加 `requiredPermissions`、`gateResultIds`、`artifactIds` 和 detail arrays。
- 前端事件详情出现 Quality Gates / Artifacts token，并可打开 Dossier。
- focused pytest、frontend build、browser screenshot 和 backend smoke 通过。
