# Phase 87 - Worldline Phase 7-10 重排总计划基线

## Status
- 当前状态：active baseline
- 生效日期：2026-04-15
- 适用范围：Worldline 后续 Phase 7、8、9、10

## 宗旨
从本文件开始，Worldline 不再沿用旧的 7/8/9/10 线性拆法。
后续阶段按“品牌与治理先收敛、多模块再验证、后端与算法再重构、数据库与数据链路最后标准化”的顺序推进。

## 阶段重排

### Phase 7：全仓品牌与文档治理重构
目标：
- 把活跃源码、配置、构建、运行、测试、主文档中的 legacy brand tokens 切换为 `Worldline`
- 压缩 Markdown 文档体系
- 重构 `AGENTS.md` 与 `CODEX_WORKFLOW.md`

主线：
- 活跃环境变量统一为 `WORLDLINE_*`
- 活跃包名、镜像名、默认数据库名、日志前缀统一为 `worldline*`
- 历史 evidence 不改写，但退出主阅读面
- `docs/` 重新分层为：
  - Canonical Docs
  - Phase Baselines
  - Historical Archive
  - Immutable Evidence

完成标准：
- 活跃源码 / 配置 / 构建 / 测试 / 主文档不再出现 legacy brand tokens
- 主阅读面只保留 Worldline 文档
- `AGENTS.md` 与 `CODEX_WORKFLOW.md` 去重完成
- 构建与基础 smoke 不回退

### Phase 8：多模块平台验证 + 模块运营化收口
目标：
- 合并原先 Phase 7 和 Phase 8
- 引入第三模块验证平台契约
- 把 `worldline-ops` 从试点骨架收口为可运营模块

默认第三模块：
- `worldline-sandbox`

完成标准：
- 三个模块并存且可发现
- 共享页继续只认 facade
- `worldline-ops` 成为可运营模块
- 形成统一多模块 smoke / evidence / release gate 基线

### Phase 9：后端服务层重构 + 算法与运行优化
目标：
- 清理后端结构债
- 收敛 router / service / knowledge / graph 边界
- 统一 chunking、retrieval、ranking、graph fallback 策略
- 增强 degraded mode、可观测性和错误定位

完成标准：
- 公开系统接口不再被知识/图谱初始化硬阻塞
- router / service / knowledge 边界清晰
- chunking / retrieval / graph fallback 有统一策略
- 后端运行行为更可观测、更可定位、更可降级

### Phase 10：数据库与知识数据链路标准化
目标：
- 统一 PostgreSQL 命名与连接策略
- 明确 metadata / indexing / graph / migration 边界
- 标准化健康检查、降级、重建与迁移入口

完成标准：
- 默认数据库名统一为 `worldline_know`
- 元数据 / 索引 / 图谱边界稳定
- 迁移脚本、健康检查、故障降级形成标准路径
- 数据层具备长期企业化演进基础

## Canonical Naming

### 产品与包名
- 产品名：`Worldline`
- Python package：`worldline`
- Web package：`worldline-web`

### Docker
- `worldline-api`
- `worldline-web`

### 默认数据库
- `worldline_know`

### 环境变量
Canonical：
- `WORLDLINE_SUPER_ADMIN_NAME`
- `WORLDLINE_SUPER_ADMIN_PASSWORD`
- `WORLDLINE_SKIP_APP_INIT`
- `WORLDLINE_BRAND_FILE_PATH`
- `WORLDLINE_URL_WHITELIST`

Deprecated compatibility：
- Phase 7-8 允许读取 legacy env aliases
- 代码必须优先读 `WORLDLINE_*`
- 若回退读到 legacy env aliases，必须记录 deprecation warning
- Phase 9 结束前删除兼容别名

### 内部常量
- `WORLDLINE_CHUNK_DELIM`
- `worldline-*` logs / temp / runtime naming

## 文档治理默认规则

### 活跃文档
Canonical Docs 默认保留：
- `README.md`
- `docs/index.md`
- `docs/platform-architecture.md`
- `docs/frontend-architecture.md`
- `docs/backend-architecture.md`
- `docs/module-extension.md`
- `docs/operations-and-validation.md`
- `AGENTS.md`
- `CODEX_WORKFLOW.md`

### 基线与归档
- 只保留最近两个阶段仍有活跃引用价值的 baseline / signoff
- 早期编号文档、旧 phase 微步骤文档、旧里程碑文档进入 archive
- `artifacts/qa-*` 作为 immutable evidence 保留，不改写内容

### 历史 evidence 处理
- 活跃源码、配置、构建、测试、主文档：彻底去 legacy brand tokens
- 历史 evidence / 旧 phase 证据：不改写内容，只退出主阅读面

## 协作规则重构目标

### AGENTS.md
仅保留长期稳定规则，建议固定为：
1. Project Identity
2. Product and Architecture Rules
3. Execution Model
4. Skill and MCP Policy
5. Delivery Contract
6. Phase Judgment Rule

### CODEX_WORKFLOW.md
承载会随阶段变化的操作性规则：
- bootstrap 顺序
- context-cache 使用原则
- phase baseline 更新规则
- build / smoke / git commit 触发条件
- Playwright / PostgreSQL / GitHub / Fetch MCP 使用判断

## 本轮执行默认子代理

### 第一波：只读设计与映射
- `system_mapper`
- `product_architect`
- `qa_release_auditor`

### 第二波：实现
- `frontend_worker`
- `backend_worker`
- `knowledge_rag_engineer`
- `agent_architect`

## 当前任务解释
从当前对话开始，仓库已进入新的 `Phase 7`。
本轮唯一主线是：
- 品牌统一
- 文档治理
- 协作规则重构

不在本轮扩功能，不提前进入多模块扩展、后端算法重构或数据库标准化主战场。

## 当前阶段最小验收基线
- `pnpm --dir web build`
- `npm run docs:build`
- grep 检查活跃源码 / 配置 / 主文档中不再出现 legacy brand tokens
- 主入口不回退：
  - `/api/system/info`
  - `/api/system/health`
  - `/themes`
  - `/worldline`
  - `/agent`
  - `/graph`

## Phase Judgment
- 当前阶段：`Phase 7`
- 对下一阶段的判定原则：
  - 先完成活跃身份与治理规则收敛
  - 再进入多模块平台验证
  - 不跳阶段
