# Design

## Artifact

The export artifact includes:

- protocol and export timestamp
- run metadata
- selected event
- current focus target
- focused Dossier
- replay timeline steps
- branches, episodes, tools, gates, artifacts, skills

## UI

The export controls live in the left Run Ledger rail:

- `Download JSON`
- `Copy Markdown`
- `Preview Artifact`

The preview is compact and scrollable to avoid disrupting the workbench layout.

## Risk Controls

- Browser-only export; no backend writes.
- Clipboard failure falls back to a visible status message.
- Download uses a temporary object URL and revokes it immediately after use.
