# Design

日期：2026-06-08

## 发现

`server/routers/graph_router.py` 中 `_get_graph_adapter()` 注释说明只有 Upload/Neo4j 类型需要 `graph_base`，但当前实现会在检测类型后仍然无条件调用 `_ensure_graph_base_running()`。这会让 LightRAG 图谱也被 Upload 图服务初始化状态卡住。

## 修改方向

- 先通过 `GraphAdapterFactory.detect_graph_type()` 判断图谱类型。
- 只有 `upload` 类型需要 `_ensure_graph_base_running()`。
- `lightrag` 类型直接创建 LightRAG adapter。
- adapter 创建失败统一转为 `HTTPException(503)`，由现有 `/subgraph`、`/stats`、`/labels` 分支转换为 degraded 空数据。

## 兼容性

- 不改变路由路径。
- 不改变成功响应 shape。
- 对失败只做兼容降级：原 500 情况变成 `success: true` + `degraded: true` + `degraded_reason`。
