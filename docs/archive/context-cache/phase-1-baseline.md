# 世界线 Phase 1 Baseline

## 项目身份

- 项目名：世界线（Worldline）
- 性质：基于 Yuxi-Know 的毕业设计级二次开发与产品化改造
- 目标：保留现有知识库管理、RAG 检索、知识图谱、智能体与后台配置能力
- 首期主题：仅完整落地《流放之路》模块

## 当前原则

- 先理解仓库，再改代码
- 先平台层，后 PoE 模块
- 先文档化方案，再最小实现
- 不大范围重构无关代码
- 平台层与模块层必须分离

## 多 Agents 架构

- 主控代理：负责理解任务、调度子代理、汇总结果、输出最终执行方案
- `repo_mapper`：负责仓库结构映射、入口点识别、平台层/模块层/高风险层分类
- `platform_architect`：负责世界线平台层改造方案
- `poe_designer`：负责 PoE 模块知识设计、metadata、问答模板、图谱设计、推荐 MVP
- `implementer`：在边界明确后做最小改动实现

## 当前仓库的物理结构

- 前端：`web/`
- 后端 HTTP 入口：`server/`
- 核心服务与领域逻辑：`src/`
- 文档：`docs/`
- 数据骨架：`data/poe/`
- Codex 配置：`.codex/`

## 当前仓库的逻辑分层

### 平台层

- 品牌、文档、导航、首页展示、平台说明
- 共用知识库管理、RAG、图谱、智能体、后台配置能力

### 模块层

- 主题知识分类
- 主题 metadata
- 主题问答模板
- 主题图谱 schema
- 主题推荐逻辑

### 高风险核心层

以下区域优先保持稳定，后续只做谨慎扩展：

- `src/knowledge/base.py`
- `src/knowledge/manager.py`
- `src/knowledge/implementations/lightrag.py`
- `src/agents/common/base.py`
- `src/agents/chatbot/graph.py`
- `src/services/chat_stream_service.py`
- `src/services/agent_run_service.py`

## 第一次提交包含内容

- 建立世界线专属 `AGENTS.md`
- 建立 `.codex` 多 agents 配置
- 重写根目录 `README.md`
- 建立根目录方案文档 `WORLDLINE_PROJECT_PLAN.md`
- 重建 `docs/` 为世界线专属文档体系
- 创建 `data/poe/` 数据骨架与 `metadata-schema.json`
- 修改首页与布局中的 Yuxi 专属外链与品牌信息
- 删除原有与后续项目无关的旧文档内容

## 明确未做的事情

- 未改动 RAG 内核逻辑
- 未改动知识图谱核心实现
- 未改动 Agent 编排核心逻辑
- 未建立真正的 PoE 业务页面与模块服务
- 未完成平台层的模块上下文切换机制

## 下一阶段建议目标

目标：完成“世界线平台层最小可运行改造方案”和第一轮最小实现。

优先级：

1. 明确首页、路由、导航、模块入口的最小改造面
2. 定义平台层与模块层的目录和上下文边界
3. 为 PoE 模块预留独立入口，但不侵入核心通用层
4. 在完成方案后，再由 `implementer` 做最小实现

## 下一阶段建议阅读顺序

1. `AGENTS.md`
2. `WORLDLINE_PROJECT_PLAN.md`
3. `docs/01-platform-architecture.md`
4. `docs/02-poe-knowledge-schema.md`
5. `docs/03-implementation-roadmap.md`
6. `web/src/router/index.js`
7. `web/src/layouts/AppLayout.vue`
8. `web/src/views/HomeView.vue`
9. `server/main.py`
10. `server/routers/__init__.py`

## 给后续 Codex 的执行约束

- 优先使用多 agents 方式推进
- 先输出文件级实施方案，再改代码
- 所有实现必须说明：
  - changed files
  - why changed
  - how to run/validate
  - remaining risks
