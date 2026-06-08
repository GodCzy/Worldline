# Alignment

## Goal

Make the Agent Workbench Run Events rail more useful as an audit surface, not just a paginated event list.

## Scope

- Add client-side event audit filters for loaded events.
- Support text search across event type, actor, branch, summary, and ids.
- Support actor filter derived from currently loaded events.
- Add a JSON audit export for the currently filtered event set.
- Keep backend contracts unchanged.

## Acceptance Criteria

- The Run Events panel can filter loaded events by keyword and actor.
- Filtered counts are visible and resettable.
- Exported audit JSON includes run id, generated timestamp, filters, loaded/total counts, and filtered events.
- Existing event kind chips and event pagination still work.
- Build and Chrome CDP QA pass.

## Out Of Scope

- No server-side filter API.
- No database schema changes.
- No long-term artifact registration for event exports in this step.
