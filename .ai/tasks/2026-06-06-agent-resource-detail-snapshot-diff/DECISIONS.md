# Decisions

## 2026-06-06

- Keep diff frontend-only for this stage; the existing artifact read endpoint already returns enough content for a useful comparison.
- Compare normalized JSON path/value pairs instead of line-based Markdown so the output stays stable for Agent replay.
- Disable `Diff Detail` until a current Resource Detail exists, keeping the action read-only and explicit.
