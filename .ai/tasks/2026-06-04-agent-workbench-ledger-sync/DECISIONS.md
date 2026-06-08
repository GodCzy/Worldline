# Agent Workbench Ledger Sync Decisions

更新时间：2026-06-04

## D1. 保持本地预览为降级路径

原因：用户已经明确“后端暂不可用，当前使用本地配置渲染首页”。Agent 工作台必须在未登录、非管理员或 API 不可用时继续可用。

## D2. 不做 schema 迁移

原因：Stage 2 run ledger 已经用文件账本提供临时持久化能力，本阶段只做前端接线，避免扩大后端风险面。

## D3. 后端返回和本地 UI 字段做兼容合并

原因：后端账本关注 run/branch/event/skill，前端工作台还需要 tool traces、quality gates、contract map 和 display meta。直接替换会丢 UI 上下文。
