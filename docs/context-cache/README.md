# Context Cache Active Baseline

`docs/context-cache/` 现在只保留当前仍在活跃使用的阶段基线。

## 当前保留文件

- `phase-87-phase7-10-reordered-master-plan.md`
  - Phase 7-10 重排后的总计划基线
  - 当前 Phase 7 的最高优先级执行依据
- `phase-86-phase6-round1-runtime-smoke-green.md`
  - 进入 Phase 7 之前最近一次通过的真实 runtime smoke 基线

## 历史压缩总览

- Worldline 已从早期阶段文档堆叠模式切换到“当前基线 + 最近稳定基线 + 历史归档”的长期维护结构。
- Phase 1 到 Phase 6 的旧缓存文件已统一下沉到 `docs/archive/context-cache/`。
- 旧缓存不再进入当前主阅读面，也不再作为默认启动阅读序列。

## 使用规则

- 新任务启动时，只优先读取当前任务真正需要的活跃基线。
- 若需要追溯旧阶段约束、旧门禁或历史决策，再进入 `docs/archive/context-cache/`。
- 若本轮产生新的稳定阶段结论，应在本目录新增或更新一份 concise baseline，而不是重新堆积大量细碎缓存。
