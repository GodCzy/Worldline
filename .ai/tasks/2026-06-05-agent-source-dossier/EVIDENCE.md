# Evidence

## Orientation

- Active root: `D:\dev\Worldline`.
- Pointer workspace: `D:\document\Worldline`.
- Branch: `codex/worldline-recovery-refactor`.
- Worktree was dirty before this stage; unrelated modified/deleted/untracked files were left untouched.

## Source Anchor Inspection

- `web/src/data/worldline/agentWorkbench.js` has three local EvidenceAnchor records with `sourceUri`, `lineStart`, and `lineEnd`.
- `server/routers/knowledge_router.py:1284-1443` exists and covers Worldline MCP manifest, overview, generate, workflow planning, golden set, and quality gate endpoints.
- `src/services/worldline_agent_workflow_service.py:10-122` exists and covers the controlled agent workflow lanes and tool definitions.
- `src/services/worldline_workbench_service.py:22-190` exists and covers SourceAsset / DocumentVersion / EvidenceAnchor imports and live workbench facade generation.

## Commands

### Static Checks

```powershell
git diff --check -- web/src/views/worldline/WorldlineAgentWorkbenchView.vue web/src/data/worldline/agentWorkbench.js .ai/tasks/2026-06-05-agent-source-dossier
```

Result: passed.

```powershell
rg -n "[ \t]+$" web/src/views/worldline/WorldlineAgentWorkbenchView.vue web/src/data/worldline/agentWorkbench.js .ai/tasks/2026-06-05-agent-source-dossier
```

Result: no trailing whitespace in target files.

### Frontend Build

```powershell
wsl -d Debian -- bash -lc "cd /mnt/d/dev/Worldline/web && npm run build"
```

Result: passed in 5m 39s. Vite emitted the existing large chunk warning for vendor bundles.

### Browser/CDP Validation

Browser plugin `node_repl` was not exposed by tool discovery, so validation used a temporary headless Chrome on CDP port `9226`.

```powershell
node .ai/tasks/2026-06-05-agent-source-dossier/screenshot-source-dossier.cjs
```

Result: passed.

Verified:

- Gate support strips include Source count: `Evidence 1Source 1Graph 1Time 2`.
- Evidence `ev-agent-workflow` exposes a Source link for `src/services/worldline_agent_workflow_service.py:10-122`.
- Source Dossier includes Source Asset, Source URI, Line Range, Document Node, Capability, and Evidence Anchor metadata.
- Source Dossier links back to Evidence Dossier.

Screenshots:

- `D:\dev\Worldline\.ai\tasks\2026-06-05-agent-source-dossier\screenshots\source-dossier-focus-viewport.png`
- `D:\dev\Worldline\.ai\tasks\2026-06-05-agent-source-dossier\screenshots\source-dossier-backlink-viewport.png`

Note: the first CDP assertion failed because it expected the internal `docnode-*` id, while the UI intentionally displays the readable Document Node label. The assertion was corrected to verify `Document Node`, readable label, line range, and backlink.

## Cleanup

- Temporary Chrome process was stopped.
- Temporary profile `D:\dev\Worldline\.ai\tasks\2026-06-05-agent-source-dossier\chrome-profile` was removed after confirming it resolved inside the task root.
