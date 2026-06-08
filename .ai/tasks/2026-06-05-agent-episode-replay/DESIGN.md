# Design

## Contract Use

`src/services/worldline_run_ledger_service.py` already normalizes and preserves:

- `AgentEpisode.diffs`
- `AgentEpisode.screenshots`
- `AgentEpisode.artifactIds`

The frontend contract in `web/src/data/worldline/agentWorkbench.js` also declares these fields. This task turns those fields into visible replay affordances.

## UI Changes

- Episode cards become buttons with stable `data-inspector-target="episode:<id>"`.
- Each card shows compact counters for tools, gates, artifacts, diffs, screenshots, and cost.
- Episode Dossier appears in the existing inspector rail.
- Dossier links reuse the established focus contract for tool, gate, and artifact targets.
- Diff and screenshot records appear as non-focus dossier rows, because they are file/path evidence metadata rather than current UI targets.

## Risk Controls

- Keep changes inside the existing Vue single-file component and local preview data.
- Reuse current focus/scroll helpers and dossier normalizers.
- Keep text compact so the rail does not overflow.
