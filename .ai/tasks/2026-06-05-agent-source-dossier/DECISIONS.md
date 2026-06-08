# Decisions

## Source Dossier As Evidence-Derived View

Decision: implement Source Dossier as an Evidence-derived focus type in the Agent Workbench view, backed by optional local `sourceRef` metadata.

Reasoning: the current store exposes evidence/wiki/graph/timeline layers from the active branch. Adding a global `sourceRefs` store field now would widen the frontend contract and create avoidable migration work. Deriving Source from Evidence keeps the change narrow while matching the backend SourceAsset / DocumentNode direction.

## No File Opener

Decision: show exact `sourceUri:lineStart-lineEnd` in the Dossier, but do not wire a browser button that attempts to open a local editor.

Reasoning: the browser sandbox cannot reliably open local files, and cross-app editor integration would be a separate permission-sensitive workflow.
