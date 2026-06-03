from __future__ import annotations

from typing import Any

from sqlalchemy import desc, func, select

from src.repositories.knowledge_graph_repository import KnowledgeGraphRepository
from src.repositories.knowledge_object_repository import KnowledgeObjectRepository
from src.repositories.wiki_repository import WikiRepository
from src.services.knowledge_graph_service import KnowledgeGraphService
from src.services.worldline_agent_workflow_service import WorldlineAgentWorkflowService
from src.storage.postgres.manager import pg_manager
from src.storage.postgres.models_knowledge import (
    DocumentVersion,
    EvidenceAnchor,
    GoldenSetItem,
    KnowledgeChunk,
    KnowledgeEntity,
    KnowledgeFile,
    KnowledgeRelationship,
    QualityGateRun,
    SourceAsset,
    TemporalFact,
    WikiPage,
    WorldlineMcpAuditLog,
    WorldlineWorkflowRun,
)


class WorldlineWorkbenchService:
    """Facade service for the live Worldline workbench.

    This composes existing deterministic baseline services. It deliberately avoids
    external model calls so the frontend can use a stable contract during recovery.
    """

    def __init__(
        self,
        object_repository: KnowledgeObjectRepository | None = None,
        wiki_repository: WikiRepository | None = None,
        graph_repository: KnowledgeGraphRepository | None = None,
        graph_service: KnowledgeGraphService | None = None,
        workflow_service: WorldlineAgentWorkflowService | None = None,
    ) -> None:
        self.object_repository = object_repository or KnowledgeObjectRepository()
        self.wiki_repository = wiki_repository or WikiRepository()
        self.graph_repository = graph_repository or KnowledgeGraphRepository()
        self.graph_service = graph_service or KnowledgeGraphService(repository=self.graph_repository)
        self.workflow_service = workflow_service or WorldlineAgentWorkflowService(repository=self.graph_repository)

    async def build_overview(self, db_id: str) -> dict[str, Any]:
        counts = await self._collect_counts(db_id)
        wiki_pages = await self.wiki_repository.list_pages(db_id, limit=8)
        entities = await self.graph_repository.list_entities(db_id, limit=8)
        relationships = await self.graph_repository.list_relationships(db_id, limit=8)
        timeline = await self.graph_repository.list_timeline(db_id, limit=8)
        evidence = await self.object_repository.list_evidence_anchors(db_id, limit=8)
        stale_report = await self.graph_service.detect_stale_pages(db_id)
        manifest = self.workflow_service.tool_manifest()
        audit_logs = await self.workflow_service.list_audit_logs(db_id, limit=8)
        latest_gate = await self._latest_quality_gate(db_id)

        has_knowledge = any(
            counts[key] > 0
            for key in (
                "source_assets",
                "document_versions",
                "evidence_anchors",
                "knowledge_chunks",
                "wiki_pages",
                "entities",
                "temporal_facts",
            )
        )

        return {
            "db_id": db_id,
            "status": "ready" if has_knowledge else "empty",
            "counts": counts,
            "evidence": evidence,
            "wiki": {
                "pages": wiki_pages,
                "stale": stale_report,
            },
            "graph": {
                "entities": entities,
                "relationships": relationships,
            },
            "timeline": timeline,
            "quality_gate": {
                "latest": latest_gate,
            },
            "mcp": {
                "manifest": manifest,
                "audit_logs": audit_logs,
            },
            "implementation": {
                "deterministic_baseline": True,
                "external_model_calls": 0,
                "notes": "Recovery facade over evidence/wiki/graph/timeline/MCP/quality-gate services.",
            },
        }

    async def generate_worldline(
        self,
        db_id: str,
        *,
        theme_id: str = "worldline",
        question: str = "",
        mode: str = "base",
        focus_branch_id: str | None = None,
        context: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        normalized_question = self._trim(
            question or "请基于当前知识库证据生成可验证的世界线分支。",
            220,
        )
        overview = await self.build_overview(db_id)
        evidence_items = list(overview["evidence"].get("items") or [])
        wiki_items = list(overview["wiki"]["pages"].get("items") or [])
        entity_items = list(overview["graph"]["entities"].get("items") or [])
        timeline_items = list(overview["timeline"].get("items") or [])

        branches = self._build_branches(
            db_id=db_id,
            theme_id=theme_id,
            question=normalized_question,
            evidence_items=evidence_items,
            wiki_items=wiki_items,
            entity_items=entity_items,
            timeline_items=timeline_items,
            context=context or {},
        )
        if focus_branch_id:
            branches = sorted(branches, key=lambda item: item["id"] != focus_branch_id)

        active_branch_id = branches[0]["id"] if branches else ""
        generation_mode = "focused" if mode == "focused" else "base"

        return {
            "themeId": theme_id or "worldline",
            "moduleId": theme_id or "worldline",
            "knowledgeDbId": db_id,
            "rootQuestion": normalized_question,
            "questionDraft": normalized_question,
            "status": "ready" if branches else "empty",
            "sourceType": "worldline-live-facade-v1",
            "generationMode": generation_mode,
            "generationRound": 2 if generation_mode == "focused" else 1,
            "branches": branches,
            "activeBranchId": active_branch_id,
            "selectedNodeId": active_branch_id,
            "tree": self._build_tree(branches, normalized_question),
            "viewState": {
                "lastGeneratedFrom": "live-generate",
                "protocolVersion": "worldline-live-v1",
            },
            "displayMeta": {
                "stageLabel": "真实知识库",
                "stageTitle": "基于证据、Wiki、图谱和时间线生成世界线",
                "stageSubtitle": "当前结果来自后端 Worldline facade；静态 adapter 只作为 fallback。",
                "branchCount": len(branches),
                "themeName": theme_id or "Worldline",
                "generationLabel": "生成真实世界线",
                "generationMode": generation_mode,
                "workspaceHint": "先检查证据支撑，再把分支带入 Agent 或 Graph 继续验证。",
            },
            "routeTrace": {
                "db_id": db_id,
                "facade": "WorldlineWorkbenchService",
                "deterministic_baseline": True,
                "counts": overview["counts"],
                "evidence_count": len(evidence_items),
                "wiki_page_count": len(wiki_items),
                "entity_count": len(entity_items),
                "timeline_count": len(timeline_items),
                "quality_gate_status": overview["quality_gate"]["latest"].get("status")
                if overview["quality_gate"]["latest"]
                else None,
            },
            "overview": {
                "status": overview["status"],
                "counts": overview["counts"],
                "quality_gate": overview["quality_gate"],
            },
        }

    async def _collect_counts(self, db_id: str) -> dict[str, int]:
        async with pg_manager.get_async_session_context() as session:
            source_assets = await session.scalar(
                select(func.count()).select_from(SourceAsset).where(SourceAsset.db_id == db_id)
            )
            document_versions = await session.scalar(
                select(func.count())
                .select_from(DocumentVersion)
                .join(SourceAsset, DocumentVersion.asset_id == SourceAsset.asset_id)
                .where(SourceAsset.db_id == db_id)
            )
            evidence_anchors = await session.scalar(
                select(func.count())
                .select_from(EvidenceAnchor)
                .join(DocumentVersion, EvidenceAnchor.doc_version_id == DocumentVersion.doc_version_id)
                .join(SourceAsset, DocumentVersion.asset_id == SourceAsset.asset_id)
                .where(SourceAsset.db_id == db_id)
            )
            files = await session.scalar(
                select(func.count()).select_from(KnowledgeFile).where(KnowledgeFile.db_id == db_id)
            )
            chunks = await session.scalar(
                select(func.count()).select_from(KnowledgeChunk).where(KnowledgeChunk.db_id == db_id)
            )
            wiki_pages = await session.scalar(select(func.count()).select_from(WikiPage).where(WikiPage.db_id == db_id))
            entities = await session.scalar(
                select(func.count()).select_from(KnowledgeEntity).where(KnowledgeEntity.db_id == db_id)
            )
            relationships = await session.scalar(
                select(func.count()).select_from(KnowledgeRelationship).where(KnowledgeRelationship.db_id == db_id)
            )
            temporal_facts = await session.scalar(
                select(func.count()).select_from(TemporalFact).where(TemporalFact.db_id == db_id)
            )
            golden_items = await session.scalar(
                select(func.count()).select_from(GoldenSetItem).where(GoldenSetItem.db_id == db_id)
            )
            quality_gate_runs = await session.scalar(
                select(func.count()).select_from(QualityGateRun).where(QualityGateRun.db_id == db_id)
            )
            workflow_runs = await session.scalar(
                select(func.count()).select_from(WorldlineWorkflowRun).where(WorldlineWorkflowRun.db_id == db_id)
            )
            mcp_audit_logs = await session.scalar(
                select(func.count()).select_from(WorldlineMcpAuditLog).where(WorldlineMcpAuditLog.db_id == db_id)
            )

        return {
            "source_assets": int(source_assets or 0),
            "document_versions": int(document_versions or 0),
            "evidence_anchors": int(evidence_anchors or 0),
            "knowledge_files": int(files or 0),
            "knowledge_chunks": int(chunks or 0),
            "wiki_pages": int(wiki_pages or 0),
            "entities": int(entities or 0),
            "relationships": int(relationships or 0),
            "temporal_facts": int(temporal_facts or 0),
            "golden_items": int(golden_items or 0),
            "quality_gate_runs": int(quality_gate_runs or 0),
            "workflow_runs": int(workflow_runs or 0),
            "mcp_audit_logs": int(mcp_audit_logs or 0),
        }

    async def _latest_quality_gate(self, db_id: str) -> dict[str, Any] | None:
        async with pg_manager.get_async_session_context() as session:
            run = (
                await session.execute(
                    select(QualityGateRun)
                    .where(QualityGateRun.db_id == db_id)
                    .order_by(desc(QualityGateRun.created_at), desc(QualityGateRun.id))
                    .limit(1)
                )
            ).scalar_one_or_none()
        return self.graph_repository.serialize_quality_gate_run(run) if run else None

    def _build_branches(
        self,
        *,
        db_id: str,
        theme_id: str,
        question: str,
        evidence_items: list[dict[str, Any]],
        wiki_items: list[dict[str, Any]],
        entity_items: list[dict[str, Any]],
        timeline_items: list[dict[str, Any]],
        context: dict[str, Any],
    ) -> list[dict[str, Any]]:
        branches: list[dict[str, Any]] = []
        if evidence_items:
            branches.append(
                self._branch(
                    db_id=db_id,
                    theme_id=theme_id,
                    branch_id="live-evidence",
                    title="证据优先世界线",
                    subtitle="先确认 EvidenceAnchor 再推进",
                    summary=self._summary_from_evidence(evidence_items, question),
                    choice_label="Evidence",
                    tone="calm",
                    evidence_refs=self._evidence_refs(evidence_items),
                    context={**context, "scene": "evidence_first", "entry": "worldline-live"},
                )
            )
        if wiki_items:
            branches.append(
                self._branch(
                    db_id=db_id,
                    theme_id=theme_id,
                    branch_id="live-wiki",
                    title="Auto-Wiki 世界线",
                    subtitle="从页面结构进入知识库",
                    summary=self._summary_from_wiki(wiki_items),
                    choice_label="Wiki",
                    tone="focus",
                    evidence_refs=self._evidence_refs(evidence_items),
                    context={**context, "scene": "auto_wiki", "entry": "worldline-live"},
                )
            )
        if entity_items or timeline_items:
            branches.append(
                self._branch(
                    db_id=db_id,
                    theme_id=theme_id,
                    branch_id="live-graph-timeline",
                    title="图谱与时间线世界线",
                    subtitle="检查实体、关系和事实变化",
                    summary=self._summary_from_graph(entity_items, timeline_items),
                    choice_label="Graph/Timeline",
                    tone="peak",
                    evidence_refs=self._evidence_refs(evidence_items),
                    context={**context, "scene": "graph_timeline", "entry": "worldline-live"},
                )
            )
        return branches[:3]

    def _branch(
        self,
        *,
        db_id: str,
        theme_id: str,
        branch_id: str,
        title: str,
        subtitle: str,
        summary: str,
        choice_label: str,
        tone: str,
        evidence_refs: list[dict[str, Any]],
        context: dict[str, Any],
    ) -> dict[str, Any]:
        return {
            "id": branch_id,
            "title": title,
            "subtitle": subtitle,
            "summary": self._trim(summary, 360),
            "branchTone": choice_label,
            "riskLabel": "可验证",
            "costLabel": "低扰动",
            "confidenceLabel": "后端证据基线",
            "routeTone": "先让来源、图谱和质量门禁可追溯，再进入下一层生成。",
            "tone": tone,
            "choiceLabel": choice_label,
            "suitability": ["真实后端", "证据优先", "可回放"],
            "focus": branch_id,
            "focusKey": branch_id,
            "candidateId": branch_id,
            "graphId": "worldline-live-graph",
            "buildId": "worldline-live-facade",
            "graphLabel": "Worldline Live Graph",
            "buildLabel": "Worldline Live Facade",
            "choiceReason": "该分支来自已持久化的 Worldline 知识对象，而不是静态 adapter 样本。",
            "switchHint": "如果证据不足，先重建 Wiki/Graph 或运行质量门禁，再继续生成。",
            "evidenceRefs": evidence_refs,
            "nextStepTitle": "继续验证此分支",
            "nextStepSubtitle": "把当前分支带入 Agent、Graph 或 Quality Gate 继续检查。",
            "nextGenerationLabel": "基于真实知识库继续生成",
            "nextActions": [
                {
                    "id": f"{branch_id}-chat",
                    "label": "带此分支去对话",
                    "description": "把真实知识库上下文交给 Agent 深聊。",
                    "targetType": "chat",
                    "emphasis": "primary",
                },
                {
                    "id": f"{branch_id}-graph",
                    "label": "查看图谱支撑",
                    "description": "进入图谱页检查实体、关系和时间线。",
                    "targetType": "graph",
                    "emphasis": "secondary",
                },
            ],
            "context": {
                **context,
                "theme": theme_id,
                "module": theme_id,
                "db_id": db_id,
                "knowledge_db_id": db_id,
                "focus": branch_id,
            },
        }

    def _build_tree(self, branches: list[dict[str, Any]], question: str) -> dict[str, Any]:
        root_node = {
            "id": "root-question",
            "type": "root",
            "title": "起始问题",
            "subtitle": self._trim(question, 56),
            "meta": "Live Query",
            "x": 120,
            "y": 280,
            "radius": 10,
            "branchId": "",
        }
        nodes = [root_node]
        edges = []
        for index, branch in enumerate(branches):
            y = 140 + index * 160
            nodes.append(
                {
                    "id": branch["id"],
                    "type": "branch",
                    "title": branch["title"],
                    "subtitle": branch["subtitle"],
                    "meta": f"{branch['choiceLabel']} / {branch['confidenceLabel']}",
                    "x": 420,
                    "y": y,
                    "radius": 9,
                    "branchId": branch["id"],
                    "tone": branch["tone"],
                }
            )
            nodes.append(
                {
                    "id": f"{branch['id']}-next",
                    "type": "next-step",
                    "title": "继续验证",
                    "subtitle": branch["nextStepSubtitle"],
                    "meta": "Agent / Graph / Gate",
                    "x": 760,
                    "y": y,
                    "radius": 8,
                    "branchId": branch["id"],
                    "tone": branch["tone"],
                }
            )
            edges.extend(
                [
                    {
                        "id": f"edge-root-{branch['id']}",
                        "source": "root-question",
                        "target": branch["id"],
                        "branchId": branch["id"],
                        "kind": "primary" if index == 0 else "secondary",
                        "label": branch["choiceLabel"],
                        "isHighlighted": index == 0,
                    },
                    {
                        "id": f"edge-next-{branch['id']}",
                        "source": branch["id"],
                        "target": f"{branch['id']}-next",
                        "branchId": branch["id"],
                        "kind": "guide",
                        "label": "继续验证",
                        "isHighlighted": index == 0,
                    },
                ]
            )
        return {
            "width": 1080,
            "height": max(560, 220 + len(branches) * 160),
            "nodes": nodes,
            "edges": edges,
        }

    def _evidence_refs(self, evidence_items: list[dict[str, Any]]) -> list[dict[str, Any]]:
        refs = []
        for item in evidence_items[:6]:
            refs.append(
                {
                    "id": item.get("evidence_id"),
                    "evidenceId": item.get("evidence_id"),
                    "title": item.get("source_title") or item.get("source_uri") or item.get("evidence_id"),
                    "type": item.get("anchor_type") or "evidence",
                    "typeLabel": "EvidenceAnchor",
                    "summary": self._trim(item.get("text_excerpt") or item.get("node", {}).get("text") or "", 180),
                    "sourceUri": item.get("source_uri"),
                    "page": item.get("page"),
                    "lineStart": item.get("line_start"),
                    "lineEnd": item.get("line_end"),
                    "bbox": item.get("bbox"),
                }
            )
        return refs

    def _summary_from_evidence(self, evidence_items: list[dict[str, Any]], question: str) -> str:
        excerpts = [item.get("text_excerpt") or item.get("node", {}).get("text") for item in evidence_items[:3]]
        excerpts = [self._trim(str(item), 120) for item in excerpts if item]
        if excerpts:
            return f"围绕“{question}”，当前最直接的证据来自：{' '.join(excerpts)}"
        return f"围绕“{question}”，当前知识库已经存在可追溯 EvidenceAnchor。"

    def _summary_from_wiki(self, wiki_items: list[dict[str, Any]]) -> str:
        titles = [item.get("title") for item in wiki_items[:4] if item.get("title")]
        return f"Auto-Wiki 已生成 {len(wiki_items)} 个页面，可先从 {', '.join(titles) if titles else '首页'} 进入知识结构。"

    def _summary_from_graph(self, entity_items: list[dict[str, Any]], timeline_items: list[dict[str, Any]]) -> str:
        entity_names = [item.get("name") for item in entity_items[:4] if item.get("name")]
        timeline_count = len(timeline_items)
        return (
            f"图谱当前覆盖 {len(entity_items)} 个实体，时间线包含 {timeline_count} 条事实；"
            f"优先检查 {', '.join(entity_names) if entity_names else '核心实体'} 的证据绑定。"
        )

    def _trim(self, value: str | None, limit: int) -> str:
        text = str(value or "").strip()
        if len(text) <= limit:
            return text
        return f"{text[:limit].rstrip()}..."
