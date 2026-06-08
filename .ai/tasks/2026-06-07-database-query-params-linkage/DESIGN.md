# 设计

## UI 结构

检索配置弹窗保持一个入口：

- 顶部：后端联通说明和当前知识库类型。
- 摘要：优先展示 4 个核心参数，例如检索模式、返回数量、Reranker、阈值。
- 参数区：按“检索范围”“重排序”“阈值与输出”“高级”分组，动态渲染后端 options。
- 预览区：折叠展示 `PUT /api/knowledge/databases/{db_id}/query-params` 请求体。

## 数据流

1. 弹窗打开时调用 `queryApi.getKnowledgeBaseQueryParams(databaseId)`。
2. 将后端 `params.options` 作为唯一参数来源，合并默认值到本地 `meta`。
3. 保存时调用 `queryApi.updateKnowledgeBaseQueryParams(databaseId, payload)`。
4. 成功后写入 `databaseStore.meta`，并刷新 `databaseStore.loadQueryParams(databaseId)`。

## 风险

- 当前组件曾把配置写入 localStorage，容易造成后端保存值和本地值不一致。本次调整以后端为主，localStorage 仅不再作为配置真相。
- `include_distances` 后端有选项但前端以前隐藏。本次保留默认 `true` 并在预览里透明展示。
