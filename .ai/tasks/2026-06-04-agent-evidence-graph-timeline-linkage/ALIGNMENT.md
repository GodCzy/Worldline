# Evidence Graph Timeline Linkage Alignment

## Goal

Continue the Agent Workbench upgrade by making the evidence surface behave like a navigable worldline dossier, not a static support panel. Reviewers should move from Evidence to Graph Entity to Temporal Fact and back to the source EvidenceAnchor from the Focus Dossier.

## Scope

- Add focus support for Evidence Rail `graph` and `wiki` layers in the Agent Workbench inspector state.
- Convert Evidence Dossier related Graph and Time chips into clickable targets.
- Add Graph Entity Dossier details with a backlink to the supporting EvidenceAnchor.
- Preserve existing Timeline Dossier backlink to EvidenceAnchor and verify it works with the generalized evidence-layer focus.

## Out Of Scope

- No backend API or schema change.
- No new graph visualization package.
- No changes to the main Worldline canvas physics or branch model.
- No cleanup of unrelated reset worktree changes.

## Acceptance

- Focusing an evidence item opens a dossier with clickable Graph and Time chips.
- Clicking a Graph chip switches Evidence Rail to `Graph` and focuses the entity.
- The Graph Dossier exposes a clickable Evidence backlink.
- Clicking the Evidence backlink switches Evidence Rail back to `Evidence` and focuses the source anchor.
- Build and browser screenshot evidence are recorded.
