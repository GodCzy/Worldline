# Alignment

## Goal

Improve the knowledge database creation UI so it uses and clearly exposes backend create capabilities without making the modal cluttered.

## Scope

- Keep the default create modal concise.
- Add a collapsed advanced backend settings section for real backend create fields.
- Expose private database flag and storage override.
- Allow optional chunk parser config overrides for non-Dify databases.
- Add a compact backend request preview modal with sensitive Dify token masked.
- Preserve existing create API shape and backend contracts.

## Acceptance Criteria

- Main modal remains one-page style: required fields first, advanced settings collapsed.
- `buildRequestData()` includes `chunk_parser_config` only when overrides are enabled.
- Dify creation continues to require URL, token, dataset ID.
- Full backend payload can be inspected from the UI without showing token in plain text.
- Frontend build passes.

## Out Of Scope

- No backend schema/API changes.
- No query-params endpoint changes.
- No database detail page redesign.
