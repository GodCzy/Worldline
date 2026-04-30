# Worldline

Worldline 是一个企业级知识平台，面向复杂领域知识的接入、检索、图谱推理、Agent 协作与运营管理。

## 当前阶段

- 当前阶段：`Phase 7`（全仓品牌与文档治理重构）
- 已完成基线：`Phase 6` 第二模块 `worldline-ops` 最小接入与 runtime smoke
- 本阶段目标：活跃源码、配置、构建、测试与主文档统一到 Worldline 产品口径，并收敛主阅读面

## 主要入口

- 前端首页: [http://localhost:5173/](http://localhost:5173/)
- 主题分区: [http://localhost:5173/themes](http://localhost:5173/themes)
- Worldline Hub: [http://localhost:5173/worldline](http://localhost:5173/worldline)
- Agent: [http://localhost:5173/agent](http://localhost:5173/agent)
- Graph: [http://localhost:5173/graph](http://localhost:5173/graph)
- 系统信息: [http://localhost:5050/api/system/info](http://localhost:5050/api/system/info)
- 健康检查: [http://localhost:5050/api/system/health](http://localhost:5050/api/system/health)
- 文档站: [http://localhost:5174](http://localhost:5174)

## 启动

```powershell
Copy-Item .env.template .env
docker compose up -d
```

## 验证建议

```powershell
pnpm --dir web build
npm run docs:build
```

命名与文档口径门槛建议：对活跃主文档与前端包信息执行一次品牌残留扫描，确认无历史前缀命中。

运行入口 smoke 建议：

- `/api/system/info`
- `/api/system/health`
- `/themes`
- `/worldline`
- `/agent`
- `/graph`

## Canonical Docs

- 文档首页: [docs/index.md](docs/index.md)
- 平台架构: [docs/platform-architecture.md](docs/platform-architecture.md)
- 前端架构: [docs/frontend-architecture.md](docs/frontend-architecture.md)
- 后端架构: [docs/backend-architecture.md](docs/backend-architecture.md)
- 模块扩展: [docs/module-extension.md](docs/module-extension.md)
- 运维与验证: [docs/operations-and-validation.md](docs/operations-and-validation.md)

## Archive 与 Context Cache 分工

- `docs/archive/`：历史方案与旧阶段文档归档，不作为默认阅读入口
- `docs/context-cache/`：当前活跃阶段基线与最近阶段收口摘要
- `docs/archive/context-cache/`：旧阶段缓存归档
- `artifacts/qa-*`：审计证据，保留原样，不并入主文档叙事

## Phase Judgment

- 当前阶段：`Phase 7`
- 进入下一阶段前主缺口：完成活跃面命名切换与文档治理的全仓回归验证
