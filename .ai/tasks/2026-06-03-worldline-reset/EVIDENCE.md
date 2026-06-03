# Worldline Reset Evidence

更新时间：2026-06-03

## Cleanup

- 已确认目标根目录：`D:\dev\Worldline`、`D:\document\Worldline`。
- 已删除旧 Markdown 内容来源。
- 已删除旧 `.ai/tasks`、旧 `.codex`、旧 artifacts、旧 docs archive/context-cache、旧 product/agent-workflow docs 和 `data/poe`。
- 已重建最小事实源：`README.md`、`AGENTS.md`、`docs/index.md`、本任务目录。

## Verification

### 文件核对

- `D:\dev\Worldline` 当前 Markdown：
  - `.ai\tasks\2026-06-03-worldline-reset\ALIGNMENT.md`
  - `.ai\tasks\2026-06-03-worldline-reset\DECISIONS.md`
  - `.ai\tasks\2026-06-03-worldline-reset\DESIGN.md`
  - `.ai\tasks\2026-06-03-worldline-reset\EVIDENCE.md`
  - `.ai\tasks\2026-06-03-worldline-reset\TASKS.md`
  - `AGENTS.md`
  - `docs\index.md`
  - `README.md`
- `D:\document\Worldline` 当前 Markdown：`README.md`
- `.github` 旧 issue/PR Markdown 模板已删除。
- `.venv` 已删除；`.env` 从 `.env.template` 复制生成，受 `.gitignore` 保护，不进入 Git。

### 旧引用扫描

命令：

```powershell
rg --hidden -n 'poePhase1|poeWorldlineAdapter|worldlineOpsAdapter|worldlineSandboxAdapter|context-cache|PROJECT_BOOK|WORLDLINE_PROJECT_PLAN|CODEX_WORKFLOW|docs/archive|docs/product|docs/agent-workflow|\.codex' -g '!node_modules/**' -g '!.git/**' -g '!uv.lock' -g '!package-lock.json'
```

结果：仅命中新 README/AGENTS/任务证据中声明旧内容失效的文本；没有代码继续导入旧 PoE adapter 或旧规划文件。

### 构建与配置

- `wsl.exe -d Debian -- bash -lc 'cd /mnt/d/dev/Worldline && docker compose config --quiet'`：通过。执行前已从 `.env.template` 复制本地 `.env`。
- `wsl.exe -d Debian -- bash -lc 'cd /mnt/d/dev/Worldline && npm --prefix web run build'`：通过，Vite 构建耗时约 5 分 23 秒；仅有大 chunk 警告。
- `wsl.exe -d Debian -- bash -lc 'cd /mnt/d/dev/Worldline && npm run docs:build'`：通过，VitePress 构建完成。

### 未通过项

- `wsl.exe -d Debian -- bash -lc 'cd /mnt/d/dev/Worldline && uv run --group test pytest test/test_knowledge_object_models.py test/test_worldline_phase5_7_services.py'`：未通过。失败点不是测试断言，而是依赖下载阶段网络错误。
- 两次失败分别卡在 `pycryptodome==3.23.0` 和 `shapely==2.1.2`，错误为 Tsinghua PyPI 镜像 `tls handshake eof`。

## Residual Risk

- Python 测试需要在依赖下载恢复后重跑。
- 当前 Git 状态包含清理前已有的代码修改；本次没有回滚这些改动。
