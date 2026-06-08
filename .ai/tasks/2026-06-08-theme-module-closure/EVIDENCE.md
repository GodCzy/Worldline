# Evidence

日期：2026-06-08

## 当前审计

- 旧交接 `2026-06-08-Worldline-Next-Goal-Unfinished-Work.md` 中 `/graph` P0 已过期；新总结 `2026-06-08-Worldline-Graph-Timeline-P0.md` 表明 P0 已完成。
- 当前优先项为主题分区自定义模块闭环。
- 工作树非常脏，本阶段只触碰主题闭环相关文件和本任务目录。

## 实现范围

- 新增 `src/services/theme_module_contract.py`，把主题模块 payload 归一化逻辑从路由中抽成纯后端契约，覆盖 `knowledge`、`context`、`worldline`、`metadata` 和能力地图。
- `server/routers/system_router.py` 的自定义主题模块创建、读取、更新、删除流程改用新契约函数；聊天模型状态测试改为懒加载，避免导入路由时牵连模型依赖。
- `web/src/views/DataBaseView.vue` 从知识库跳转到 `/themes?new_module=1` 时携带知识库 ID、名称、类型和描述。
- `web/src/views/themes/ThemeHubView.vue` 保持主弹窗简洁，只展示核心字段；生成配置、能力开关和 payload 预览收进“能力与生成配置”抽屉。
- `web/src/views/themes/ThemeDetailView.vue` 展示绑定知识库、目标、证据来源和能力摘要，并带上下文进入工作台。
- `web/src/views/worldline/WorldlineWorkbenchView.vue` 使用主题模块的 `knowledge_db_id`、目标、证据来源和生成配置生成世界线。
- `web/src/utils/worldlineCapabilities.js` 将 MCP、Workflow 纳入可开关 surface。
- 新增 `test/test_theme_module_contract.py` 覆盖完整主题模块 payload 和旧格式兼容。

## 自动化验证

- `wsl -d Debian -- bash -lc 'cd /mnt/d/dev/Worldline && timeout 120s env PYTHONPATH=. .venv/bin/pytest test/test_theme_module_contract.py -q -vv'`
  - 结果：`2 passed in 11.17s`。
  - 备注：仅有 requests 依赖版本 warning，与本次改动无关。
- `wsl -d Debian -- bash -lc 'cd /mnt/d/dev/Worldline && /home/joy/.local/bin/npm --prefix web run build'`
  - 结果：通过，`built in 6m 9s`。
  - 备注：保留既有大 chunk warning。
- `git diff --check -- src/services/theme_module_contract.py server/routers/system_router.py test/test_theme_module_contract.py web/src/utils/worldlineCapabilities.js web/src/views/DataBaseView.vue web/src/views/themes/ThemeHubView.vue web/src/views/themes/ThemeDetailView.vue web/src/views/worldline/WorldlineWorkbenchView.vue .ai/tasks/2026-06-08-theme-module-closure`
  - 结果：无空白错误。
  - 备注：提示少量既有 CRLF/LF 规范化 warning。
- `wsl -d Debian -- bash -lc 'pgrep -af pytest || true'`
  - 结果：无残留 pytest 进程。

## 真实 API 验证

- 使用临时管理员和临时知识库验证 `/api/system/themes`：
  - `POST /api/system/themes`：主题模块创建成功。
  - `GET /api/system/themes`：读回包含 `knowledge.knowledge_db_id`。
  - `PUT /api/system/themes/{themeId}`：更新 generation mode 和 surface 开关成功。
  - `GET /api/system/info`：自定义主题进入系统主题列表。
  - `GET /api/knowledge/databases/{db_id}/worldline/overview`：临时空知识库返回可解释 `empty` 状态。
  - `POST /api/knowledge/databases/{db_id}/worldline/generate`：临时空知识库返回 `empty`，且 `knowledgeDbId` 保持正确。
- API 验证后清理临时主题、临时知识库和临时管理员。

## 浏览器和截图 QA

- 先按 Browser skill 尝试 in-app Browser；当前连接中 `localStorage` evaluate 与 `Page.captureScreenshot` 不稳定，截图未以 in-app Browser 成功产出。
- 改用同一前端服务的 Chrome CDP 脚本 `qa-theme-module-closure-cdp.mjs` 做登录、路由、断言和截图。
- 断言文件：`theme-module-closure-browser-checks.json`。
  - `createDesktop`：目标、证据来源、配置按钮、绑定知识库均存在，无横向溢出。
  - `detailDesktop`：绑定知识库、目标、能力摘要、工作台入口均存在，无横向溢出。
  - `workbenchDesktop`：生成入口存在，页面非空，无横向溢出。
  - `createMobile` / `detailMobile` / `workbenchMobile`：390px 视口无横向溢出。
- 截图：
  - `screenshots/theme-create-modal-1440x900.png`
  - `screenshots/theme-detail-1440x900.png`
  - `screenshots/theme-workbench-1440x900.png`
  - `screenshots/theme-create-modal-390x844.png`
  - `screenshots/theme-detail-390x844.png`
  - `screenshots/theme-workbench-390x844.png`
- 视觉检查结果：
  - 桌面创建弹窗紧凑，复杂配置通过按钮/抽屉进入。
  - 桌面详情页显示绑定知识库、控制台和工作台入口。
  - 桌面工作台非空，临时空知识库不会生成分支是预期结果。
  - 移动端创建、详情、工作台均未出现横向溢出；长内容在输入框或页面滚动中处理。
- 浏览器 QA 后清理临时主题 `codex-theme-module-closure-qa`、临时知识库 `codex_theme_qa_20260608162549` 和临时管理员。

## 旁路审计

- Faraday 子代理只读审计了 Agent/run ledger 任务目录和临时浏览器 profile。
- 结论：run ledger 后续应先按真实后端契约任务分组推进；大量 2026-06-04/05/06 UI 任务仍是 mock/front-end-only/stage preview，不应当误判为后端已闭环。
- 结论：`.ai/tasks/*/chrome-profile*`、`Default/Cache`、`Code Cache`、`GPUCache`、`Local Storage`、`Service Worker`、CDP `.log` 属于临时 QA 噪声，后续分组清理时不要和功能代码一起 `git add .`。

## 残余风险

- `server/routers/system_router.py` 仍保留旧的本地 `_normalize_theme_payload` 辅助函数，但主题模块端点已切换到 `src.services.theme_module_contract.normalize_theme_payload`。后续可单独清理死代码。
- 工作树已有大量历史和并行修改，本阶段没有尝试整理或回滚未知改动。
- 主题模块闭环只验证了临时空知识库的真实 API 链路；包含上传、解析、EvidenceAnchor、WikiPage、TemporalFact 的完整有内容知识库链路仍属于后续任务。
