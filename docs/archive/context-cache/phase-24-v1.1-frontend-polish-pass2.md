# Phase 24 Cache: v1.1 Frontend Polish Pass 2

## Scope
- Frontend presentation-layer copy polish only.
- Files touched:
  - `web/src/views/AgentView.vue`
  - `web/src/views/GraphView.vue`
  - `web/src/views/DashboardView.vue`

## Stable Outcome
- Agent page guidance is clearer:
  - top section explicitly says it is for theme context, recommendation, and loop summary
  - the actual input area is still described as fixed at the bottom
  - the config selector now shows `当前配置` when there is no active config name
- Graph page copy is more explicit:
  - header uses `知识图谱`
  - database selector uses `当前知识库`
  - empty state explains the current graph is unavailable and suggests switching knowledge bases or uploading files
  - upload modal and import tips are rewritten in clearer Chinese
- Dashboard copy is less technical:
  - agent section is renamed to `智能体使用情况`
  - tool section is renamed to `工具使用情况`
  - conversations are presented as `近期对话`
  - filters and action labels are clearer

## Validation
- `pnpm build` in `web/` passed.
- `npm run docs:build` passed.

## Phase Judgment
- Current phase: `v1.1`
- Readiness for next sub-wave: `ready`
- Main remaining gap: continue only with low-risk visible-layer polish, not core runtime changes.

