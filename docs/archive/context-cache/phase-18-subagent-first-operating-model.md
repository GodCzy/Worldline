# 世界线 Phase 18 Subagent-First 协作模式重构

## Goal

- 将仓库协作方式从旧的轻量多角色模式，重构为真正的 subagent-first operating model。
- 让后续企业级版本迭代默认以真实子代理并行为主，而不是仅靠角色标签描述。

## Problem Statement

此前的多角色模式没有形成明显收益，核心原因是：

1. 角色偏顺序，天然更像串行流程
2. 角色适合早期单模块阶段，不适合企业级复杂协作
3. 很多任务中“角色”只是表达层标签，而不是真实并行的 subagent 执行

## Stable Decisions

- 世界线后续 substantial tasks 默认采用 true subagents。
- 默认 first wave：
  - `system_mapper`
  - `product_architect`
  - `qa_release_auditor`
- scope 稳定后再进入 write wave：
  - `frontend_worker`
  - `backend_worker`
  - `knowledge_rag_engineer`
  - `graph_engineer`
  - `agent_architect`
- 旧角色集合已废弃，不再作为默认模式：
  - `repo_mapper`
  - `platform_architect`
  - `poe_designer`
  - `implementer`

## Files Updated In This Refactor

- `AGENTS.md`
- `CODEX_WORKFLOW.md`
- `.codex/config.toml`
- `.codex/agents/system_mapper.toml`
- `.codex/agents/product_architect.toml`
- `.codex/agents/knowledge_rag_engineer.toml`
- `.codex/agents/graph_engineer.toml`
- `.codex/agents/agent_architect.toml`
- `.codex/agents/frontend_worker.toml`
- `.codex/agents/backend_worker.toml`
- `.codex/agents/qa_release_auditor.toml`
- `docs/10-subagent-operating-model.md`

## Config Decisions

- `max_threads = 6`
- `max_depth = 2`

这表示后续世界线默认允许更真实的并行 subagent 协作，而不是保守的轻量串行模式。

## Validation Snapshot

- 协作规则、agent 配置与正式说明文档已重写
- 后续应通过 `npm run docs:build` 与 git 状态检查确认文档层变更稳定

## Next Step

- 基于新协作模型收敛企业化 `v1.1` 版本计划
- 在后续 substantial task 中真正执行“先 read-only wave，再 write wave”的 subagent 调度
