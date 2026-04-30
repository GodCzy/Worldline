# 平台架构

## 产品定位

Worldline 是企业级知识平台，不是单一主题站点，也不是单纯聊天应用。  
平台层负责稳定入口、共享布局、权限、上下文切换、运维验证和模块接入；模块层负责各自的知识结构、推荐逻辑、图谱语义与业务资产。

## Phase 5 架构目标

1. 把共享视图从 PoE 直连改为平台 facade。
2. 保持 `/agent`、`/graph`、`/worldline`、`/themes` 等主路由稳定。
3. 保持 Phase 4 已锁定的 graph/auth 权限边界稳定。
4. 让文档站表达当前产品结构，而不是继续堆叠历史阶段过程。

## 平台层与模块层边界

### 平台层

- 品牌与信息入口：`/api/system/info`
- 主路由与权限守卫：前端 router + user store
- 共享布局：`layouts/*`
- 共享视图：`/agent`、`/graph`、`/worldline`
- 验收与 replay：脚本、文档、evidence contract

### 模块层

- 模块知识卡、图谱、推荐候选
- 模块默认问题与展示标签
- 模块专属世界线生成逻辑
- 模块专属文案和资产

## 当前实现原则

- 平台共享视图只依赖 worldline adapter facade，不直接 import PoE 数据。
- 模块通过 `web/src/data/worldline/*` 暴露能力，而不是把模块内部文件路径暴露给共享页面。
- 后端结构收敛以兼容为前提，只清理入口组织和职责边界，不做协议级破坏性调整。
