# 对齐

## 目标

完善知识库详情页的检索参数配置体验，让前端完整承接后端 `GET/PUT /api/knowledge/databases/{db_id}/query-params` 暴露的能力，同时保持页面简洁、中文清晰。

## 范围

- 优化检索配置弹窗的中文文案、参数分组、摘要和后端请求预览。
- 覆盖 Milvus、LightRAG、Dify 的动态 options，不硬编码为单一知识库类型。
- 保存配置后同步到 `databaseStore.meta`，保证检索测试和 RAG 评估继续使用后端保存的参数。

## 不做

- 不改后端查询参数契约。
- 不改知识库创建流程。
- 不改图谱查询接口或 RAG 评估业务逻辑。

## 验收

- 弹窗默认展示核心摘要，不把所有说明铺满页面。
- 详细配置中能看到 Reranker、召回、阈值、Dify 映射、LightRAG 图谱内容范围等后端参数。
- 后端请求预览能清楚显示 `PUT /query-params` 的 payload。
- 构建通过，CDP QA 能验证 UI 和保存 payload。
