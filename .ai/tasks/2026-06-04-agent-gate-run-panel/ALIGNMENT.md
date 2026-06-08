# Agent Gate Run Panel Alignment

更新时间：2026-06-04

## 目标

把 Agent 工作台中的 Quality Gates 从静态状态格子升级为 Gate Run Panel，让每个质量门能展示输入、阈值、状态原因、修复建议、来源工具和关联 Artifact。

## 范围

- 仅改 Agent 工作台前端和本地 preview 数据。
- 复用已有 `gateResults`、event summary `gateDetails`、Artifact Rail 和 Focus Dossier。
- 支持 `Branch`、`Event`、`All` 三种质量门视角。
- 点击质量门条目后复用 Focus Dossier，并高亮 Gate panel 条目。

## 不做

- 不新增数据库 schema。
- 不新增后端 API。
- 不新增依赖。
- 不触碰无关 dirty tree 或旧 `.ai/tasks` 删除项。

## 验收

- `/worldline/agent` 中 Quality Gates 面板展示 Gate Run 信息，而不只是状态格子。
- Branch/Event/All 视角计数正确。
- 每个 Gate Run 显示状态、value、threshold、input、tool、artifact 和 remediation。
- 点击 `Permission risk` 等 gate 后，Focus Dossier 显示扩展详情并高亮对应 gate。
- 前端 build、diff check、浏览器交互验证通过，截图写入任务证据。
