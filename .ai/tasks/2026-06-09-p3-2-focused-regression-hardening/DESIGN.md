# Design

## Problem

P3-2 graph focus behavior currently exists in component-local methods. That makes route parsing, evidence matching, canvas node lookup, and workbench-to-graph routing difficult to regression test without a full browser session.

## Approach

1. Add `web/src/utils/worldlineGraphFocus.js`.
2. Move pure focus helpers into that module:
   - query value normalization
   - stable ref ids and labels
   - graph focus query parsing
   - item evidence id matching
   - entity, relationship, timeline, and conflict match construction
   - canvas node candidate matching
   - outgoing `/graph` query construction
3. Keep Vue components responsible for rendering, route pushes, store state, and graph instance calls.
4. Add a small Node assertion test under `web/src/utils/__tests__/` and a package script.

## Evidence Plan

- Node assertion test for utility behavior.
- Existing focused pytest for live graph/timeline/projection contract.
- Frontend build.
- Docs build.
- Browser DOM/screenshot QA for `/graph` and `/worldline/:themeId` if the in-app Browser screenshot path is available.

## Risks

- Screenshot capture may still fail through the in-app Browser CDP path. If it does, record DOM/layout QA and the screenshot blocker honestly.
- The existing app has historical mojibake in some SFC display strings; this slice avoids touching those unrelated strings.
