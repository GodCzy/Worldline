# Evidence

Date: 2026-06-08

## Validation Log

## Temporary QA Context

- Temporary KB: `codex_ui_kb_1780918000`
- Temporary theme: `codex-ui-1780918000`
- Temporary admin: `codex_ui_admin`
- Seed chain result:
  - `SourceAsset=1`
  - `DocumentVersion=1`
  - `EvidenceAnchor=5`
  - `WikiPage=11`
  - `KnowledgeEntity=20`
  - `KnowledgeRelationship=28`
  - `TemporalFact=3`
  - `QualityGateRun=1`
  - `Worldline status=ready`

## Screenshot Sweep

Routes captured at `1280x720` and `390x844`:

- `/`
- `/themes`
- `/themes/codex-ui-1780918000`
- `/worldline`
- `/worldline/codex-ui-1780918000?theme=codex-ui-1780918000&module=codex-ui-1780918000&db_id=codex_ui_kb_1780918000&knowledge_db_id=codex_ui_kb_1780918000`
- `/worldline/agent`
- `/graph?db_id=codex_ui_kb_1780918000&knowledge_db_id=codex_ui_kb_1780918000`
- `/database`
- `/dashboard`
- `/extensions`

Report:

- `D:\dev\Worldline\.ai\tasks\2026-06-08-full-site-ui-qa\screenshot-report.json`

Initial results:

- Document-level horizontal overflow: `false` for all mobile routes.
- Console error/warn logs: `0` for all captured routes.
- Blocking issue found: `/extensions` mobile layout kept desktop split panes, squeezed the main list to `54px`, and produced an internal horizontal scrollbar.

## Fix

Files changed:

- `D:\dev\Worldline\web\src\assets\css\extensions.less`
  - Added `max-width: 720px` single-column rules for extension page layout.
  - Sidebar/list and detail panel now stack vertically on small screens.
- `D:\dev\Worldline\web\src\views\ExtensionsView.vue`
  - Added mobile header wrapping and compact icon-only action buttons under `480px`.

Recheck:

- `D:\dev\Worldline\.ai\tasks\2026-06-08-full-site-ui-qa\extensions-recheck-report.json`
- Desktop screenshot: `D:\dev\Worldline\.ai\tasks\2026-06-08-full-site-ui-qa\screenshots\extensions-desktop-1280x720-fixed.jpg`
- Mobile screenshot: `D:\dev\Worldline\.ai\tasks\2026-06-08-full-site-ui-qa\screenshots\extensions-mobile-390x844-fixed.jpg`
- Recheck desktop: `hasHorizontalOverflow=false`, `visibleOverflow=[]`, `logCount=0`
- Recheck mobile: `hasHorizontalOverflow=false`, `visibleOverflow=[]`, `logCount=0`

## Cleanup

- `kb_deleted=true`
- `theme_deleted=true`
- `admin_deleted=true`

Verification:

- Temporary admin login returns `403`.
- Temporary theme visible in `/api/system/info`: `false`
- Temporary KB row exists: `false`

## Commands

- `git diff --check -- web/src/assets/css/extensions.less web/src/views/ExtensionsView.vue src/knowledge/manager.py test/test_worldline_live_services.py .ai/tasks/2026-06-08-full-site-ui-qa .ai/tasks/2026-06-08-content-kb-full-chain`
  - Passed; only CRLF warnings.
- `npm --prefix web run build`
  - Passed in about 5m9s.
  - Existing large chunk warning remains.
