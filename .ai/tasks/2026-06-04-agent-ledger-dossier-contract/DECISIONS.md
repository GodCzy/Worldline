# Agent Ledger Dossier Contract Decisions

更新时间：2026-06-04

## 决策

- 采用 additive summary 字段，不替换现有字段。原因：保护已有前端和测试对 run ledger event shape 的消费。
- 暂不做 DB schema。原因：当前 run ledger 明确是 file-backed Stage 2，目标是先稳定前后端交互契约。
- Artifact token 只打开 Dossier，不要求页面内存在独立 artifact rail。原因：当前页面还没有 artifact 专用面板，强行滚动会造成虚假定位。
