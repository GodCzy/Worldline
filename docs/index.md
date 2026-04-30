---
layout: home
title: Worldline 文档中心
hero:
  name: Worldline
  text: Phase 7 文档治理基线
  tagline: 面向企业级知识平台的主文档入口，强调平台层与模块层边界、运行验证路径与历史归档分工。
  actions:
    - theme: brand
      text: 平台架构
      link: /platform-architecture
    - theme: alt
      text: 运维与验证
      link: /operations-and-validation
features:
  - title: Canonical Docs
    details: 主阅读面只保留当前产品有效文档，用于开发、运营、验证与协作。
  - title: Archive
    details: 历史阶段材料集中在 archive，仅用于审计追溯，不作为默认实施依据。
  - title: Context Cache
    details: context-cache 只保留当前活跃阶段与最近收口基线，旧缓存转入归档。
---

## 当前基线

- 当前阶段：`Phase 7`（品牌与文档治理重构）
- 最近完成：`Phase 6` 第二模块 `worldline-ops` 最小试点与 runtime smoke
- 本阶段重点：活跃面统一 Worldline 口径，不扩业务功能

## Canonical Docs（主阅读面）

1. 仓库根 `README.md`
2. [平台架构](/platform-architecture)
3. [前端架构](/frontend-architecture)
4. [后端架构](/backend-architecture)
5. [模块扩展](/module-extension)
6. [运维与验证](/operations-and-validation)

## Archive 与 Context Cache 分工

- [历史归档](/archive/)：历史方案、旧阶段文档、旧缓存总入口
- `docs/context-cache/`：仅保留当前阶段与最近阶段收口文档
- `docs/archive/context-cache/`：旧缓存归档区

默认阅读路径：
先读 Canonical Docs，只有在审计追溯或对比历史方案时才进入 archive。
