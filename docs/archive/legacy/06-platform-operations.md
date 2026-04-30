# 06 运行与运维说明

## 目标

这份文档用于说明如何在本地启动、验证和维护世界线项目。

如果你想看“怎么使用页面、每个区域是什么意思、应该怎么点击”，请直接看：

- [07 完整使用教程](D:/worldline/docs/07-complete-user-guide.md)

## 运行前准备

建议本机已具备：

- Docker Desktop
- Node.js
- npm / pnpm
- Git

## 环境变量

首次运行需要：

```powershell
Copy-Item .env.template .env
```

至少补齐：

- `SILICONFLOW_API_KEY`

## 启动系统

在仓库根目录执行：

```powershell
docker compose up --build -d
```

## 主要访问入口

- 首页：`http://localhost:5173/`
- 主题分区：`http://localhost:5173/themes`
- PoE 主题页：`http://localhost:5173/themes/poe`
- Agent：`http://localhost:5173/agent`
- Graph：`http://localhost:5173/graph`
- Dashboard：`http://localhost:5173/dashboard`
- API 健康检查：`http://localhost:5050/api/system/health`
- 文档站：`http://localhost:5174`

## 当前本地验证建议

建议每次演示前至少验证以下内容：

1. `docker compose ps`
2. 首页可访问
3. PoE 主题页可访问
4. 登录后 Agent 页可输入
5. Graph 页可打开
6. Dashboard 可打开

## 典型问题

### 1. 登录后无法输入

当前已知根因已经修复：访问 `/agent` 时会自动跳转到默认智能体页面。

若仍异常，先尝试：

- `Ctrl+F5` 强刷前端
- 重新打开 `http://localhost:5173/agent`

### 2. 前端出现红色 Vite 报错遮罩

优先检查：

- 容器是否已重建
- `docker compose logs web`
- `pnpm build` 是否通过

### 3. 页面文案有乱码

这是当前展示层仍需继续清理的问题，通常不影响主链路运行，但影响最终展示质量。

### 4. 模型无响应

优先检查：

- `.env` 中的模型服务密钥
- 后端日志
- 外部模型服务是否可访问

## 文档站

本项目文档站可通过以下命令启动：

```powershell
npm install
npm run docs:dev
```

如需构建：

```powershell
npm run docs:build
```

## 运维建议

毕业答辩阶段不建议再做以下高风险操作：

- 大范围目录迁移
- 重写底层知识库/RAG/图谱运行链
- 清理全部历史兼容命名

更合理的做法是：

- 优先保证功能稳定
- 优先保证展示页面文本可读
- 优先保证演示脚本与系统状态一致
