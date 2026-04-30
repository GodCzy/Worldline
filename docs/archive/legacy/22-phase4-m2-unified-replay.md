# Phase 4b M2 Unified Replay

## 目标

在不修改业务功能的前提下，用一个入口把三段证据收敛成一条可复用、非交互的 replay 流程：

- `L0 runtime`
- `L1 readonly API matrix`
- `L2 Playwright UI guard`

入口脚本：

- `scripts/qa_phase4_m2_replay.py`

依赖脚本：

- `scripts/qa_graph_auth_readonly_check.py`

## 非交互凭据策略

replay 不再依赖人工交互输入。推荐使用一个 JSON manifest 统一描述本次运行所需的所有输入。

优先级规则：

1. 命令行显式参数
2. `--replay-manifest` 指定的 JSON manifest
3. 环境变量
4. 脚本默认值

### Manifest 字段

Manifest 是一个 JSON 对象，支持以下键：

- `api_base`
- `frontend_base`
- `out_dir`
- `artifact_prefix`
- `timeout_seconds`
- `skip_runtime`
- `ui_source_dir`
- `admin_token`
- `admin_token_file`
- `user_token`
- `user_token_file`

推荐只把 token 放在文件里，不把明文 token 写进 manifest。
manifest 和 token 文件都兼容 UTF-8 与 UTF-8 BOM，方便直接用 PowerShell 生成。

### 示例

```json
{
  "api_base": "http://127.0.0.1:5050",
  "frontend_base": "http://127.0.0.1:5173",
  "out_dir": "artifacts",
  "artifact_prefix": "qa-phase4-m2-harden",
  "timeout_seconds": 12,
  "skip_runtime": false,
  "ui_source_dir": "D:\\worldline\\artifacts\\qa-phase4-m1-baseline-20260403-074449",
  "admin_token_file": "D:\\worldline\\secrets\\worldline-admin.token",
  "user_token_file": "D:\\worldline\\secrets\\worldline-user.token"
}
```

### 推荐命令

```powershell
python scripts/qa_phase4_m2_replay.py `
  --replay-manifest D:\worldline\configs\qa-phase4-m2-replay.json
```

如果需要临时覆盖单个参数，命令行参数优先于 manifest。

## 单入口流程

replay 的执行顺序固定为：

1. 解析 manifest / CLI / env，得到非交互输入
2. 检查 L0 runtime
3. 调用 readonly checker 生成 L1 API 证据
4. 校验并合并 L2 UI 证据
5. 输出单个 summary

## 输出契约

默认证据目录命名：

```text
artifacts/qa-phase4-m2-harden-<timestamp>/
```

最小输出文件：

- `00-run-metadata.json`
- `01-precondition-error.json`
- `02-main-blocker.json`
- `10-runtime-health.txt`
- `11-api-run.log`
- `20-api-matrix.json`
- `21-api-matrix.txt`
- `30-ui-graph-guard.png`
- `31-ui-network-graph-guard.txt`
- `32-ui-final-url-assertion.json`
- `90-mcp-next-steps.md`
- `99-evidence-summary.md`

兼容历史输出：

- `result.json`
- `result.txt`
- `run_config.json`
- `mcp_next_steps.md`

## 退出码

- `0`：L0 / L1 / L2 全部通过
- `2`：L0 失败
- `3`：L1 失败
- `4`：L2 失败
- `5`：摘要写入失败
- `6`：前置条件失败

## 唯一主阻塞项规则

主阻塞项按固定顺序判定：

`precondition -> L0-runtime -> L1-api-matrix -> L2-ui-guard -> summary`

规则如下：

1. 只记录第一个失败项为唯一主阻塞项。
2. 其余失败不升级为并列主阻塞，只能作为派生信息写入摘要或 metadata。
3. 如果所有阶段都通过，则 `main_blocker = null`。
4. 如果前置条件失败，主阻塞项就是前置条件，不再继续判定后续阶段。

metadata 中会写入 `main_blocker`，summary 中会写入 `main_blocker` 和 `blocker_rule`，便于 CI 和人工复核使用同一判定口径。

## 边界说明

- replay 只做读取、校验和证据合并，不做业务写入。
- `--replay-manifest` 只是一种输入封装，不改变权限语义。
- UI 证据必须来自已有的 `role=user` /graph 交互结果，不在 replay 里临时创建交互行为。

## 验证命令

```powershell
python -m py_compile D:\worldline\scripts\qa_phase4_m2_replay.py
python D:\worldline\scripts\qa_phase4_m2_replay.py --help
python D:\worldline\scripts\qa_phase4_m2_replay.py --replay-manifest D:\worldline\configs\qa-phase4-m2-replay.json
```

## CI 固化步骤

GitHub Actions workflow：

- `.github/workflows/phase4-replay.yml`

CI 默认 `ui_source_dir`：

- `artifacts/qa-phase4-m1-baseline-20260403-074449`
- 该目录位于仓库已跟踪文件中，可直接作为 headless replay 的 L2 基线证据来源。

CI 固化顺序：

1. checkout 仓库
2. 准备 replay manifest
3. 写入临时 token 文件
4. 启动 `graph` 与 `api` 运行时依赖
5. 执行 `qa_phase4_m2_replay.py --replay-manifest ...`
6. 解析 `run_dir`
7. 把 manifest 复制为 `00-replay-manifest.json`
8. 上传整个 `run_dir` 作为 GitHub artifact

最小重试策略：

- 只对 `exit_code=2(runtime_failed)` 或 `exit_code=3(api_failed)` 重试一次。
- `exit_code=6(precondition_failed)` 不重试，直接失败并输出 precondition 信息。

失败码映射在 workflow summary 中保持一致：

- `0` -> `pass`
- `2` -> `runtime_failed`
- `3` -> `api_failed`
- `4` -> `ui_failed`
- `5` -> `summary_failed`
- `6` -> `precondition_failed`

### 证据归档策略

- 单次 replay 的主归档单元是整个 `artifacts/qa-phase4-m2-harden-<timestamp>/` 目录。
- workflow 会把生成的 replay manifest 复制进 run dir，文件名固定为 `00-replay-manifest.json`。
- run dir 里保留：
  - `00-run-metadata.json`
  - `02-main-blocker.json`
  - `10-runtime-health.txt`
  - `11-api-run.log`
  - `20-api-matrix.json`
  - `21-api-matrix.txt`
  - `30-ui-graph-guard.png`
  - `31-ui-network-graph-guard.txt`
  - `32-ui-final-url-assertion.json`
  - `99-evidence-summary.md`
- GitHub artifact 命名建议：
  - `qa-phase4-m2-replay-runid-runattempt`
- 保留期建议：
  - `14` 天

说明：
- workflow 不再提前检查 `ui_source_dir` 的具体证据文件
- UI 缺证时由 `qa_phase4_m2_replay.py` 自己写入 `main_blocker` 和 `run_dir`
