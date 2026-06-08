# Design

## UI

`WikiSection.vue` 放在知识库详情右侧 tab 区：

- 顶部：标题、刷新、重建。
- 统计：页面数、支持主张、引用数、stale 数。
- 左侧：Wiki 页面列表。
- 右侧：当前页面的 review、coverage、freshness、claims、citations、open questions。
- Drawer：完整 Markdown 详情。

## API

复用现有后端接口：

- `GET /api/knowledge/databases/{db_id}/wiki/pages`
- `GET /api/knowledge/databases/{db_id}/wiki/pages/{page_id}`
- `GET /api/knowledge/databases/{db_id}/wiki/stale-pages`
- `POST /api/knowledge/databases/{db_id}/wiki/rebuild`

## 风险

- 未登录时 `/database/:db_id` 仍会按现有权限跳转登录页。
- 真实截图 QA 需要可用登录态或临时管理员。
- 空知识库会显示空态，不应被误判为坏掉。
