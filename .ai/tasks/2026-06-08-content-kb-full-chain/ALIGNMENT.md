# Content KB Full Chain

Date: 2026-06-08

## Goal

Verify a real, non-empty Worldline knowledge-base chain against the running API/Postgres stack:

`SourceAsset -> DocumentVersion -> DocumentNode -> EvidenceAnchor -> KnowledgeChunk -> WikiPage -> KnowledgeEntity -> KnowledgeRelationship -> TemporalFact -> QualityGateRun -> Worldline`

## Boundaries

- Use `D:\dev\Worldline` as the active source root.
- Do not rely on static adapters or mock-only frontend payloads for acceptance.
- Keep backend contracts compatible with existing `/api/knowledge/databases/{db_id}/worldline/*`, wiki, graph, timeline, quality-gate, and theme-module routes.
- Temporary admin, KB, theme module, and screenshots are QA artifacts only.
- Do not stage or commit the wider dirty worktree in this task.

## Acceptance

- A temporary KB with real content exists long enough for browser QA.
- API/service validation proves non-zero SourceAsset, DocumentVersion, DocumentNode, EvidenceAnchor, KnowledgeChunk, WikiPage, Entity, Relationship, TemporalFact, GoldenSetItem, QualityGateRun counts.
- Worldline overview and generation return `ready` and include branches with evidence, wiki, entity, timeline, and quality references.
- Browser QA opens the live Worldline route as an admin and captures desktop and mobile screenshots.
- Cleanup removes the temporary admin, theme module, and KB data after screenshots.
