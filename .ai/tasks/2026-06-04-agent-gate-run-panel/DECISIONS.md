# Agent Gate Run Panel Decisions

更新时间：2026-06-04

## 决策

- 复用现有 `QUALITY GATES` 面板，而不是新增第四个右侧面板。原因：质量门是已有概念，应升级原有面板而不是增加重复入口。
- Gate Run 采用 Branch/Event/All 视角。原因：与 Artifact Rail 一致，支持分支检查、事件回放和全局审计。
- 不加入执行按钮。原因：当前后端质量门执行入口属于知识库质量门，不应在本地 preview 中伪造真实执行。
