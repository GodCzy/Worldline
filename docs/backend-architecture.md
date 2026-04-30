# 后端结构

## 目标

Phase 5 后端不追求换接口，而是把入口组织和职责边界整理清楚。

当前默认原则：

- Phase 4 锁定的 graph/auth 契约不能回退
- 现有 API 路径保持兼容
- 优先收敛 router/bootstrap 结构债

## 结构分层

### 平台级

- `system`
- `auth`
- 共享运行配置与健康检查

### 知识与工作流

- `chat`
- `knowledge`
- `evaluation`
- `mindmap`
- `graph`
- `tasks`

### 运维扩展

- `mcp`
- `skills`
- `tools`

## Phase 5 的后端改动边界

- 可以重组 router 注册方式
- 可以抽出 app 创建和 middleware 注册过程
- 可以修复兼容式 bug
- 不做 schema 迁移
- 不改 graph/auth 公开语义
- 不把模块专有逻辑写回平台固定入口
