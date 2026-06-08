# 设计

## 信息架构

- 主 Modal：知识库类型、名称、描述、非 Dify 的嵌入模型和分块策略、LightRAG 的语言和 LLM、Dify 的 URL/Token/Dataset ID。
- 摘要卡片：后端配置、分块解析、共享设置、创建请求。
- 抽屉：
  - 高级后端配置：`is_private`、`storage`。
  - 分块解析：`chunk_parser_config`、RAPTOR、GraphRAG。
  - 共享设置：`ShareConfigForm`。
  - 创建请求预览：遮罩 Dify Token 后的 payload。

## 契约

- 不改后端 route、service、model 或数据库 schema。
- 继续使用 `buildRequestData()` 生成：
  - `database_name`
  - `description`
  - `embed_model_name`
  - `kb_type`
  - `additional_params`
  - `llm_info`
  - `share_config`
