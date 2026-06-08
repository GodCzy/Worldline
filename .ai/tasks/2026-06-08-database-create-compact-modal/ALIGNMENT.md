# 新建知识库页面紧凑化

日期：2026-06-08

## 目标

- 从 `D:\dev\Worldline` 继续 Worldline 开发。
- 优先完成“新建知识库页面紧凑化”。
- 保留完整后端创建能力，但让主弹窗只保留核心字段和摘要。

## 验收

- `POST /api/knowledge/databases` 的前端 payload 字段不减少。
- Dify、LightRAG、Milvus/CommonRAG 三类创建配置都能看到对应能力入口。
- 高级后端配置、分块解析、共享设置、请求预览通过按钮/抽屉打开。
- 前端 build 通过。
- 浏览器检查 `/database` 新建知识库弹窗在桌面和移动视口不冗长、不重叠。
