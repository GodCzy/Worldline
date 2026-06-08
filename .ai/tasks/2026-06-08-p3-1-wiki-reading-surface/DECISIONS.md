# Decisions

## D1. Wiki 阅读面放在知识库详情页

原因：Wiki 页面是知识库资产，放在 `/database/:db_id` 的右侧 tab 与图谱、检索测试、评估并列，符合操作台信息架构。

## D2. 完整 Markdown 放 drawer

原因：主 tab 需要紧凑展示 claims/citations/review/open questions；完整 Markdown 较长，适合抽屉。

## D3. 不新增依赖

原因：已有页面可以用 Ant Design Vue、lucide 和现有 API 完成，不需要引入 Markdown viewer 或额外可视化库。
