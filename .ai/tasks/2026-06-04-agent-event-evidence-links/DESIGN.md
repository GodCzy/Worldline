# Agent Event Evidence Links Design

更新时间：2026-06-04

## 后端 summary 字段

事件 summary 增加以下可选字段：

- `evidenceIds`
- `toolCallIds`
- `temporalFactIds`
- `requiredPermissions`
- `evidenceRunIds`
- `branch_title`
- `branch_type`
- `quality_status`
- `score`

这些字段都放在现有 `summary` 对象内，不改变事件顶层 schema。

## 前端展示

前端从 `event.summary` 中提取数组字段，生成 chips：

- Evidence `n`
- Tool `n`
- Timeline `n`
- Permission `n`
- Run Evidence `n`

Chip 不跳转外部页面；点击事件本身仍聚焦 `branchId`。

## Preview 事件

本地 preview 事件从当前 active branch、tool traces、timeline refs 和 skill proposals 派生 chips，保证后端暂不可用时也能看到最终产品形态。
