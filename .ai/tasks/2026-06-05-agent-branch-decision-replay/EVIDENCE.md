# Evidence

## Orientation

- Active root: `D:\dev\Worldline`.
- Branch: `codex/worldline-recovery-refactor`.
- Worktree was dirty before this stage; unrelated modified/deleted/untracked files are left untouched.

## Current Contract Inspection

- `src/services/worldline_run_ledger_service.py` exposes `reject_branch(...)` and records `event_type="branch.rejected"`.
- `server/routers/worldline_run_router.py` exposes `POST /api/worldline/runs/{run_id}/branches/{branch_id}/reject`.
- `web/src/apis/worldline_api.js` exposes `worldlineRunApi.rejectBranch(...)`.
- `web/src/data/worldline/agentWorkbench.js` local `nextActions` only included approve and trace before this stage.
- `web/src/views/worldline/WorldlineAgentWorkbenchView.vue` only handled `approve` before this stage.

## Commands

### Static Checks

```powershell
git diff --check -- web/src/data/worldline/agentWorkbench.js web/src/components/worldline/WorldlineBranchDetailPanel.vue web/src/views/worldline/WorldlineAgentWorkbenchView.vue .ai/tasks/2026-06-05-agent-branch-decision-replay
```

Result: passed.

```powershell
rg -n "[ \t]+$" web/src/data/worldline/agentWorkbench.js web/src/components/worldline/WorldlineBranchDetailPanel.vue web/src/views/worldline/WorldlineAgentWorkbenchView.vue .ai/tasks/2026-06-05-agent-branch-decision-replay
```

Result: no trailing whitespace in target files.

### Frontend Build

```powershell
wsl -d Debian -- bash -lc "cd /mnt/d/dev/Worldline/web && npm run build"
```

Result: passed in 5m 34s. Vite emitted the existing large vendor chunk warning.

### Browser/CDP QA

Browser plugin `node_repl` was not exposed by tool discovery, so validation used a temporary headless Chrome on CDP port `9227`.

```powershell
node .ai/tasks/2026-06-05-agent-branch-decision-replay/screenshot-branch-decision.cjs
```

Result: passed.

Verified:

- Branch Inspector exposes actions: approve, trace, and reject.
- Tool branch can be selected.
- Reject action text is visible: `拒绝并回滚`.
- Clicking reject in the current unauthenticated/local state shows the explicit gated message: `请先登录管理员账号；当前继续使用本地预览。`
- No fake local ledger mutation is presented as a successful backend rejection.

Screenshot:

- `D:\dev\Worldline\.ai\tasks\2026-06-05-agent-branch-decision-replay\screenshots\branch-reject-gated-message.png`

### Backend Focused Test Attempts

```powershell
uv run --group test pytest test/test_worldline_run_ledger_service.py
```

Result: failed on Windows because `uv` is not installed on the Windows side.

```powershell
wsl -d Debian -- bash -lc "cd /mnt/d/dev/Worldline && uv run --group test pytest test/test_worldline_run_ledger_service.py"
```

Result: failed before tests because `uv` attempted to fetch `neo4j` from `https://pypi.tuna.tsinghua.edu.cn/simple/neo4j/` and hit `tls handshake eof`.

```powershell
wsl -d Debian -- bash -lc "cd /mnt/d/dev/Worldline && .venv/bin/python -m pytest test/test_worldline_run_ledger_service.py"
```

Result: timed out after 304 seconds without producing a passing result.

Interpretation: backend reject contract was confirmed by source inspection in this stage, but focused pytest did not produce pass evidence due to local Python dependency/runtime issues.

## Cleanup

- Temporary Chrome process was stopped.
- Temporary profile `D:\dev\Worldline\.ai\tasks\2026-06-05-agent-branch-decision-replay\chrome-profile` was removed after confirming it resolved inside the task root.
