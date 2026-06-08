# Gate Artifact Linkage Decisions

## Dossier Chips

Use buttons for focusable Dossier chips and disabled button styling for known-but-unfocusable chips. This keeps the visual chip language but gives reviewers a direct action surface.

## No New State Store

Keep linkage in `WorldlineAgentWorkbenchView.vue` because the state is local inspector state and does not need persistence.
