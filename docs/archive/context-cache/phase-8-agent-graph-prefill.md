# Phase 8 Agent / Graph Prefill

## Goal
- 在不触碰高风险核心层的前提下，完成平台层最后一段最小联动。
- `/agent` 在存在 PoE 推荐上下文时，展示更明确的欢迎提示与可直接复用的提问建议。
- `/graph` 在存在 PoE 图谱闭环上下文时，自动预填更合适的默认查询关键词。

## Stable Decisions
- 本轮只允许修改前端页面层和前端本地数据适配层。
- 推荐欢迎提示不直接侵入聊天内核，只作为页面顶部的上下文提示面板存在。
- 图谱默认关键词直接从闭环样本数据推导，优先级为：
  1. `Build`
  2. `SkillGem`
  3. `Mechanic`
  4. `Ascendancy`
  5. `Class`
- 如果用户已有输入，则不覆盖现有查询词。

## Changed Surface
- `web/src/data/poePhase1.js`
  - 新增图谱默认关键词推导 helper。
- `web/src/views/AgentView.vue`
  - 新增推荐欢迎提示面板。
  - 新增可复制的建议提问 chips。
- `web/src/views/GraphView.vue`
  - 根据当前 `themeContext.graph` 自动预填 `searchInput`。

## Validation Snapshot
- `pnpm build` in `web/`: passed
- `GET http://localhost:5173/agent`: `200`
- `GET http://localhost:5173/graph?theme=poe&module=poe&scene=graph_loop&version=phase2&graph=poe-necromancer-minion-loop`: `200`

## Risks
- `/agent` 当前只是在页面层表露推荐欢迎提示，还没有把这些建议提问真正注入聊天输入框。
- `/graph` 当前只预填关键词，不会自动触发查询，避免误伤通用图谱页行为。
- 图谱默认关键词依赖样本闭环节点质量，后续如果闭环数据扩展，需要继续复核关键词优先级。

## Next Step
- 下一阶段可以进入“PoE 模块演示收口”：把主题页、Agent 页、Graph 页串成一条答辩演示路径，并补一页更明确的 Demo Script / Thesis Materials 联动说明。
