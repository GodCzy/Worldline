# Decisions

## Reuse the content-KB chain scripts

The P1-3 scripts already create a deterministic live KB and theme module through the correct repository/API boundaries. Reusing them avoids a second seeding mechanism and keeps cleanup consistent.

## Treat browser warnings as evidence, not automatic blockers

Known framework/library warnings are recorded. Blocking status is reserved for visible layout breakage, route failure, console errors, or mobile horizontal overflow.
