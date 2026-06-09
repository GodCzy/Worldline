from __future__ import annotations

import time
from typing import Any

from sqlalchemy import func, select

from src.repositories.knowledge_graph_repository import KnowledgeGraphRepository
from src.repositories.knowledge_object_repository import KnowledgeObjectRepository
from src.services.knowledge_graph_service import KnowledgeGraphService
from src.services.worldline_agent_workflow_service import WorldlineAgentWorkflowService
from src.storage.postgres.manager import pg_manager
from src.storage.postgres.models_knowledge import (
    GoldenSetItem,
    KnowledgeEntity,
    KnowledgeRelationship,
    TemporalFact,
    WikiPage,
)
from src.utils import hashstr
from src.utils.datetime_utils import utc_now_naive


class WorldlineQualityGateService:
    """Deterministic evaluation and production-readiness gate."""

    DEFAULT_THRESHOLDS = {
        "evidence_accuracy_min": 0.95,
        "faithfulness_min": 0.90,
        "context_recall_min": 0.85,
        "context_precision_min": 0.80,
        "golden_items_min": 1,
        "stale_pages_max": 0,
        "temporal_conflicts_max": 0,
        "permission_checks_required": True,
    }

    def __init__(
        self,
        repository: KnowledgeGraphRepository | None = None,
        object_repository: KnowledgeObjectRepository | None = None,
        graph_service: KnowledgeGraphService | None = None,
        workflow_service: WorldlineAgentWorkflowService | None = None,
    ) -> None:
        self.repository = repository or KnowledgeGraphRepository()
        self.object_repository = object_repository or KnowledgeObjectRepository()
        self.graph_service = graph_service or KnowledgeGraphService(repository=self.repository)
        self.workflow_service = workflow_service or WorldlineAgentWorkflowService(repository=self.repository)

    async def build_golden_set(self, db_id: str, *, limit: int = 20) -> dict[str, Any]:
        entities = (await self.repository.list_entities(db_id, limit=limit))["items"]
        pages = await self.repository.list_wiki_pages(db_id)

        items = []
        for entity in entities:
            if not entity["evidence_ids"]:
                continue
            items.append(
                {
                    "item_id": self._golden_item_id(db_id, "entity", entity["entity_id"]),
                    "db_id": db_id,
                    "query": f"What evidence supports the entity {entity['name']}?",
                    "expected_evidence_ids": entity["evidence_ids"],
                    "expected_entity_ids": [entity["entity_id"]],
                    "coverage_tags": ["entity", "evidence"],
                    "status": "active",
                    "item_metadata": {
                        "source": "knowledge_entities",
                        "entity_name": entity["name"],
                    },
                }
            )
            if len(items) >= limit:
                break

        if len(items) < limit:
            for page in pages:
                evidence_ids = list(page.evidence_ids or [])
                if not evidence_ids:
                    continue
                items.append(
                    {
                        "item_id": self._golden_item_id(db_id, "wiki", page.page_id),
                        "db_id": db_id,
                        "query": f"What evidence supports the wiki page {page.title}?",
                        "expected_evidence_ids": evidence_ids[:20],
                        "expected_entity_ids": [],
                        "coverage_tags": ["wiki", page.page_type, "evidence"],
                        "status": "active",
                        "item_metadata": {
                            "source": "wiki_pages",
                            "page_id": page.page_id,
                            "page_type": page.page_type,
                        },
                    }
                )
                if len(items) >= limit:
                    break

        await self.repository.replace_golden_set(db_id, items)
        return {
            "db_id": db_id,
            "status": "success" if items else "empty",
            "item_count": len(items),
            "items": [
                {
                    "item_id": item["item_id"],
                    "query": item["query"],
                    "coverage_tags": item["coverage_tags"],
                    "expected_evidence_ids": item["expected_evidence_ids"],
                }
                for item in items
            ],
        }

    async def run_gate(
        self,
        db_id: str,
        *,
        thresholds: dict[str, Any] | None = None,
        created_by: str = "system",
    ) -> dict[str, Any]:
        started = time.perf_counter()
        effective_thresholds = dict(self.DEFAULT_THRESHOLDS)
        effective_thresholds.update(thresholds or {})

        golden_items = await self.repository.list_golden_set(db_id)
        if not golden_items:
            await self.build_golden_set(db_id)
            golden_items = await self.repository.list_golden_set(db_id)

        stale_report = await self.graph_service.detect_stale_pages(db_id)
        conflict_report = await self.graph_service.detect_temporal_conflicts(db_id)
        counts = await self._collect_counts(db_id)
        evidence_accuracy = await self._calculate_evidence_accuracy(db_id, counts)
        context_scores = self._calculate_context_scores(golden_items, evidence_accuracy)
        permission_checks = self._permission_checks()
        coverage_map = self._coverage_map(counts, stale_report, conflict_report, golden_items)

        metrics = {
            "evidence_accuracy": evidence_accuracy,
            "faithfulness": context_scores["faithfulness"],
            "context_recall": context_scores["context_recall"],
            "context_precision": context_scores["context_precision"],
            "golden_item_count": len(golden_items),
            "entity_count": counts["entities"],
            "relationship_count": counts["relationships"],
            "temporal_fact_count": counts["temporal_facts"],
            "wiki_page_count": counts["wiki_pages"],
            "stale_page_count": stale_report["stale_count"],
            "temporal_conflict_count": conflict_report["conflict_count"],
            "permission_checks_passed": permission_checks["passed"],
        }

        failures = self._evaluate_failures(metrics, effective_thresholds, permission_checks)
        latency_ms = round((time.perf_counter() - started) * 1000, 3)
        status = "passed" if not failures else "failed"
        gate_id = self._gate_id(db_id, metrics)
        replay_refs = (
            await self._build_replay_refs(
                db_id,
                gate_id=gate_id,
                status=status,
                metrics=metrics,
            )
            if failures
            else {}
        )

        payload = {
            "gate_id": gate_id,
            "db_id": db_id,
            "status": status,
            "thresholds": effective_thresholds,
            "metrics": metrics,
            "coverage_map": coverage_map,
            "failure_replay": self._failure_replay(
                db_id,
                failures,
                replay_refs=replay_refs,
                replay_thresholds=effective_thresholds,
            ),
            "tracing": {
                "trace_id": f"trace_{hashstr(gate_id, length=16)}",
                "phase": "worldline_quality_gate_v1",
                "service": "WorldlineQualityGateService",
                "deterministic": True,
            },
            "cost_stats": {
                "llm_calls": 0,
                "embedding_calls": 0,
                "estimated_usd": 0.0,
                "notes": "deterministic gate, no external model calls",
            },
            "latency_stats": {
                "total_ms": latency_ms,
                "stale_detection_ms": None,
                "coverage_eval_ms": None,
            },
            "permission_checks": permission_checks,
            "created_by": created_by,
            "completed_at": utc_now_naive(),
        }
        await self.repository.insert_quality_gate_run(payload)
        run = await self.repository.get_quality_gate_run(db_id, gate_id)
        return self.repository.serialize_quality_gate_run(run)

    async def get_gate_run(self, db_id: str, gate_id: str) -> dict[str, Any] | None:
        run = await self.repository.get_quality_gate_run(db_id, gate_id)
        return self.repository.serialize_quality_gate_run(run) if run else None

    async def _collect_counts(self, db_id: str) -> dict[str, int]:
        async with pg_manager.get_async_session_context() as session:
            entities = await session.scalar(
                select(func.count()).select_from(KnowledgeEntity).where(KnowledgeEntity.db_id == db_id)
            )
            relationships = await session.scalar(
                select(func.count()).select_from(KnowledgeRelationship).where(KnowledgeRelationship.db_id == db_id)
            )
            temporal_facts = await session.scalar(
                select(func.count()).select_from(TemporalFact).where(TemporalFact.db_id == db_id)
            )
            wiki_pages = await session.scalar(select(func.count()).select_from(WikiPage).where(WikiPage.db_id == db_id))
            golden_items = await session.scalar(
                select(func.count()).select_from(GoldenSetItem).where(GoldenSetItem.db_id == db_id)
            )
        return {
            "entities": int(entities or 0),
            "relationships": int(relationships or 0),
            "temporal_facts": int(temporal_facts or 0),
            "wiki_pages": int(wiki_pages or 0),
            "golden_items": int(golden_items or 0),
        }

    async def _calculate_evidence_accuracy(self, db_id: str, counts: dict[str, int]) -> float:
        async with pg_manager.get_async_session_context() as session:
            entity_rows = (
                await session.execute(select(KnowledgeEntity.evidence_ids).where(KnowledgeEntity.db_id == db_id))
            ).all()
            relationship_rows = (
                await session.execute(
                    select(KnowledgeRelationship.evidence_ids).where(KnowledgeRelationship.db_id == db_id)
                )
            ).all()
            temporal_rows = (
                await session.execute(select(TemporalFact.evidence_ids).where(TemporalFact.db_id == db_id))
            ).all()
            wiki_rows = (await session.execute(select(WikiPage.evidence_ids).where(WikiPage.db_id == db_id))).all()

        rows = [*entity_rows, *relationship_rows, *temporal_rows, *wiki_rows]
        denominator = sum(counts[key] for key in ("entities", "relationships", "temporal_facts", "wiki_pages"))
        if denominator == 0:
            return 0.0
        evidence_bound = sum(1 for row in rows if list(row[0] or []))
        return round(evidence_bound / denominator, 6)

    def _calculate_context_scores(
        self,
        golden_items: list[GoldenSetItem],
        evidence_accuracy: float,
    ) -> dict[str, float]:
        if not golden_items:
            return {"faithfulness": 0.0, "context_recall": 0.0, "context_precision": 0.0}

        evidence_backed_items = sum(1 for item in golden_items if list(item.expected_evidence_ids or []))
        entity_backed_items = sum(
            1
            for item in golden_items
            if list(item.expected_entity_ids or []) or "wiki" in list(item.coverage_tags or [])
        )
        context_recall = evidence_backed_items / len(golden_items)
        context_precision = entity_backed_items / len(golden_items)
        faithfulness = min(evidence_accuracy, context_recall, context_precision)
        return {
            "faithfulness": round(faithfulness, 6),
            "context_recall": round(context_recall, 6),
            "context_precision": round(context_precision, 6),
        }

    def _permission_checks(self) -> dict[str, Any]:
        manifest = self.workflow_service.tool_manifest()
        write_tools = [tool for tool in manifest["tools"] if tool["write_scope"] != "none"]
        all_write_tools_require_admin = all(tool.get("requires_admin") for tool in write_tools)
        passed = (
            all_write_tools_require_admin
            and manifest["security"]["external_agents_direct_db_write"] is False
            and manifest["security"]["secrets_in_manifest"] is False
        )
        return {
            "passed": passed,
            "all_write_tools_require_admin": all_write_tools_require_admin,
            "external_agents_direct_db_write": manifest["security"]["external_agents_direct_db_write"],
            "secrets_in_manifest": manifest["security"]["secrets_in_manifest"],
            "checked_tool_count": len(manifest["tools"]),
        }

    def _coverage_map(
        self,
        counts: dict[str, int],
        stale_report: dict[str, Any],
        conflict_report: dict[str, Any],
        golden_items: list[GoldenSetItem],
    ) -> dict[str, Any]:
        return {
            "graph": {
                "entities": counts["entities"],
                "relationships": counts["relationships"],
                "conflicts": conflict_report["conflict_count"],
                "covered": counts["entities"] > 0
                and counts["relationships"] > 0
                and conflict_report["conflict_count"] == 0,
            },
            "timeline": {
                "temporal_facts": counts["temporal_facts"],
                "covered": counts["temporal_facts"] > 0,
            },
            "wiki": {
                "pages": counts["wiki_pages"],
                "stale_pages": stale_report["stale_count"],
                "covered": counts["wiki_pages"] > 0 and stale_report["stale_count"] == 0,
            },
            "golden_set": {
                "items": len(golden_items),
                "covered": len(golden_items) > 0,
            },
            "production": {
                "tracing": True,
                "cost_stats": True,
                "latency_stats": True,
                "permission_checks": True,
            },
        }

    def _evaluate_failures(
        self,
        metrics: dict[str, Any],
        thresholds: dict[str, Any],
        permission_checks: dict[str, Any],
    ) -> list[dict[str, Any]]:
        failures = []
        if metrics["evidence_accuracy"] < float(thresholds["evidence_accuracy_min"]):
            failures.append(
                {
                    "check": "evidence_accuracy",
                    "observed": metrics["evidence_accuracy"],
                    "expected": f">= {thresholds['evidence_accuracy_min']}",
                }
            )
        if metrics["faithfulness"] < float(thresholds["faithfulness_min"]):
            failures.append(
                {
                    "check": "faithfulness",
                    "observed": metrics["faithfulness"],
                    "expected": f">= {thresholds['faithfulness_min']}",
                }
            )
        if metrics["context_recall"] < float(thresholds["context_recall_min"]):
            failures.append(
                {
                    "check": "context_recall",
                    "observed": metrics["context_recall"],
                    "expected": f">= {thresholds['context_recall_min']}",
                }
            )
        if metrics["context_precision"] < float(thresholds["context_precision_min"]):
            failures.append(
                {
                    "check": "context_precision",
                    "observed": metrics["context_precision"],
                    "expected": f">= {thresholds['context_precision_min']}",
                }
            )
        if metrics["golden_item_count"] < int(thresholds["golden_items_min"]):
            failures.append(
                {
                    "check": "golden_items",
                    "observed": metrics["golden_item_count"],
                    "expected": f">= {thresholds['golden_items_min']}",
                }
            )
        if metrics["stale_page_count"] > int(thresholds["stale_pages_max"]):
            failures.append(
                {
                    "check": "stale_pages",
                    "observed": metrics["stale_page_count"],
                    "expected": f"<= {thresholds['stale_pages_max']}",
                }
            )
        if metrics["temporal_conflict_count"] > int(thresholds["temporal_conflicts_max"]):
            failures.append(
                {
                    "check": "temporal_conflicts",
                    "observed": metrics["temporal_conflict_count"],
                    "expected": f"<= {thresholds['temporal_conflicts_max']}",
                }
            )
        if thresholds.get("permission_checks_required") and not permission_checks["passed"]:
            failures.append(
                {
                    "check": "permission_checks",
                    "observed": permission_checks,
                    "expected": "all controlled tool permissions pass",
                }
            )
        return failures

    async def _build_replay_refs(
        self,
        db_id: str,
        *,
        gate_id: str,
        status: str,
        metrics: dict[str, Any],
    ) -> dict[str, list[dict[str, Any]]]:
        evidence = (await self.object_repository.list_evidence_anchors(db_id, limit=3))["items"]
        wiki_pages = await self.repository.list_wiki_pages(db_id)
        entities = (await self.repository.list_entities(db_id, limit=3))["items"]
        timeline = (await self.repository.list_timeline(db_id, limit=3))["items"]

        return {
            "evidence": [self._evidence_replay_ref(item) for item in evidence if item.get("evidence_id")],
            "wiki": [self._wiki_replay_ref(page) for page in wiki_pages[:3] if page.page_id],
            "graph": [self._graph_replay_ref(item) for item in entities if item.get("entity_id")],
            "timeline": [self._timeline_replay_ref(item) for item in timeline if item.get("fact_id")],
            "run": [
                {
                    "id": gate_id,
                    "gate_id": gate_id,
                    "db_id": db_id,
                    "kind": "quality_gate_run",
                    "label": f"Quality Gate {status}",
                    "status": status,
                    "metrics": {
                        "evidence_accuracy": metrics.get("evidence_accuracy"),
                        "faithfulness": metrics.get("faithfulness"),
                        "context_recall": metrics.get("context_recall"),
                        "context_precision": metrics.get("context_precision"),
                    },
                }
            ],
        }

    def _evidence_replay_ref(self, item: dict[str, Any]) -> dict[str, Any]:
        return {
            "id": item.get("evidence_id"),
            "evidence_id": item.get("evidence_id"),
            "kind": "evidence",
            "label": item.get("source_title") or item.get("source_uri") or item.get("evidence_id"),
            "source_uri": item.get("source_uri"),
            "page": item.get("page"),
            "line_start": item.get("line_start"),
            "line_end": item.get("line_end"),
            "excerpt": item.get("text_excerpt"),
        }

    def _wiki_replay_ref(self, page: WikiPage) -> dict[str, Any]:
        evidence_ids = list(page.evidence_ids or [])
        return {
            "id": page.page_id,
            "page_id": page.page_id,
            "kind": "wiki",
            "label": page.title or page.slug or page.page_id,
            "slug": page.slug,
            "page_type": page.page_type,
            "evidence_id": evidence_ids[0] if evidence_ids else "",
            "evidence_ids": evidence_ids[:5],
            "status": page.status,
        }

    def _graph_replay_ref(self, item: dict[str, Any]) -> dict[str, Any]:
        evidence_ids = list(item.get("evidence_ids") or [])
        return {
            "id": item.get("entity_id"),
            "entity_id": item.get("entity_id"),
            "kind": "graph",
            "label": item.get("name") or item.get("entity_id"),
            "entity_type": item.get("entity_type"),
            "evidence_id": evidence_ids[0] if evidence_ids else "",
            "evidence_ids": evidence_ids[:5],
        }

    def _timeline_replay_ref(self, item: dict[str, Any]) -> dict[str, Any]:
        evidence_ids = list(item.get("evidence_ids") or [])
        return {
            "id": item.get("fact_id"),
            "fact_id": item.get("fact_id"),
            "kind": "timeline",
            "label": item.get("subject") or item.get("object") or item.get("fact_id"),
            "subject": item.get("subject"),
            "predicate": item.get("predicate"),
            "object": item.get("object"),
            "occurred_at": item.get("occurred_at"),
            "evidence_id": evidence_ids[0] if evidence_ids else "",
            "evidence_ids": evidence_ids[:5],
            "conflict_status": item.get("conflict_status"),
        }

    def _failure_replay(
        self,
        db_id: str,
        failures: list[dict[str, Any]],
        *,
        replay_refs: dict[str, list[dict[str, Any]]],
        replay_thresholds: dict[str, Any],
    ) -> list[dict[str, Any]]:
        return [
            {
                **failure,
                "reason": self._failure_reason(failure),
                "severity": self._failure_severity(failure.get("check")),
                "refs": replay_refs,
                "jump_targets": self._jump_targets(replay_refs),
                "replay": {
                    "method": "POST",
                    "path": f"/api/knowledge/databases/{db_id}/quality-gates/run",
                    "body": {"thresholds": replay_thresholds},
                },
            }
            for failure in failures
        ]

    def _failure_reason(self, failure: dict[str, Any]) -> str:
        check = failure.get("check")
        observed = failure.get("observed")
        expected = failure.get("expected")
        labels = {
            "evidence_accuracy": "Evidence coverage is below the required accuracy threshold.",
            "faithfulness": "The evidence-bound context is not faithful enough for promotion.",
            "context_recall": "The golden set cannot recall enough expected evidence.",
            "context_precision": "The golden set is not precise enough for the current branch.",
            "golden_items": "The knowledge base does not have enough active golden items.",
            "stale_pages": "One or more Wiki pages are stale against the graph/evidence layer.",
            "temporal_conflicts": "Temporal facts contain reviewable conflicts.",
            "permission_checks": "Controlled MCP or Agent write permissions did not pass.",
        }
        prefix = labels.get(str(check), "The quality gate check failed.")
        return f"{prefix} Observed {observed}; expected {expected}."

    def _failure_severity(self, check: str | None) -> str:
        if check in {"evidence_accuracy", "faithfulness", "temporal_conflicts", "permission_checks"}:
            return "high"
        if check in {"context_recall", "context_precision", "stale_pages"}:
            return "medium"
        return "warning"

    def _jump_targets(self, replay_refs: dict[str, list[dict[str, Any]]]) -> list[dict[str, Any]]:
        targets: list[dict[str, Any]] = []
        for kind in ("evidence", "wiki", "graph", "timeline", "run"):
            for ref in replay_refs.get(kind, [])[:2]:
                targets.append(
                    {
                        "kind": kind,
                        "label": ref.get("label") or ref.get("id") or kind,
                        "target_id": ref.get("id"),
                        "evidence_id": ref.get("evidence_id"),
                        "entity_id": ref.get("entity_id"),
                        "fact_id": ref.get("fact_id"),
                        "page_id": ref.get("page_id"),
                        "gate_id": ref.get("gate_id"),
                    }
                )
        return targets

    def _golden_item_id(self, db_id: str, item_type: str, source_id: str) -> str:
        return f"gold_{hashstr(f'{db_id}:golden:{item_type}:{source_id}', length=32)}"

    def _gate_id(self, db_id: str, metrics: dict[str, Any]) -> str:
        fingerprint = ":".join(f"{key}={metrics[key]}" for key in sorted(metrics))
        return f"gate_{hashstr(f'{db_id}:gate:{fingerprint}:{time.time_ns()}', length=32)}"
