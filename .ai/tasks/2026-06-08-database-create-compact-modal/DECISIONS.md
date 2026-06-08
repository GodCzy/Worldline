# 决策

## 保留后端契约

- 不改 `server/routers/knowledge_router.py`。
- 通过前端信息架构调整完成本阶段目标。

## 主表单收敛

- 分块预设仍留在主表单，因为它是非 Dify 创建路径的核心选择。
- `chunk_parser_config`、RAPTOR、GraphRAG 放入“分块解析”抽屉。
- `ShareConfigForm` 放入“共享设置”抽屉，主表单只显示摘要。

## 请求预览

- 请求预览改为抽屉，继续调用 `buildRequestData()`。
- Dify Token 继续通过 `maskSensitiveCreatePayload()` 遮罩。
