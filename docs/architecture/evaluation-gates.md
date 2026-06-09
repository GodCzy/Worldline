# Evaluation Gates

更新时间：2026-06-08

## Goal

Worldline 的评估不是只跑 benchmark，而是持续检查知识编译、Wiki、图谱、RAG、Agent 和 MCP 是否可信。

## Gates

- Evidence coverage：回答、Wiki 段落、实体、关系、时间事实必须有 evidence ids。
- Citation accuracy：引用能打开 source uri，并定位到 page/line/bbox。
- Graph consistency：实体去重、关系方向、时间有效期、冲突事实。
- Wiki freshness：来源更新后 stale page 可检测、可重建。
- Retrieval quality：RAG 召回覆盖 golden set，但不替代最终可信度。
- Hallucination check：无证据 claim 标记为 unsupported。
- MCP permission：高风险工具禁用，写工具有审计日志。
- Cost / latency：记录模型调用、检索耗时、图谱更新耗时。

## Acceptance Evidence

- pytest 结果。
- Vite build / docs build / docker compose config。
- Browser/Playwright 截图。
- Quality gate run payload。
- `.ai/tasks/<date-task>/EVIDENCE.md` 命令摘要。

## P3 Gate Matrix

| Slice | Required checks | Browser QA | Required artifacts |
|---|---|---|---|
| P3-1 Evidence-backed Wiki | Focused pytest for Wiki metadata, evidence coverage, citations, stale state | `/worldline/:themeId` desktop and `390x844` if UI changes | Wiki page payload, citation refs, `EVIDENCE.md`, OutputMD |
| P3-2 Temporal KG | Focused pytest for entity/relation/fact evidence ids and conflict detection | `/graph` and `/worldline/:themeId` focus states | graph/timeline payloads, conflict sample |
| P3-3 Branch Canvas | Payload compatibility test for `/worldline/generate` and store hydration | branch hover/select desktop and `390x844` | screenshot report, branch refs |
| P3-4 Agent Run Ledger | Run ledger service pytest and audit contract pytest | Agent Workbench real backend E2E when UI changes | run id, audit rows, cleanup proof |
| P3-5 MCP/Skill Governance | governance report and release gate | Optional only for admin UI | tool manifest, disabled defaults, rollback path |
| P3-6 Quality Gate Replay | gate service pytest and intentional failure replay | replay panel desktop and mobile when UI changes | QualityGateRun payload, failure refs |
| P3-7 Compact Console UX | `pnpm --dir web build`, `git diff --check` | required for touched routes at desktop and `390x844` | screenshots, console error/warn report |

## Release Gate

The static project release gate lives in `WorldlineReleaseGateService`.

The gate checks:

- Required docs are present.
- Required task directories and `EVIDENCE.md` files are present.
- Local Codex Worldline skills are installed.
- Application MCP defaults pass the Worldline governance report.
- MCP disabled-tool policy is present, including high-risk markers, conditional servers disabled by default, and task-required enablement review.
- Connector rollback policy is present, including `remove_secrets`, `revoke_remote_authorization`, and remote draft cleanup evidence paths.
- The controlled Worldline manifest keeps audit logs, service-boundary writes, and subagent lanes.
- UI screenshot QA has no failures and covers home, themes, Worldline hub, Agent login redirect, and authenticated superadmin sidebar across desktop and mobile viewports.

The command is:

```powershell
python scripts\worldline_phase6_7_release_gate.py
```
