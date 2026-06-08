# Design

## Problem

The Agent Workbench currently exposes backend JSON and MCP args directly in the rail. This is complete but visually noisy, especially when a Resource Detail response is loaded.

## Proposed UI

Use a compact default view:

- Chinese section labels.
- Tool and URI remain visible.
- Primary actions remain buttons.
- Full backend payloads move into a modal opened by explicit buttons.

## Detail Modal

The modal is frontend-only state:

- `detailModalOpen`
- `detailModalTitle`
- `detailModalSubtitle`
- `detailModalBody`

It presents a title, short subtitle, scrollable preformatted body, and close button.

## Validation

Run existing diff artifact save QA and add assertions that the compact detail buttons are present and the modal can show backend content.
