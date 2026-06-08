# Gate Artifact Linkage Design

## Interaction Model

Focus Dossier items become normalized records:

- `label`: visible chip text.
- `targetType`: `tool`, `artifact`, `gate`, or an unsupported passive type.
- `targetId`: target record id.
- `branchId`: optional branch to select before focusing.
- `canFocus`: whether the chip should be enabled.

## Scope Selection

When focusing an artifact from Dossier:

1. Select its branch if present.
2. Prefer Artifact Rail `event` scope if the selected event contains the artifact.
3. Prefer `branch` scope if the active branch contains the artifact.
4. Fall back to `all` so a known artifact is always visible.

When focusing a gate from Dossier:

1. Select its branch if present.
2. Prefer Gate Run `event`, then `branch`, then `all`.

## Reuse

The implementation reuses existing inspector focus state and `scrollToInspectorTarget`. No new store or route state is introduced.
