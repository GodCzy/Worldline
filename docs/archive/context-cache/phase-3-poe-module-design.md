# 世界线 Phase 3 PoE Module Design

## Goal

只完成 PoE 模块设计收敛，不进入大规模实现。

## Stable Decisions

- PoE 首期采用 7 个一级知识类目：
  - `class_ascendancy`
  - `skill_support`
  - `item_build`
  - `mechanic_defense`
  - `progression_growth`
  - `league_patch`
  - `faq_pitfall`
- 内容类型固定为 6 类：
  - `concept_card`
  - `build_card`
  - `progression_card`
  - `faq_card`
  - `patch_note_card`
  - `recommendation_card`
- `data/poe/metadata-schema.json` 升级为 PoE 的统一契约，面向检索、Agent 模板、图谱和推荐共用。
- PoE 回答模板首期固定 5 套：
  - `mechanic_explainer`
  - `build_recommendation`
  - `progression_guide`
  - `item_choice`
  - `faq_quick_answer`
- 图谱首期只保证最小闭环：
  - `Class -> Ascendancy -> Build -> SkillGem -> UniqueItem -> Mechanic -> KnowledgeCard`
- 推荐 MVP 采用规则打分，不做机器学习。

## Allowed Files

- `docs/02-poe-knowledge-schema.md`
- `data/poe/metadata-schema.json`
- `data/poe/raw/`
- `data/poe/processed/`
- 后续低风险平台承接点：
  - `src/config/static/info.template.yaml`
  - `web/src/stores/themeContext.js`
  - `web/src/views/themes/ThemeDetailView.vue`
  - `web/src/views/AgentView.vue`
  - `server/routers/chat_router.py`
  - `server/routers/knowledge_router.py`
  - `server/routers/graph_router.py`

## High-Risk Files Still Blocked

- `src/knowledge/base.py`
- `src/knowledge/manager.py`
- `src/knowledge/implementations/lightrag.py`
- `src/agents/common/base.py`
- `src/agents/chatbot/graph.py`
- `src/services/chat_stream_service.py`
- `src/services/agent_run_service.py`

## Next Step

进入 PoE 最小实现准备：

1. 先产出 10 到 15 张高质量 PoE 样本知识卡
2. 再把 metadata 契约接到知识导入数据
3. 再做 3 条图谱闭环链路
4. 最后接推荐 MVP 与 Agent 模板
