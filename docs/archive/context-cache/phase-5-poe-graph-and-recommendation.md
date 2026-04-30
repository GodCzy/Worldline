# 世界线 Phase 5 PoE Graph And Recommendation

## Goal

基于现有 13 张 PoE 样本卡，补齐可展示的图谱闭环数据和推荐 MVP 候选集。

## Stable Decisions

- 图谱样本采用纯 JSON 数据文件，不接运行时代码。
- 本轮固定生成 3 条闭环：
  - `poe-necromancer-minion-loop`
  - `poe-deadeye-mapping-loop`
  - `poe-boneshatter-melee-loop`
- 推荐 MVP 候选集采用单文件聚合：
  - `data/poe/processed/recommendation/phase1-candidates.json`
- 候选集固定包含 3 条推荐方向：
  - 死灵师低预算召唤
  - 锐眼远程快刷
  - 碎骨近战推进
- 所有图谱与推荐文件都已经通过对现有 `cards/manifest.json` 的引用一致性校验。

## Allowed Files

- `data/poe/processed/graph/**`
- `data/poe/processed/recommendation/**`
- `docs/context-cache/phase-5-poe-graph-and-recommendation.md`

## High-Risk Files Still Blocked

- `src/knowledge/base.py`
- `src/knowledge/manager.py`
- `src/knowledge/implementations/lightrag.py`
- `src/agents/common/base.py`
- `src/agents/chatbot/graph.py`
- `src/services/chat_stream_service.py`
- `src/services/agent_run_service.py`

## Next Step

1. 让前端或脚本层能够读取 `phase1-candidates.json`
2. 让图谱页先消费 3 条闭环数据做最小展示
3. 再把 `theme_context.scene` 与推荐候选和图谱入口联动
4. 最后才考虑把这些数据接进知识导入和 Agent 检索过滤
