# Decisions

## Use deterministic seed instead of external upload

Reason: P1-3 needs proof of the full backend knowledge chain, not Docling or MinIO stress. Seeding through `KnowledgeObjectRepository` exercises the protected storage contracts with reproducible content and avoids flaky external parsing dependencies.

## Keep browser route live by creating a temporary theme module

Reason: `/worldline/:themeId` filters available themes through live bridge capability metadata. Creating a temporary module is closer to the product path than passing only query params.

## Cleanup after screenshots, not immediately after API validation

Reason: The browser must read the same live KB and theme data. Cleanup is deferred until screenshots and console checks are recorded.
