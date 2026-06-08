# 决策记录

## 以垂直切片替代大阶段口号

原因：Worldline 同时涉及知识编译、Wiki、图谱、UI、Agent 和评估。如果按模块平铺，容易出现每层都有半成品但没有可验证闭环。后续 P3 应先做单文档到 Wiki/Graph/Branch/Gate 的最小闭环。

## RAG 继续作为支持层

原因：现有项目定位要求 LLM Wiki、Evidence Graph 和 Temporal KG 是核心资产。Milvus、LightRAG、LlamaIndex、BM25、graph traversal 用于 evidence recall 和质量门禁覆盖，不决定主界面或可信度。

## MCP 默认只保留受控 Worldline 边界

原因：外部 Agent 写入必须经过 Worldline service boundary、权限检查和审计日志。数据库直写 MCP、全盘 filesystem MCP、shell MCP 不进入默认路线。

## 紧凑控制台是产品要求

原因：复杂后端能力已经存在，UI 应把复杂配置放入按钮、抽屉、命令面板和详情窗，不把第一屏变成配置表单或营销页。
