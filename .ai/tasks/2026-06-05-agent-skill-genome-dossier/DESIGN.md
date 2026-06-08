# Design

## Backend Capability Being Surfaced

`WorldlineRunLedgerService._normalize_skill_proposal` preserves normalized skill proposal fields and keeps the rest of the payload through `**payload`. The current UI only shows a shallow candidate card. This task makes the full skill genome visible and linkable.

## Interaction

- Skill cards keep the existing submit action.
- The whole card also becomes focusable with `role="button"` and keyboard handlers.
- Submit button stops event propagation so submitting does not accidentally change the inspector focus.
- Skill Dossier reuses existing Dossier items for permissions, gates, artifacts, and episodes.

## Visual Rules

- Keep the compact rail layout.
- Use chips and small metadata rows instead of a new panel.
- Avoid introducing a landing-page style section.
