# Alignment

目标：验证 Agent Workbench 在管理员登录态下能真实调用 `/api/worldline/runs` 后端，而不是只停留在本地 preview。

范围：
- 使用当前本地后端 `http://127.0.0.1:5050`。
- 启动前端 dev server 后访问 `/worldline/agent`。
- 覆盖保存 run、读取 run 列表/详情、审批或拒绝分支、读取 manifest/resource/gates/evidence/knowledge。
- 完成桌面和 390px 移动端截图 QA。

不做：
- 不伪造管理员截图。
- 不绕过登录权限。
- 不清理无关脏工作树。
