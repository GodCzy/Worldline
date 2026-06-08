# 证据

## 已核对

- `D:\document\OutputMD\2026-06-08-Worldline-Project-Handoff-Unfinished-Work.md`
- `D:\dev\Worldline\AGENTS.md`
- `D:\dev\Worldline\README.md`
- `D:\dev\Worldline\docs\index.md`
- `server/routers/knowledge_router.py` 的 `POST /api/knowledge/databases`
- `web/src/views/DataBaseView.vue` 的 `buildRequestData()`

## 验证记录

### `git diff --check`

- 结果：通过。
- 备注：仅出现已有工作树文件的 CRLF/LF 提示。

### `npm --prefix web run build`

- 命令：

```powershell
wsl -d Debian -- bash -lc "cd /mnt/d/dev/Worldline && stdbuf -oL -eL /home/joy/.local/bin/npm --prefix web run build"
```

- 结果：通过。
- Vite 输出：`✓ built in 4m 47s`。
- 备注：存在既有的大 chunk warning，未阻塞构建。

### 编码清理

- 移除 `web/src/views/DataBaseView.vue` 首字节 UTF-8 BOM。
- 当前文件前三个字节：`3C 74 65`。

### 浏览器 QA

- 前端 dev server：`http://127.0.0.1:5173/`，已启动。
- `/database` 会重定向到 `/?login=1&redirect=/database`。
- 2026-06-08 复查：in-app Browser 实际导航 `http://127.0.0.1:5173/database` 后，当前 URL 为 `http://127.0.0.1:5173/?login=1&redirect=/database`；DOM 中存在 `登录 Worldline`，不存在 `新建知识库`。
- 2026-06-08 blocked 后恢复复查：目标恢复为 active 后，再次用 in-app Browser 导航 `/database`，当前 URL 仍为 `http://127.0.0.1:5173/?login=1&redirect=/database`；DOM 中存在 `登录 Worldline`，不存在 `新建知识库` 或 `文档知识库`。
- 2026-06-08 blocked 后第二次恢复复查：in-app Browser 导航 `/database`，当前 URL 仍为 `http://127.0.0.1:5173/?login=1&redirect=/database`；DOM 中存在 `登录 Worldline`，不存在 `新建知识库` 或 `文档知识库`。
- 2026-06-08 blocked 后第三次恢复复查：in-app Browser 导航 `/database`，当前 URL 仍为 `http://127.0.0.1:5173/?login=1&redirect=/database`；DOM 中存在 `登录 Worldline`，不存在 `新建知识库` 或 `文档知识库`。
- 本地项目测试账号在当前数据库中登录失败。
- `.env` 中 `WORLDLINE_SUPER_ADMIN_NAME` 和 `WORLDLINE_SUPER_ADMIN_PASSWORD` 是注释状态。
- 未创建临时超级管理员，未伪造登录态；需要 Joy 登录管理员账号后复查桌面和移动截图。

### blocked 后新的恢复复查

- 2026-06-08 新的恢复复查：目标状态为 `active` 后再次检查本地服务，`http://127.0.0.1:5173/api/system/info` 返回 `success: true`。
- 2026-06-08 新的恢复复查：`.env` 中 `WORLDLINE_SUPER_ADMIN_NAME` 和 `WORLDLINE_SUPER_ADMIN_PASSWORD` 仍为注释状态。
- 2026-06-08 新的恢复复查：in-app Browser 实际导航 `http://127.0.0.1:5173/database` 后，当前 URL 仍为 `http://127.0.0.1:5173/?login=1&redirect=/database`；DOM 中存在 `登录 Worldline`，不存在 `新建知识库` 或 `文档知识库`。
- 本次仍未绕过登录权限、未伪造登录状态、未创建临时管理员账号。

### blocked 后新一轮第二次恢复复查

- 2026-06-08 第二次恢复复查：`http://127.0.0.1:5173/api/system/info` 仍返回 `success: true`。
- 2026-06-08 第二次恢复复查：`.env` 中 `WORLDLINE_SUPER_ADMIN_NAME` 和 `WORLDLINE_SUPER_ADMIN_PASSWORD` 仍为注释状态。
- 2026-06-08 第二次恢复复查：in-app Browser 导航 `http://127.0.0.1:5173/database` 后，当前 URL 仍为 `http://127.0.0.1:5173/?login=1&redirect=/database`；DOM 中存在 `登录 Worldline`，不存在 `新建知识库`、`文档知识库` 或 `高级后端配置`。
- 本轮仍未绕过登录权限、未伪造登录状态、未创建临时管理员账号。

