# Evidence

Date: 2026-06-09

## Initial Audit

- `test_worldline_live_services.py` already covers graph rebuild, timeline, temporal conflicts, and read-only Neo4j projection.
- `GraphView.vue` route focus helpers were component-local, so they could not be tested without rendering the full view.
- `/worldline/:themeId` graph navigation logic was also local to `WorldlineWorkbenchView.vue`.
- `GraphCanvas.vue` exposes `focusNode(id)` and `clearFocus()`, but node matching was not covered by a pure regression test.

## Checks

## Implementation

- Added `web/src/utils/worldlineGraphFocus.js` to centralize:
  - route query parsing
  - stable ref ids and labels
  - entity, relationship, timeline, conflict, and evidence focus matching
  - canvas node lookup for best-effort `GraphCanvas.focusNode()`
  - outbound `/graph` query construction from Wiki citations and `/worldline/:themeId`
- `GraphView.vue` now consumes the shared focus utility and includes relationship matches in the route focus card.
- `WorldlineWorkbenchView.vue` now builds graph focus links through the shared utility.
- `WikiSection.vue` now builds citation evidence links through the shared utility.
- `WorldlineWorkbenchService` now fills `entityRefs[].evidenceId` and `timelineRefs[].evidenceId` from `evidence_ids[]` when only array evidence is present.
- `test_worldline_live_services.py` now asserts evidence-bound relationships, projection evidence ids, and workbench graph/timeline refs.
- Added `web/src/utils/__tests__/worldlineGraphFocus.spec.js` and `web/package.json` script `test:worldline-focus`.

## Command Validation

- `wsl -d Debian -- bash -lc 'cd /mnt/d/dev/Worldline && /home/joy/.local/bin/npm --prefix web run test:worldline-focus'`
  - Passed.
  - Node reported the existing `MODULE_TYPELESS_PACKAGE_JSON` warning because `web/package.json` has no `"type": "module"`.
- Initial pytest command without `PYTHONPATH=.` failed during collection with `ModuleNotFoundError: No module named 'src'`.
- Corrected focused pytest:

```text
PYTHONPATH=. uv run --group test pytest \
  test/test_worldline_live_services.py::test_live_graph_timeline_and_stale_detector \
  test/test_worldline_live_services.py::test_temporal_conflicts_are_reviewable_in_timeline_and_projection \
  test/test_worldline_live_services.py::test_workbench_overview_and_generate
```

  - Passed: `3 passed, 1 warning in 8.51s`.
  - Warning: SQLAlchemy `declarative_base()` deprecation and existing `requests` dependency warning.
- `wsl -d Debian -- bash -lc 'cd /mnt/d/dev/Worldline && /home/joy/.local/bin/npm --prefix web run build'`
  - First run timed out at about 244s.
  - Rerun passed in `4m 24s`.
  - Vite reported existing large chunk warnings.
- `wsl -d Debian -- bash -lc 'cd /mnt/d/dev/Worldline && /home/joy/.local/bin/npm run docs:build'`
  - Passed in `16.05s`.
- `git diff --check`
  - Passed; Git reported only CRLF normalization warnings for `web/package.json` and `web/src/views/GraphView.vue`.

## Browser QA

Temporary QA KB:

- `db_id`: `kb_codex_graph_conflict_20260609032418`
- Seed command ran inside the API container with `PYTHONPATH=/app`.
- Seed result:
  - `entities=8`
  - `relationships=23`
  - `timeline=2`
  - `conflict_status=needs_review`
  - `conflict_count=1`
  - focused fact: `tf_1312d591528f199b18561c8a310e0756`
  - focused evidence: `ev_c22e8e00aaa803031aee5a1063040e97`

`/graph` focus URL:

```text
http://127.0.0.1:5173/graph?db_id=kb_codex_graph_conflict_20260609032418&knowledge_db_id=kb_codex_graph_conflict_20260609032418&fact_id=tf_1312d591528f199b18561c8a310e0756&evidence_id=ev_c22e8e00aaa803031aee5a1063040e97&focus_layer=timeline&focus_label=Graph%20timeline%20regression
```

Desktop `/graph` QA:

- Viewport: `1280x720`
- `bodyClientWidth=1280`, `bodyScrollWidth=1280`, `overflowX=false`.
- Route focus card visible.
- Metrics visible: `8 entities`, `23 relations`, `2 timeline`, `1 conflicts`.
- Focus card included timeline, conflict, and `RELATIONSHIP / CO_MENTIONS` chips.
- `focusedItemCount=3`.
- Screenshot: `D:\dev\Worldline\.ai\tasks\2026-06-09-p3-2-focused-regression-hardening\screenshots\graph-focus-desktop-1280x720.png`.

Mobile `/graph` QA:

- Viewport: `390x844`
- `bodyClientWidth=390`, `bodyScrollWidth=390`, `overflowX=false`.
- `problemNodes=[]`.
- Route focus card visible.
- Metrics visible: `8 entities`, `23 relations`, `2 timeline`, `1 conflicts`.
- Focus card included timeline, conflict, and relationship chips.
- `focusedItemCount=3`.
- Screenshot: `D:\dev\Worldline\.ai\tasks\2026-06-09-p3-2-focused-regression-hardening\screenshots\graph-focus-mobile-390x844.png`.

`/worldline/:themeId` live URL:

```text
http://127.0.0.1:5173/worldline/codex-graph-focus-regression?theme=codex-graph-focus-regression&module=codex-graph-focus-regression&db_id=kb_codex_graph_conflict_20260609032418&knowledge_db_id=kb_codex_graph_conflict_20260609032418
```

Desktop `/worldline/:themeId` QA:

- Viewport: `1280x720`
- `bodyClientWidth=1280`, `bodyScrollWidth=1280`, `overflowX=false`.
- Live facade generated successfully; not blocked.
- `2 条分支` visible.
- Evidence Rail visible with `11 条支撑`, `Graph 6`, `Time 2`.
- Graph Focus visible with `6 ENTITIES`, `2 TEMPORAL`, `DB kb_codex_graph_conflict_20260609032418`, `FACADE WorldlineWorkbenchService`.
- Screenshot: `D:\dev\Worldline\.ai\tasks\2026-06-09-p3-2-focused-regression-hardening\screenshots\worldline-live-desktop-1280x720.png`.

Mobile `/worldline/:themeId` QA:

- Viewport: `390x844`
- `bodyClientWidth=390`, `bodyScrollWidth=390`, `overflowX=false`.
- Live facade generated successfully; not blocked.
- `2 条分支`, Evidence Rail, and Graph Focus visible.
- `problemNodes` reported wide internal SVG nodes from the worldline canvas, but they did not create page-level horizontal overflow.
- Screenshot: `D:\dev\Worldline\.ai\tasks\2026-06-09-p3-2-focused-regression-hardening\screenshots\worldline-live-mobile-390x844.png`.

Console logs:

- Valid final QA routes had no relevant warning/error logs.
- Three earlier logs came from opening a stale historical route for `codex_ui_kb_1780918000`; they were excluded from final QA because that historical KB had already been cleaned up.

## Cleanup

- Cleanup command ran inside the API container using `cleanup_content_kb_full_chain.py`.
- Cleanup result: `kb_deleted=true` for `kb_codex_graph_conflict_20260609032418`.
- Deletion verification:

```text
{"db_id": "kb_codex_graph_conflict_20260609032418", "exists": false}
```
