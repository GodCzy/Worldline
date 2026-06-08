# P2-3 验证证据

日期：2026-06-08

## 清理前统计

第一批目标来自 Agent/run 目录审计，共 8 个：

| 目标 | 类型 | 文件数 | 字节 |
|---|---:|---:|---:|
| `.ai/tasks/2026-06-05-agent-focus-dossier-mcp-shortcut/chrome-profile` | directory | 594 | 87541652 |
| `.ai/tasks/2026-06-05-agent-gate-mcp-read-contract/chrome-profile` | directory | 595 | 83945126 |
| `.ai/tasks/2026-06-05-agent-last-mcp-call-preview/chrome-profile` | directory | 585 | 83299326 |
| `.ai/tasks/2026-06-05-agent-last-mcp-call-preview/chrome-profile-global` | directory | 588 | 83475825 |
| `.ai/tasks/2026-06-05-agent-evidence-mcp-read-contract/chrome-cdp.err.log` | file | 1 | 1021 |
| `.ai/tasks/2026-06-05-agent-evidence-mcp-read-contract/chrome-cdp.out.log` | file | 1 | 0 |
| `.ai/tasks/2026-06-05-agent-knowledge-mcp-read-contract/chrome-cdp.err.log` | file | 1 | 1027 |
| `.ai/tasks/2026-06-05-agent-knowledge-mcp-read-contract/chrome-cdp.out.log` | file | 1 | 0 |

第一批合计：2366 个文件，338263977 字节。

第二批目标来自清理后复扫，共 3 个：

| 目标 | 类型 | 文件数 | 字节 |
|---|---:|---:|---:|
| `.ai/tasks/2026-06-07-database-create-backend-capabilities/chrome-profile-cdp` | directory | 338 | 35143701 |
| `.ai/tasks/2026-06-07-database-query-params-linkage/chrome-profile-cdp` | directory | 431 | 34703021 |
| `.ai/tasks/2026-06-07-knowledge-graph-state-ux/chrome-profile-cdp` | directory | 494 | 40148922 |

第二批合计：1263 个文件，109995644 字节。

总计清理：11 个目标，3629 个文件，448259621 字节，约 427.5 MiB。

## 删除命令策略

使用 PowerShell：

- `Resolve-Path -LiteralPath` 解析每个目标。
- 检查解析结果必须位于 `D:\dev\Worldline\.ai\tasks` 下。
- 通过后执行 `Remove-Item -LiteralPath <path> -Recurse -Force`。

没有使用跨 shell 拼接删除命令。

## 删除后验证

目标逐项复核：

- 11 个删除目标 `Test-Path` 均为 `false`。
- `.ai/tasks` 下 `chrome-profile*` 目录计数：0。
- `.ai/tasks` 下 `chrome-cdp*.log` 文件计数：0。
- `.ai/tasks` 下常见浏览器缓存目录 `Cache`、`Code Cache`、`GPUCache`、`Local Storage`、`Service Worker` 计数：0。
- `.ai/tasks` 下截图证据仍有 176 个文件。

## Git 状态说明

相关任务目录仍显示为 untracked 是预期结果，因为目录内保留了 Markdown 证据、截图或 QA 报告。P2-4 会单独处理工作树分组与提交边界。
