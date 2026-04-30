# 世界线 Phase 13 Official Docs Refresh

## Goal

- 将仓库内非缓存类正式 Markdown 文档统一重写为可交付、可答辩、可维护的正式版本。
- 明确项目当前完成程度、当前可用能力和后续工作重点。

## Stable Decisions

- `docs/context-cache/` 继续只作为压缩工作记忆，不纳入正式对外交付文档体系。
- 正式文档入口以 `README.md` 和 `docs/index.md` 为核心。
- 文档叙事统一围绕“基于底座进行产品化改造 + PoE 首期模块闭环验证”。
- AGENTS 和 CODEX 工作流文档保留规则语义，但清理编码污染并提升可读性。

## Allowed Files

- `README.md`
- `WORLDLINE_PROJECT_PLAN.md`
- `AGENTS.md`
- `CODEX_WORKFLOW.md`
- `docs/*.md`
- `src/agents/skills/reporter/SKILLS.md`
- `docs/context-cache/phase-13-official-docs-refresh.md`

## Blocked Files

- `docs/context-cache/**` 之外的运行时代码本轮不修改
- 高风险后端核心链路不在本轮范围内

## Validation Snapshot

- `npm run docs:build`: passed
- 正式文档集已重写完成
- 当前项目叙事、阶段状态、演示用途与后续路线已统一

## Next Step

- 继续做前端展示层乱码清理
- 补一次“当前项目完成度与剩余缺口”的对外汇总说明
