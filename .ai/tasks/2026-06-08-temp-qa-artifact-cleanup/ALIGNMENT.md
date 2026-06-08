# P2-3 临时 QA 产物清理

日期：2026-06-08

## 目标

清理 `.ai/tasks` 中可再生的浏览器 QA 临时产物，包括 Chrome profile、CDP 日志和浏览器缓存目录，降低工作树噪音和仓库体积风险。

## 边界

- 只清理 `D:\dev\Worldline\.ai\tasks` 内的临时 QA profile、日志和缓存。
- 不删除截图、`EVIDENCE.md`、`TASKS.md`、QA 脚本、业务代码或用户资料。
- 删除前必须解析绝对路径，并确认目标位于 `.ai\tasks` 内。
- 本任务不处理提交、不回滚旧修改、不重写历史任务证据。

## 验收

- 已识别的临时 profile 和 CDP 日志被删除。
- `.ai/tasks` 下 `chrome-profile*`、`chrome-cdp*.log` 和常见浏览器缓存目录无残留。
- 截图证据仍存在。
- 清理过程和验证结果写入 `EVIDENCE.md` 与 `D:\document\OutputMD`。
