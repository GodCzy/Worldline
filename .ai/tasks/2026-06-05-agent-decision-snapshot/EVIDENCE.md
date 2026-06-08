# Evidence

## Orientation

- Active root: `D:\dev\Worldline`.
- Branch: `codex/worldline-recovery-refactor`.
- Worktree was dirty before this stage; unrelated modified/deleted/untracked files are left untouched.

## Current Inspection

- `src/services/worldline_run_ledger_service.py` branch decisions store `branch["decision"]` and emit `_branch_event_summary(...)`.
- `_branch_event_summary(...)` returns `status`, `reason`, `branch_title`, `branch_type`, `quality_status`, `score`, and linked evidence/tool/timeline/gate/artifact details.
- `web/src/views/worldline/WorldlineAgentWorkbenchView.vue` Event Detail does not currently render a structured branch decision snapshot.

## Commands

### Static Checks

```powershell
git diff --check -- web/src/views/worldline/WorldlineAgentWorkbenchView.vue .ai/tasks/2026-06-05-agent-decision-snapshot
```

Result: passed.

```powershell
rg -n "[ \t]+$" web/src/views/worldline/WorldlineAgentWorkbenchView.vue .ai/tasks/2026-06-05-agent-decision-snapshot -g "!chrome-profile/**"
```

Result: no trailing whitespace in target files.

### Frontend Build

```powershell
wsl -d Debian -- bash -lc "cd /mnt/d/dev/Worldline/web && npm run build"
```

Result: passed in 2m 49s. Vite emitted the existing large vendor chunk warning.

### Browser/CDP QA

Browser plugin `node_repl` was not exposed by tool discovery, so validation used a temporary headless Chrome on CDP port `9228`.

```powershell
node .ai/tasks/2026-06-05-agent-decision-snapshot/screenshot-decision-snapshot.cjs
```

Result: passed.

Verified:

- Selecting `工具执行分支` syncs Event Detail to the branch replay event.
- Event Detail renders `Decision Snapshot`.
- Snapshot includes `Status=needs_approval`, `Branch=工具执行分支`, `Type=tool_action`, `Quality=needs_approval`, `Score=87%`, and reason `审批或拒绝工具调用`.
- Existing Evidence, Tool, Timeline, Gate, Artifact, and Permission tokens remain visible below the snapshot.

Screenshot:

- `D:\dev\Worldline\.ai\tasks\2026-06-05-agent-decision-snapshot\screenshots\decision-snapshot-tool-branch.png`

## QA Finding And Fix

Initial browser QA failed because selecting a branch updated the canvas but did not synchronize Event Detail to the branch replay event. This made the new Decision Snapshot difficult to discover. The view now syncs Event Detail when a user selects a branch or canvas node, while internal token/dossier focus keeps the current event selection stable.

## Cleanup

- Temporary Chrome process was stopped.
- Temporary profile `D:\dev\Worldline\.ai\tasks\2026-06-05-agent-decision-snapshot\chrome-profile` was removed after confirming it resolved inside the task root.
