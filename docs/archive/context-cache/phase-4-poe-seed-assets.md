# 世界线 Phase 4 PoE Seed Assets

## Goal

完成 PoE 首批样本知识资产的最小实现，不进入高风险核心层修改。

## Stable Decisions

- 首批 PoE 样本卡片实际落地为 `13` 张独立 JSON 卡片。
- 数据目录采用按 `category` 分桶的结构：
  - `data/poe/processed/cards/class_ascendancy/`
  - `data/poe/processed/cards/skill_support/`
  - `data/poe/processed/cards/item_build/`
  - `data/poe/processed/cards/mechanic_defense/`
  - `data/poe/processed/cards/progression_growth/`
  - `data/poe/processed/cards/faq_pitfall/`
  - `data/poe/processed/cards/league_patch/`
- 增加 `data/poe/processed/cards/manifest.json` 作为样本索引，记录数量、路径、分类和内容类型。
- 所有卡片均通过 `data/poe/metadata-schema.json` 校验。
- 首批卡片覆盖的内容类型为：
  - `concept_card`
  - `build_card`
  - `progression_card`
  - `faq_card`
  - `patch_note_card`
  - `recommendation_card`

## Allowed Files

- `data/poe/processed/cards/**`
- `data/poe/metadata-schema.json`
- `docs/context-cache/phase-4-poe-seed-assets.md`

## High-Risk Files Still Blocked

- `src/knowledge/base.py`
- `src/knowledge/manager.py`
- `src/knowledge/implementations/lightrag.py`
- `src/agents/common/base.py`
- `src/agents/chatbot/graph.py`
- `src/services/chat_stream_service.py`
- `src/services/agent_run_service.py`

## Next Step

1. 把这 13 张卡接入后续知识导入样本
2. 基于卡片里的 `graph_entities` 和 `graph_relations` 生成 3 条图谱闭环
3. 基于 `recommendation_card` 和 manifest 生成推荐 MVP 候选集
4. 最后再把 `theme_context` 真正约束到 Agent 和知识库查询过滤
