# 世界线 Phase 19 Subagent 提示词与常驻纪律

## Goal

- 让 subagent-first 模式落实到实际执行纪律上。
- 固化新的协作要求：
  - 与项目正式相关的 subagents 可以常驻且应保持可见
  - 与项目无关、一次性探索、临时调试用的 subagents 可以关闭
  - 下一轮提示词固定使用统一结构
  - substantial task 必须体现合理且充分的 subagent 分配

## Stable Decisions

- 世界线正式定义的 subagent 阵型可以常驻显示，方便用户随时查看。
- 不需要长期保留的只有这几类：
  - unrelated subagents
  - one-off debugging subagents
  - temporary exploratory subagents
- 后续给用户的单一提示词统一采用以下结构：
  - `先读：`
  - `当前基线：`
  - `本轮优先任务：`
  - `要求：`
- 其中 `本轮优先任务` 必须是提示词重点。
- 如果任务属于 substantial task，提示词中必须体现 subagent 分配方式，而且要尽量充分利用项目常驻 subagent 阵型。
- 每阶段仍保持：
  - 自动 git 提交
  - 给出验证方式
  - 在适当时候更新 `docs/context-cache/`

## Files Updated

- `AGENTS.md`
- `CODEX_WORKFLOW.md`
- `docs/context-cache/phase-19-subagent-prompt-discipline.md`

## Next Step

- 下一次真实版本任务应按新的提示词结构发起，并验证“常驻 subagent + 合理并行分配”是否真正落地。
