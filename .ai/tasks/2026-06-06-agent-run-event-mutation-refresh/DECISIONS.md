# Decisions

## 2026-06-06

- Reuse the existing event pagination endpoint rather than creating mutation-specific refresh endpoints.
- Refresh only the active run event rail after active mutations; selector-only mutations continue to refresh the selector list.
- Keep `latestEvent` merging as a compatible fallback, then let the paginated fetch establish the authoritative ordered window.
- Capture the event window size before each mutation. Mutation responses may append `latestEvent` locally, but the follow-up fetch should preserve the user's already-loaded window size and refresh that window from the backend.
