# 运维与验证

## Phase 7 验证目标

本阶段只做品牌与文档治理重构，验证目标是确保：

- 活跃主文档口径统一为 Worldline enterprise platform
- 主阅读面和 archive/context-cache 职责清晰
- 前端构建和文档构建不回退
- 核心入口 smoke 路径可复用

## 构建验证

```powershell
pnpm --dir web build
npm run docs:build
```

## 命名与口径门槛

建议在活跃主文档与前端包信息上执行一次品牌残留扫描。

期望结果：无历史前缀命中。

## 运行入口 smoke

建议保留以下入口作为回归门槛：

- `/api/system/info`
- `/api/system/health`
- `/themes`
- `/worldline`
- `/agent`
- `/graph`

## 文档分工约束

- Canonical Docs：`README.md` 与 `docs/` 主入口文档，承载当前实施口径
- Archive：`docs/archive/`，承载历史方案与旧阶段文档
- Context Cache：`docs/context-cache/`，仅保留当前活跃阶段与最近收口基线
- 历史 evidence：`artifacts/qa-*` 保留原样，不改写、不混入主阅读面

## 备注

本阶段不扩展业务功能，不引入新的模块能力，只做命名与文档治理收敛。
