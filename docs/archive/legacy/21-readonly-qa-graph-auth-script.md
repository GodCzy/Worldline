# 只读 QA 验收脚本（Graph/Auth）

## 目的

提供一个默认只读的验收脚本入口，用于快速采集 `/api/system/health` 与 `/api/graph/*` 的状态码证据，并生成 M1 规范的最小证据包。

脚本文件：
- `scripts/qa_graph_auth_readonly_check.py`

## 安全边界

1. 仅执行 `GET` 请求。
2. 不创建、不更新、不删除业务数据。
3. 允许外部传入 `admin/user` token 做正负例校验，但脚本本身不造数。
4. `--allow-temp-user` 仅保留为兼容参数，不会触发写操作。

## M1 输出契约

默认输出目录采用：

```text
artifacts/qa-phase4-m1-baseline-<timestamp>/
```

脚本会同时保留历史兼容文件，避免旧流程失效：

- `result.json`
- `result.txt`
- `run_config.json`
- `mcp_next_steps.md`

M1 新规范下，脚本还会补齐这些结构化文件：

- `00-run-metadata.json`
- `20-api-matrix.json`
- `21-api-matrix.txt`
- `99-evidence-summary.md`

说明：

- `runtime` 桶由控制器在外部补充，如 `10-runtime-health.txt`。
- `api` 桶由该脚本生成。
- `ui` 桶由控制器的 Playwright 复核或历史证据继承补齐。
- `summary` 桶由该脚本生成。

## 运行方式

### 1) 本地自检

```bash
python scripts/qa_graph_auth_readonly_check.py --self-check
```

说明：`--self-check` 不发网络请求，仅验证 artifact 落盘路径与文件生成。

### 2) 匿名只读验收

```bash
python scripts/qa_graph_auth_readonly_check.py --api-base http://127.0.0.1:5050
```

### 3) 携带 token 做正负例

```bash
python scripts/qa_graph_auth_readonly_check.py \
  --api-base http://127.0.0.1:5050 \
  --admin-token "<ADMIN_TOKEN>" \
  --user-token "<USER_TOKEN>"
```

### 4) 复跑旧前缀

如果需要临时复跑历史目录命名，可显式指定前缀：

```bash
python scripts/qa_graph_auth_readonly_check.py --package-prefix qa-readonly-graph-auth
```

## 验收矩阵

### L0 / Shell-Runtime

要求：

- `api-dev` healthy
- `graph` healthy
- `python scripts/qa_graph_auth_readonly_check.py --self-check` 通过
- `/api/system/health` 返回 `200`

### L1 / API 权限边界

要求：

- anonymous 访问 `/api/graph/list` 返回 `401`
- anonymous 访问 `/api/graph/neo4j/info` 返回 `401`
- admin 访问上述接口返回 `200`
- `role=user` 访问上述接口返回 `403`

### L2 / MCP Playwright 交互守卫

要求：

- `role=user` 登录后访问 `/graph`
- 最终 URL 回退至 `/agent` 或 `/agent/{id}`
- Network 中不出现 user 对 `api/graph/*` 的 admin-only 成功态
- 截图、网络摘要、最终 URL 断言落盘

## 证据目录命名

新包目录：

```text
artifacts/qa-phase4-m1-baseline-YYYYMMDD-HHMMSS/
```

最小留痕建议：

- `00-run-metadata.json`
- `10-runtime-health.txt`
- `20-api-matrix.json`
- `21-api-matrix.txt`
- `30-ui-graph-guard.png`
- `31-ui-network-graph-guard.txt`
- `32-ui-final-url-assertion.json`
- `90-mcp-next-steps.md`
- `99-evidence-summary.md`

历史兼容目录：

- `artifacts/qa-readonly-graph-auth-*`
- `artifacts/qa-release-audit-*`

## 风险说明

1. 脚本默认只读，不包含任何写入能力。
2. 如果没有新鲜的 Playwright 证据，`ui` 桶只能先使用历史继承证据，不能冒充为新交互结果。
3. `runtime` 桶的真实健康信息需要由控制器或 shell 侧补齐，脚本只负责生成契约文件与 API 结果。

## 结论

该脚本的职责是提供稳定、可复放的只读 API 验收入口，并把 M1 证据包的目录结构固定下来；它不承担业务数据写入，也不承担模块层功能扩展。
