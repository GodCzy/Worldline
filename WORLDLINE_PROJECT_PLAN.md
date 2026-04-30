# Worldline 项目总计划（Phase 7-10）

## 1. 项目定位

Worldline 是企业级知识平台，不再以历史项目名称或单模块形态定义当前产品身份。平台目标是长期支撑：

- 多模块知识接入
- 检索与图谱推理
- Agent 协作流程
- 运营与发布前验证

## 2. 当前阶段

- 当前阶段：`Phase 7`（全仓品牌与文档治理重构）
- 已完成基线：`Phase 6` 第二模块 `worldline-ops` 最小接入试点
- 本轮边界：只做命名统一与文档体系治理，不扩展功能

## 3. Phase 7-10 路线

### Phase 7：品牌与文档治理重构

- 活跃源码、配置、构建、测试、主文档统一到 Worldline 口径
- 主阅读面突出 Canonical Docs
- archive/context-cache/evidence 分工收敛

### Phase 8：多模块平台验证与模块运营化收口

- 引入第三模块完成接入验证
- 形成统一的多模块 smoke 与验收基线
- `worldline-ops` 从骨架收口为可运营模块

### Phase 9：后端服务层重构与算法运行优化

- router/service/knowledge/graph 边界收敛
- chunking/retrieval/ranking/fallback 策略统一
- 提升降级可控性与可观测性

### Phase 10：数据库与知识数据链路标准化

- 默认数据库名、连接策略、迁移与健康检查标准化
- metadata/indexing/graph 边界明确
- 数据层演进路径稳定化

## 4. 文档治理约束

- Canonical Docs：当前实施口径文档
- Archive：历史文档与旧阶段材料
- Context Cache：当前阶段与最近阶段收口基线
- Immutable Evidence：`artifacts/qa-*`，保留原样不改写

## 5. 本阶段验收建议

```powershell
pnpm --dir web build
npm run docs:build
```

并执行活跃文档与前端包信息的品牌残留扫描（期望零命中）。

并执行入口 smoke：

- `/api/system/info`
- `/api/system/health`
- `/themes`
- `/worldline`
- `/agent`
- `/graph`

## 6. 阶段判断

- 当前阶段：`Phase 7 进行中`
- 进入下一阶段前主缺口：完成活跃面口径统一后的回归验证与收口确认
