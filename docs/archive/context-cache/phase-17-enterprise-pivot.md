# 世界线 Phase 17 企业化战略转向

## Goal

- 将项目叙事从早期阶段性交付转向企业级产品演进。
- 保留此前对话沉淀下来的稳定结论，作为后续版本升级的压缩工作记忆。
- 新增一份大体量的版本演进路线文档，作为未来多个版本的上位规划依据。

## Historical Summary

到本阶段为止，仓库已经完成了以下关键里程碑：

1. 平台层基础完成：
   - 世界线品牌
   - 首页、主题分区、导航和路由
   - 主题上下文在主题页、Agent、Graph 之间透传
2. PoE 首期模块完成：
   - 样本知识卡
   - 推荐候选集
   - 图谱闭环样本
   - Agent / Graph 页面联动
3. 运行与交付基础完成：
   - Docker 本地运行链路可用
   - 文档站、使用教程、测试手册已形成
   - `v1.0.0` 基线已建立
4. 展示层关键问题已处理：
   - PoE 数据加载问题修复
   - 浏览器标题与品牌修复
   - Agent 页面输入区首屏可见问题修复

## New Strategic Position

从本阶段开始：

- 不再将世界线定义为“毕业设计项目”
- 不再将世界线定义为“上游项目的对外延伸版本”
- 将世界线定义为一个企业级知识平台产品
- 此前的答辩、演示、阶段性文档只保留为历史阶段材料

## Stable Decisions

- 未来版本规划以企业化能力为目标：
  - 知识接入
  - 知识治理
  - RAG 质量
  - 图谱生产化
  - 推荐系统升级
  - 权限与审计
  - 多智能体编排
  - 观测与运营
- 保持平台层与模块层分离仍然是长期原则。
- 当前 PoE 模块继续作为最成熟业务模块，但不再是产品定位本身。

## New Primary Planning Document

- 新增 `docs/09-enterprise-evolution-roadmap.md`
- 该文档作为后续 `v1.1` 及以上版本的主路线图

## Allowed Files For This Pivot

- `AGENTS.md`
- `README.md`
- `docs/index.md`
- `docs/09-enterprise-evolution-roadmap.md`
- `docs/context-cache/phase-17-enterprise-pivot.md`

## Blocked Files

- 本轮不触碰高风险核心层实现：
  - `src/knowledge/**`
  - `src/agents/common/**`
  - `src/services/chat_stream_service.py`

## Validation Snapshot

- 本轮主要是战略文档和规则层更新
- 后续应执行 `npm run docs:build` 验证文档站

## Next Step

- 基于新路线图收敛 `v1.1` 范围
- 输出企业化能力分级文档
- 按版本节奏逐步替换旧叙事入口文档
