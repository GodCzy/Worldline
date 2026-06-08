# Alignment

日期：2026-06-08

## 目标

完成 P1「主题分区自定义模块闭环」：自定义主题模块应能从知识库上下文创建、保存到后端、读回、在主题详情展示绑定知识库和能力摘要，并进入 `/worldline/:themeId` 使用正确知识库生成或查看世界线。

## 验收

- `/themes?new_module=1` 能打开新建模块流程。
- 从 `/database` 的“创建主题模块”跳转能携带知识库 ID、名称、描述和类型。
- 模块 payload 覆盖目标、证据来源、Worldline 生成配置、Wiki/Graph/Timeline/Gate/MCP/Workflow 能力开关。
- `POST/PUT/GET /api/system/themes` 保留 `context`、`knowledge`、`worldline`、`metadata` 的兼容结构。
- 主题详情显示绑定知识库、能力摘要、入口和可解释空态。
- `/worldline/:themeId` 基于主题模块解析 `knowledge_db_id`。
- 完成 focused test、前端 build、桌面和 390px 移动截图 QA。

## 边界

- 不回滚当前脏工作树中的未知修改。
- 不改数据库 schema。
- 不把复杂配置铺满页面；放进按钮、抽屉或预览。
- 不把临时管理员密码、token 或本地凭据写入仓库或总结。
