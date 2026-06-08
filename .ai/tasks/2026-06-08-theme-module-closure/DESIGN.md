# Design

## 后端

`server/routers/system_router.py` 继续用 JSON 文件保存自定义主题模块，但规范化时补齐：

- `knowledge` 子对象：知识库 ID、名称、类型、描述、证据来源。
- `worldline.objective`、`worldline.evidence_sources`、`worldline.generation`。
- `worldline.surfaces` 扩展到 Wiki、Graph、Timeline、Quality Gate、MCP、Workflow。
- `context` 保留默认问题、目标、证据来源和知识库信息。

保持兼容：现有 `db_id`、`knowledge_db_id`、`worldline.default_question` 和旧 4 个 surface 字段仍可读。

## 前端

- `worldlineCapabilities.js` 扩展 surface 定义，让 MCP 和 Workflow 可被开关控制。
- `ThemeHubView.vue` 保持主弹窗简洁：模块名、知识库、目标、证据来源、短描述。生成配置、能力地图和 payload 放进抽屉。
- `DataBaseView.vue` 跳转到 `/themes?new_module=1` 时带上知识库描述和类型。
- `ThemeDetailView.vue` 和 `WorldlineWorkbenchView.vue` 用 query/context 继续传递 `knowledge_db_id`。

## 验证

- 后端 focused pytest 覆盖 theme payload 归一化。
- 前端 build 覆盖 Vue 编译。
- 浏览器 QA 覆盖创建、详情、工作台的真实路由。