### blocked 后新一轮第三次恢复复查

- 2026-06-08 第三次恢复复查：`http://127.0.0.1:5173/api/system/info` 仍返回 `success: true`。
- 2026-06-08 第三次恢复复查：`.env` 中 `WORLDLINE_SUPER_ADMIN_NAME` 和 `WORLDLINE_SUPER_ADMIN_PASSWORD` 仍为注释状态。
- 2026-06-08 第三次恢复复查：in-app Browser 导航 `http://127.0.0.1:5173/database` 后，当前 URL 仍为 `http://127.0.0.1:5173/?login=1&redirect=/database`；DOM 中存在 `登录 Worldline`，不存在 `新建知识库`、`文档知识库`、`高级后端配置` 或 `分块解析`。
- 本轮仍未绕过登录权限、未伪造登录状态、未创建临时管理员账号。
- 结论：blocked 后新一轮恢复审计已连续三次遇到同一登录拦截条件；真实 `/database` 桌面/移动截图 QA 仍需管理员登录这一外部状态变化。

### 登录阻塞解除与 QA 方式

- 2026-06-08 Joy 明确追加“目标受阻可以解决的话你自己解决”后，使用项目自带 `scripts/ensure_superadmin.py` 创建/更新本地临时 `codex_temp_admin` superadmin。
- 临时密码只在进程内随机生成，并短暂写入 Windows 临时文件供自动登录；`C:\Users\Joy\AppData\Local\Temp\worldline-codex-creds.json` 与 `C:\Users\Joy\AppData\Local\Temp\worldline-codex-token.txt` 均已删除。
- 未修改 `.env`，未把密码写入仓库、任务文档或 OutputMD。
- QA 完成后已清理临时账号：`codex_temp_admin` 在本地数据库中已标记 `is_deleted=1`。
- in-app Browser 在恢复阶段出现 `ERR_BLOCKED_BY_CLIENT` 和标签页 attach 超时，因此改用 Windows 临时目录安装的 `playwright-core` 加系统 Chrome 做真实渲染 QA；临时目录 `C:\Users\Joy\AppData\Local\Temp\worldline-qa-node` 已删除。

### 系统 Chrome / Playwright 截图 QA

- 登录结果：`codex_temp_admin`，角色 `superadmin`。
- 实际页面：`http://127.0.0.1:5173/database`。
- 主弹窗核心字段均可见：知识库类型、名称、描述、后端配置、分块解析、共享设置、创建请求。
- 抽屉 QA：
  - `高级后端配置`：可见私有知识库、存储标识。
  - `分块解析`：开启覆盖后可见 Chunk Token 数、重叠比例、分隔符、RAPTOR、GraphRAG。
  - `共享设置`：可见 `share_config` 对应共享配置。
  - `创建请求预览`：可见 `POST /api/knowledge/databases` payload。
- Dify 遮罩 QA：填入测试 Dify Token 后，payload 预览包含 `***`，不包含原始测试 token，仍包含 Dify Dataset ID。
- LightRAG QA：可见语言和 LLM 字段。
- Dify QA：可见 Dify API URL、Dify Token、Dataset ID 字段。
- 移动端修复后测量：Modal `left=12`、`width=366`、`right=378`、`viewport=390`，`horizontalOverflow=false`。
- 截图：
  - `screenshots/database-create-modal-desktop.png`
  - `screenshots/database-create-drawer-backend-desktop.png`
  - `screenshots/database-create-drawer-chunk-desktop.png`
  - `screenshots/database-create-drawer-chunk-override-desktop.png`
  - `screenshots/database-create-drawer-share-desktop.png`
  - `screenshots/database-create-drawer-payload-desktop.png`
  - `screenshots/database-create-drawer-payload-dify-masked-desktop.png`
  - `screenshots/database-create-modal-lightrag-desktop.png`
  - `screenshots/database-create-modal-dify-desktop.png`
  - `screenshots/database-create-modal-mobile.png`

### 移动端响应式修复

- `web/src/views/DataBaseView.vue` 增加移动端全局 Ant Modal / Drawer 覆盖：
  - `.new-database-modal` 在 `max-width: 760px` 下限制为 `calc(100vw - 24px)`。
  - `.new-database-modal .ant-modal-body` 限制高度并启用纵向滚动。
  - `.create-database-drawer .ant-drawer-content-wrapper` 在移动端限制为 `calc(100vw - 16px)`。

### 最终构建复查

- 命令：`npm --prefix web run build`。
- 结果：通过。
- Vite 输出：`✓ built in 5m 33s`。
- 备注：仍有既有大 chunk warning，未阻塞构建。
