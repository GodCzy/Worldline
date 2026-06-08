# Evidence Graph Timeline Linkage Design

## Focus Types

The Agent Workbench already uses `inspectorFocus` as the single focus state. This task extends evidence-layer focus to:

- `evidence`
- `wiki`
- `graph`
- `timeline`

The `WorldlineEvidenceRail` component already accepts `activeLayer` and `activeItemId`, switches tabs, and highlights matching rail items.

## Dossier Links

Focus Dossier item records use the existing normalized chip model:

- `targetType`: `evidence`, `graph`, `timeline`, or `wiki`.
- `targetId`: stable item id.
- `layer`: Evidence Rail layer to activate.
- `canFocus`: only true when the target exists in current local state.

## Detail Pages

Graph Dossier shows entity id, type, confidence, and supporting evidence. Timeline Dossier already shows temporal bounds and supporting evidence; this task relies on the same generic evidence-layer focus path for the backlink.
