# 清理设计

## 清理对象

本次只处理以下可再生临时产物：

- `chrome-profile`
- `chrome-profile-global`
- `chrome-profile-cdp`
- `chrome-cdp.err.log`
- `chrome-cdp.out.log`
- profile 内常见浏览器缓存目录

## 删除策略

使用 PowerShell 原生命令完成：

1. `Resolve-Path` 解析目标路径。
2. 检查解析后的路径必须以 `D:\dev\Worldline\.ai\tasks` 开头。
3. 统计文件数和字节数。
4. 对通过校验的目标调用 `Remove-Item -LiteralPath ... -Recurse -Force`。
5. 再次扫描残留目标。

## 保留策略

以下内容明确保留：

- `screenshots/` 下截图证据。
- 各任务的 `ALIGNMENT.md`、`DESIGN.md`、`TASKS.md`、`EVIDENCE.md`、`DECISIONS.md`。
- QA 脚本、报告 JSON、可读审计报告。
- 业务代码、测试代码、Docker 配置和文档。
