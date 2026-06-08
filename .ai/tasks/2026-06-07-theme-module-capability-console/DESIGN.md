# 设计

## 前端结构

- 新增 `web/src/utils/worldlineCapabilities.js`，集中定义 Worldline 后端能力组、端点摘要和启用面计算。
- `ThemeHubView.vue` 使用能力定义：
  - 卡片展示“能力组 / 接口数”的短摘要。
  - 创建/编辑弹窗展示启用能力组、核心端点和保存预览。
  - 保存 payload 继续走 `/api/system/themes`，在 `worldline.capability_map` 中附带能力映射。
- `ThemeDetailView.vue` 使用同一份能力定义：
  - 增加“模块能力控制台”短区块。
  - 常用动作直接作为按钮，完整端点和 payload 放到右侧抽屉。

## 后端契约

`server/routers/system_router.py` 的 `_normalize_theme_payload` 会保留 `worldline` 子对象中的扩展字段，因此 `worldline.capability_map` 可以作为自定义模块元数据保存，不影响已有 `db_id`、`surfaces`、`default_question` 字段。

## 取舍

- 不把每个端点都铺在页面正文，避免主题页变成接口清单。
- 不新增依赖；沿用 Vue 3、Ant Design Vue、lucide 和现有 Worldline CSS 变量。
- 不在详情页直接触发重建 Wiki/图谱/质量门禁，先提供入口和清楚的能力地图，避免误操作。
