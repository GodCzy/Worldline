# Phase 30 - 本地聊天模型切换到火山引擎 Ark 接入点

## 结论

- 当前本地运行环境已将世界线默认聊天模型从旧聊天线路切换到火山引擎 Ark。
- 切换方式采用本地运行配置覆盖，不重写仓库默认模型栈。
- 本轮仅覆盖聊天相关模型：
  - `default_model`
  - `fast_model`
  - `content_guard_llm_model`
- Embedding 与 Reranker 暂不在本轮切换范围内。

## 本地运行配置

- `.env` 新增：
  - `ARK_API_KEY`
- `saves/config/base.toml` 新增：
  - `default_model = "ark/ep-20260320171357-zqd6p"`
  - `fast_model = "ark/ep-20260320171357-zqd6p"`
  - `content_guard_llm_model = "ark/ep-20260320171357-zqd6p"`

## 约束

- 这是本地运行时切换，不是仓库默认模型配置重构。
- 如果后续要把 Embedding、Reranker、知识导入与评测链路也一并切到 Ark，需要另开版本任务处理。

## 核心验证

- API 与 worker 重启后保持健康。
- 登录接口正常。
- 默认智能体接口正常。
- 底层模型直接调用可返回文本。
- Agent 流式链路已不再出现旧的 `403 insufficient balance`。

## 兼容性补丁

- 进一步验证发现，当前 Ark 接入点的流式输出会把正文主要放在 `reasoning_content`，而不是旧链路默认依赖的 `content`。
- 为了保证 Agent 页面能看到实际回复，本轮对 `src/services/chat_stream_service.py` 做了最小兼容补丁：
  - 优先读取 `content`
  - 若为空，回退读取 `reasoning_content`
- 该修改只影响流式 chunk 的文本提取，不改变模型选择、Agent 架构或知识链路。

## 阶段判断

- 当前阶段：`v1.1 最终验收执行`
- 下一阶段 readiness：`ready`
- 进入下一阶段前的主要 gap：如果要把 Ark 从“本地可用聊天线路”提升为“统一模型栈”，还需要单独评估 Embedding、Reranker 与相关治理策略。
