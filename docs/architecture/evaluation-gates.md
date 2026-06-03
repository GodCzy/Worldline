# Evaluation Gates

更新时间：2026-06-03

## Goal

Worldline 的评估不是只跑 benchmark，而是持续检查知识编译、Wiki、图谱、RAG、Agent 和 MCP 是否可信。

## Gates

- Evidence coverage：回答、Wiki 段落、实体、关系、时间事实必须有 evidence ids。
- Citation accuracy：引用能打开 source uri，并定位到 page/line/bbox。
- Graph consistency：实体去重、关系方向、时间有效期、冲突事实。
- Wiki freshness：来源更新后 stale page 可检测、可重建。
- Retrieval quality：RAG 召回覆盖 golden set，不替代最终可信度。
- Hallucination check：无证据 claim 标记为 unsupported。
- MCP permission：高风险工具禁用，写工具有审计日志。
- Cost / latency：记录模型调用、检索耗时、图谱更新耗时。

## Acceptance Evidence

- pytest 结果。
- Vite build / docs build / docker compose config。
- Browser/Playwright 截图。
- Quality gate run payload。
- `.ai/tasks/<date-task>/EVIDENCE.md` 命令摘要。

## Phase 7 Release Gate

Phase 7 adds a static project release gate in `WorldlineReleaseGateService`.

The gate checks:

- Required docs are present.
- Required phase task directories and `EVIDENCE.md` files are present.
- Local Codex Worldline skills are installed.
- Application MCP defaults pass the Worldline governance report.
- The controlled Worldline manifest keeps audit logs, service-boundary writes, and subagent lanes.
- Phase 5 screenshot QA has no failures and covers hub, workbench, and graph pages across desktop and mobile viewports.

The command is:

```powershell
python scripts\worldline_phase6_7_release_gate.py
```
