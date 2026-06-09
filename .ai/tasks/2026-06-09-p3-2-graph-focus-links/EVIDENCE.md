# Evidence

Date: 2026-06-09

## Initial Audit

- `GraphCanvas` exposes `focusNode(id)` and `clearFocus()`.
- `GraphView.vue` already accepts `db_id` / `knowledge_db_id`, but it does not parse `entity_id`, `fact_id`, or `evidence_id`.
- `WorldlineWorkbenchView.vue` can route to `/graph`, but currently passes only the general Worldline context query.
- `WikiSection.vue` shows citation evidence ids but has no direct graph focus action.

## Checks

## Implementation

- `GraphView.vue` now accepts `entity_id`, `fact_id`, `evidence_id`, `focus_layer`, and `focus_label` query params.
- `/graph` renders a compact route focus card and highlights matching conflict/timeline review items.
- Timeline/fact focus is prioritized ahead of broad evidence entity matches so the focus title remains stable.
- `WorldlineWorkbenchView.vue` now routes graph, timeline, and evidence rail focus events into `/graph` query params.
- `WorldlineGraphFocusPanel.vue` now emits explicit entity and timeline focus actions.
- `WikiSection.vue` citation rows include an `Open graph` action that routes with `evidence_id`.

## Build

- `git diff --check`: passed; Git reported only the existing CRLF normalization warning for `web/src/views/GraphView.vue`.
- `wsl -d Debian -- bash -lc 'cd /mnt/d/dev/Worldline && /home/joy/.local/bin/npm --prefix web run build'`: passed in about 3m03s on the final rerun; Vite reported the existing large chunk warning.
- `wsl -d Debian -- bash -lc 'cd /mnt/d/dev/Worldline && /home/joy/.local/bin/npm run docs:build'`: passed in about 25s.

## Browser QA

Temporary QA knowledge bases:

- `kb_codex_graph_conflict_20260609014621`: seeded, used for initial focus QA, then deleted.
- `kb_codex_graph_conflict_20260609015701`: seeded for final focus QA, then deleted.

Final focus URL used:

```text
http://127.0.0.1:5173/graph?db_id=kb_codex_graph_conflict_20260609015701&knowledge_db_id=kb_codex_graph_conflict_20260609015701&fact_id=tf_ff340a9ae47f051e89c828a34426fafc&evidence_id=ev_3b84e5ce8fa686f27a3c0cef72ebdeb0&focus_layer=timeline&focus_label=Graph%20timeline%20focus
```

Desktop DOM QA:

- `bodyClientWidth`: `1280`
- `bodyScrollWidth`: `1280`
- `overflowX`: `false`
- Focus card text included `ROUTE FOCUS`, `Graph`, `fact tf_ff340...26fafc`, `evidence ev_3b84e...ebdeb0`, and `5 matched`.
- `focusedItemCount`: `2`
- Focused items included the temporal conflict and the matching `Graph` timeline fact.
- Browser console warnings/errors captured by the QA hook: none.

Mobile DOM QA:

- Viewport: `390x844`
- `innerWidth`: `390`
- `bodyClientWidth`: `390`
- `bodyScrollWidth`: `390`
- `overflowX`: `false`
- `problemNodes`: `[]`
- Focus card text included `ROUTE FOCUS`, `Graph`, `fact tf_ff340...26fafc`, `evidence ev_3b84e...ebdeb0`, and `5 matched`.
- `focusedItemCount`: `2`
- Browser console warnings/errors captured by the QA hook: none.

Screenshot capture limitation:

- In the authenticated in-app Browser tab, `tab.screenshot({ fullPage: false })` repeatedly failed with `Timed out running CDP command "Page.captureScreenshot"` after the graph focus page loaded.
- Edge headless screenshots were attempted, but the separate headless profile had no app login token and captured the login surface instead of `/graph`; those misleading images were deleted.
- This slice therefore has DOM/layout QA evidence for desktop and `390x844`, but no final screenshot artifact.

## Cleanup

- `kb_codex_graph_conflict_20260609014621`: verified deleted (`false` exists check).
- `kb_codex_graph_conflict_20260609015701`: verified deleted (`false` exists check).
- Edge headless temporary profile was removed.
- Vite dev server logs were removed after stopping the local `5173` dev server.
