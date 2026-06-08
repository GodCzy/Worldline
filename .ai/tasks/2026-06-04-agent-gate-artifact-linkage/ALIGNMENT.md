# Gate Artifact Linkage Alignment

## Goal

Connect the Agent Workbench Focus Dossier with the Gate Run Panel, Artifact Rail, and Tool Trace so reviewers can move from a quality gate to the exact generated artifact or tool call without scanning side panels manually.

## Scope

- Convert Focus Dossier context chips from passive text into focusable actions where the target is known.
- Let Gate Dossier artifact chips focus the Artifact Rail item and auto-select the most relevant artifact scope.
- Let Gate, Artifact, Permission, and Tool Dossier tool chips focus the Tool Trace item.
- Preserve existing local fallback rendering while the backend is unavailable.

## Out Of Scope

- No backend API changes.
- No schema or database changes.
- No new frontend dependency.
- No global UI restyle beyond the Dossier chip interaction states.

## Acceptance

- Permission risk gate can be focused from the Gate Run Panel.
- Its Focus Dossier exposes clickable tool and artifact chips.
- Clicking the workflow artifact chip focuses the Artifact Rail row and updates the dossier to the artifact.
- Build and screenshot evidence are captured.
