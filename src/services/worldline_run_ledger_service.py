from __future__ import annotations

import asyncio
import json
import re
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import aiofiles

from src import config

_LEDGER_LOCK = asyncio.Lock()


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _safe_id(value: Any, prefix: str) -> str:
    candidate = str(value or "").strip().lower()
    candidate = re.sub(r"[^a-z0-9_-]+", "-", candidate)
    candidate = re.sub(r"-{2,}", "-", candidate).strip("-_")
    if candidate:
        return candidate[:96]
    return f"{prefix}_{uuid.uuid4().hex[:16]}"


def _as_dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _as_list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def _string_list(value: Any) -> list[str]:
    return [str(item).strip() for item in _as_list(value) if str(item).strip()]


def _unique_strings(values: list[Any]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        item = str(value or "").strip()
        if not item or item in seen:
            continue
        seen.add(item)
        result.append(item)
    return result


class WorldlineRunLedgerService:
    """File-backed Stage 2 ledger for Agent Worldline runs.

    This service deliberately avoids schema churn. It gives the workbench a
    durable API surface while later Postgres-backed tables are still being
    designed.
    """

    PROTOCOL_VERSION = "worldline-run-ledger-v0.1"
    COMPARE_CONTRACT_VERSION = "worldline-run-compare-v0.1"

    def __init__(self, storage_path: Path | None = None) -> None:
        self.storage_path = storage_path or Path(config.save_dir) / "worldline" / "runs.json"

    async def create_run(self, payload: dict[str, Any] | None = None, *, created_by: str = "system") -> dict[str, Any]:
        payload = _as_dict(payload)
        normalized = self._normalize_run(payload, created_by=created_by)
        event = self._event(
            normalized["id"],
            event_type="run.created",
            actor=created_by,
            summary=self._run_event_summary(normalized),
        )

        async with _LEDGER_LOCK:
            ledger = await self._load_ledger()
            ledger["runs"][normalized["id"]] = normalized
            ledger["events"].setdefault(normalized["id"], []).append(event)
            await self._save_ledger(ledger)

        return {**normalized, "events": [event]}

    async def get_run(self, run_id: str) -> dict[str, Any] | None:
        ledger = await self._load_ledger()
        run = ledger["runs"].get(run_id)
        if not run:
            return None
        return {**run, "events": ledger["events"].get(run_id, [])}

    async def list_runs(
        self,
        *,
        limit: int = 20,
        offset: int = 0,
        query: str = "",
        status: str = "",
        theme_id: str = "",
        created_by: str = "",
    ) -> dict[str, Any]:
        normalized_limit = max(1, min(int(limit or 20), 100))
        normalized_offset = max(0, int(offset or 0))
        filters = {
            "query": self._normalize_filter(query),
            "status": self._normalize_filter(status),
            "themeId": self._normalize_filter(theme_id),
            "createdBy": self._normalize_filter(created_by),
        }
        ledger = await self._load_ledger()
        runs = [_as_dict(item) for item in _as_dict(ledger.get("runs")).values() if isinstance(item, dict)]
        runs.sort(
            key=lambda item: str(item.get("updatedAt") or item.get("createdAt") or ""),
            reverse=True,
        )
        summaries = [self._run_summary(item, ledger=ledger) for item in runs]
        filtered = [item for item in summaries if self._run_summary_matches_filters(item, filters)]
        total = len(filtered)
        sliced = filtered[normalized_offset : normalized_offset + normalized_limit]
        return {
            "items": sliced,
            "total": total,
            "limit": normalized_limit,
            "offset": normalized_offset,
            "filters": filters,
            "storage": {"type": "worldline_run_ledger", "read_only": True},
        }

    async def compare_runs(self, left_run_id: str, right_run_id: str) -> dict[str, Any] | None:
        ledger = await self._load_ledger()
        left_run = ledger["runs"].get(left_run_id)
        right_run = ledger["runs"].get(right_run_id)
        if not left_run or not right_run:
            return None

        left_resources = self._run_resource_indexes(ledger, left_run_id, left_run)
        right_resources = self._run_resource_indexes(ledger, right_run_id, right_run)
        sections = {
            key: self._diff_resource_section(key, left_resources.get(key, {}), right_resources.get(key, {}))
            for key in self._run_diff_section_labels()
        }
        timeline = [
            {
                "key": key,
                "label": section["label"],
                "added": section["counts"]["added"],
                "removed": section["counts"]["removed"],
                "changed": section["counts"]["changed"],
                "shared": section["counts"]["shared"],
                "totalDelta": section["counts"]["added"] + section["counts"]["removed"] + section["counts"]["changed"],
            }
            for key, section in sections.items()
        ]
        summary = {
            "added": sum(section["counts"]["added"] for section in sections.values()),
            "removed": sum(section["counts"]["removed"] for section in sections.values()),
            "changed": sum(section["counts"]["changed"] for section in sections.values()),
            "shared": sum(section["counts"]["shared"] for section in sections.values()),
            "sectionsChanged": sum(1 for item in timeline if item["totalDelta"] > 0),
        }
        return {
            "status": "ok",
            "contractVersion": self.COMPARE_CONTRACT_VERSION,
            "left": self._run_summary(left_run, ledger=ledger),
            "right": self._run_summary(right_run, ledger=ledger),
            "summary": summary,
            "sections": sections,
            "timeline": timeline,
            "storage": {"type": "worldline_run_ledger", "read_only": True},
        }

    async def list_events(self, run_id: str, *, limit: int = 100, offset: int = 0) -> dict[str, Any] | None:
        ledger = await self._load_ledger()
        if run_id not in ledger["runs"]:
            return None
        events = ledger["events"].get(run_id, [])
        total = len(events)
        sliced = events[offset : offset + limit]
        return {"run_id": run_id, "items": sliced, "total": total, "limit": limit, "offset": offset}

    async def list_artifacts(self, run_id: str, *, limit: int = 100, offset: int = 0) -> dict[str, Any] | None:
        ledger = await self._load_ledger()
        run = ledger["runs"].get(run_id)
        if not run:
            return None
        artifacts = self._artifacts_for_run(ledger, run_id, run)
        total = len(artifacts)
        sliced = artifacts[offset : offset + limit]
        return {"run_id": run_id, "items": sliced, "total": total, "limit": limit, "offset": offset}

    async def list_gates(self, run_id: str, *, limit: int = 100, offset: int = 0) -> dict[str, Any] | None:
        ledger = await self._load_ledger()
        run = ledger["runs"].get(run_id)
        if not run:
            return None
        gates = [_as_dict(item) for item in _as_list(run.get("gateResults")) if isinstance(item, dict)]
        total = len(gates)
        sliced = gates[offset : offset + limit]
        return {"run_id": run_id, "items": sliced, "total": total, "limit": limit, "offset": offset}

    async def list_evidence(self, run_id: str, *, limit: int = 100, offset: int = 0) -> dict[str, Any] | None:
        ledger = await self._load_ledger()
        run = ledger["runs"].get(run_id)
        if not run:
            return None
        evidence = [_as_dict(item) for item in _as_list(run.get("evidenceRefs")) if isinstance(item, dict)]
        total = len(evidence)
        sliced = evidence[offset : offset + limit]
        return {"run_id": run_id, "items": sliced, "total": total, "limit": limit, "offset": offset}

    async def list_knowledge(
        self,
        run_id: str,
        *,
        kind: str = "all",
        limit: int = 100,
        offset: int = 0,
    ) -> dict[str, Any] | None:
        ledger = await self._load_ledger()
        run = ledger["runs"].get(run_id)
        if not run:
            return None
        items = self._knowledge_refs_for_run(run, kind=kind)
        total = len(items)
        sliced = items[offset : offset + limit]
        return {"run_id": run_id, "kind": kind or "all", "items": sliced, "total": total, "limit": limit, "offset": offset}

    async def register_artifact(
        self,
        run_id: str,
        payload: dict[str, Any] | None = None,
        *,
        actor: str = "system",
    ) -> dict[str, Any] | None:
        payload = _as_dict(payload)
        async with _LEDGER_LOCK:
            ledger = await self._load_ledger()
            run = ledger["runs"].get(run_id)
            if not run:
                return None

            artifact = self._normalize_registered_artifact(payload, run_id=run_id, actor=actor)
            artifacts = [
                item
                for item in self._artifacts_for_run(ledger, run_id, run)
                if _as_dict(item).get("id") != artifact["id"]
            ]
            artifacts.append(artifact)
            ledger.setdefault("artifacts", {})[run_id] = artifacts
            run["artifacts"] = artifacts
            run["updatedAt"] = _now_iso()
            run["qualitySummary"] = {
                **_as_dict(run.get("qualitySummary")),
                "artifactCount": len(artifacts),
            }

            event = self._event(
                run_id,
                event_type="artifact.registered",
                actor=actor,
                branch_id=artifact.get("branchId") or None,
                summary=self._artifact_event_summary(artifact),
            )
            ledger["runs"][run_id] = run
            ledger["events"].setdefault(run_id, []).append(event)
            await self._save_ledger(ledger)

        return {**run, "latestEvent": event, "artifact": artifact, "artifacts": artifacts}

    async def approve_branch(
        self,
        run_id: str,
        branch_id: str,
        payload: dict[str, Any] | None = None,
        *,
        actor: str = "system",
    ) -> dict[str, Any] | None:
        return await self._update_branch_status(
            run_id,
            branch_id,
            status="approved",
            event_type="branch.approved",
            payload=payload,
            actor=actor,
        )

    async def reject_branch(
        self,
        run_id: str,
        branch_id: str,
        payload: dict[str, Any] | None = None,
        *,
        actor: str = "system",
    ) -> dict[str, Any] | None:
        return await self._update_branch_status(
            run_id,
            branch_id,
            status="rejected",
            event_type="branch.rejected",
            payload=payload,
            actor=actor,
        )

    async def propose_skill(
        self,
        run_id: str,
        payload: dict[str, Any] | None = None,
        *,
        actor: str = "system",
    ) -> dict[str, Any] | None:
        payload = _as_dict(payload)
        async with _LEDGER_LOCK:
            ledger = await self._load_ledger()
            run = ledger["runs"].get(run_id)
            if not run:
                return None

            proposal = self._normalize_skill_proposal(payload, run_id=run_id)
            proposals = _as_list(run.get("skillProposals"))
            proposals = [item for item in proposals if _as_dict(item).get("id") != proposal["id"]]
            proposals.append(proposal)
            run["skillProposals"] = proposals
            run["updatedAt"] = _now_iso()
            run["qualitySummary"] = {
                **_as_dict(run.get("qualitySummary")),
                "skillProposalCount": len(proposals),
            }

            event = self._event(
                run_id,
                event_type="skill.proposed",
                actor=actor,
                branch_id=payload.get("branchId") or payload.get("branch_id"),
                summary=self._skill_event_summary(proposal),
            )
            ledger["runs"][run_id] = run
            ledger["events"].setdefault(run_id, []).append(event)
            await self._save_ledger(ledger)

        return {**run, "latestEvent": event, "skillProposal": proposal}

    async def rename_run(
        self,
        run_id: str,
        payload: dict[str, Any] | None = None,
        *,
        actor: str = "system",
    ) -> dict[str, Any] | None:
        payload = _as_dict(payload)
        title = str(payload.get("title") or payload.get("name") or "").strip()
        if not title:
            return None

        async with _LEDGER_LOCK:
            ledger = await self._load_ledger()
            run = ledger["runs"].get(run_id)
            if not run:
                return None

            old_title = str(run.get("title") or "")
            now = _now_iso()
            run["title"] = title
            run["updatedAt"] = now
            run["maintenance"] = {
                **_as_dict(run.get("maintenance")),
                "lastRenamedAt": now,
                "lastRenamedBy": actor,
            }
            event = self._event(
                run_id,
                event_type="run.renamed",
                actor=actor,
                summary={
                    "oldTitle": old_title,
                    "newTitle": title,
                    "reason": str(payload.get("reason") or payload.get("note") or "").strip(),
                },
            )
            ledger["runs"][run_id] = run
            ledger["events"].setdefault(run_id, []).append(event)
            await self._save_ledger(ledger)

        return {**run, "latestEvent": event}

    async def archive_run(
        self,
        run_id: str,
        payload: dict[str, Any] | None = None,
        *,
        actor: str = "system",
    ) -> dict[str, Any] | None:
        payload = _as_dict(payload)
        async with _LEDGER_LOCK:
            ledger = await self._load_ledger()
            run = ledger["runs"].get(run_id)
            if not run:
                return None

            previous_status = str(run.get("status") or "ready")
            now = _now_iso()
            run["status"] = "archived"
            run["archivedAt"] = now
            run["archivedBy"] = actor
            run["updatedAt"] = now
            run["maintenance"] = {
                **_as_dict(run.get("maintenance")),
                "archivedAt": now,
                "archivedBy": actor,
                "previousStatus": previous_status,
            }
            event = self._event(
                run_id,
                event_type="run.archived",
                actor=actor,
                summary={
                    "previousStatus": previous_status,
                    "status": "archived",
                    "reason": str(payload.get("reason") or payload.get("note") or "").strip(),
                },
            )
            ledger["runs"][run_id] = run
            ledger["events"].setdefault(run_id, []).append(event)
            await self._save_ledger(ledger)

        return {**run, "latestEvent": event}

    async def restore_run(
        self,
        run_id: str,
        payload: dict[str, Any] | None = None,
        *,
        actor: str = "system",
    ) -> dict[str, Any] | None:
        payload = _as_dict(payload)
        async with _LEDGER_LOCK:
            ledger = await self._load_ledger()
            run = ledger["runs"].get(run_id)
            if not run:
                return None

            maintenance = _as_dict(run.get("maintenance"))
            previous_status = str(run.get("status") or "ready").strip() or "ready"
            restored_status = str(maintenance.get("previousStatus") or "ready").strip() or "ready"
            if previous_status != "archived":
                restored_status = previous_status
            elif restored_status == "archived":
                restored_status = "ready"

            now = _now_iso()
            run["status"] = restored_status
            run["updatedAt"] = now
            run.pop("archivedAt", None)
            run.pop("archivedBy", None)
            run["maintenance"] = {
                **maintenance,
                "lastRestoredAt": now,
                "lastRestoredBy": actor,
                "restoredFromStatus": previous_status,
                "restoredToStatus": restored_status,
            }
            event = self._event(
                run_id,
                event_type="run.restored",
                actor=actor,
                summary={
                    "previousStatus": previous_status,
                    "status": restored_status,
                    "reason": str(payload.get("reason") or payload.get("note") or "").strip(),
                },
            )
            ledger["runs"][run_id] = run
            ledger["events"].setdefault(run_id, []).append(event)
            await self._save_ledger(ledger)

        return {**run, "latestEvent": event}

    async def _update_branch_status(
        self,
        run_id: str,
        branch_id: str,
        *,
        status: str,
        event_type: str,
        payload: dict[str, Any] | None = None,
        actor: str,
    ) -> dict[str, Any] | None:
        payload = _as_dict(payload)
        async with _LEDGER_LOCK:
            ledger = await self._load_ledger()
            run = ledger["runs"].get(run_id)
            if not run:
                return None

            branches = _as_list(run.get("branches"))
            branch_found = False
            event_branch: dict[str, Any] | None = None
            for branch in branches:
                if _as_dict(branch).get("id") != branch_id:
                    continue
                branch_found = True
                branch["status"] = status
                branch["updatedAt"] = _now_iso()
                branch["decision"] = {
                    "status": status,
                    "actor": actor,
                    "reason": payload.get("reason") or payload.get("note") or "",
                    "createdAt": branch["updatedAt"],
                }
                if status == "approved":
                    run["activeBranchId"] = branch_id
                    run["selectedNodeId"] = branch_id
                event_branch = _as_dict(branch)
                break

            if not branch_found:
                return None

            run["branches"] = branches
            run["status"] = "approved" if status == "approved" else run.get("status", "ready")
            run["updatedAt"] = _now_iso()
            event = self._event(
                run_id,
                event_type=event_type,
                actor=actor,
                branch_id=branch_id,
                summary=self._branch_event_summary(
                    run,
                    event_branch or {},
                    status=status,
                    reason=payload.get("reason") or payload.get("note") or "",
                ),
            )
            ledger["runs"][run_id] = run
            ledger["events"].setdefault(run_id, []).append(event)
            await self._save_ledger(ledger)

        return {**run, "latestEvent": event}

    def _normalize_run(self, payload: dict[str, Any], *, created_by: str) -> dict[str, Any]:
        run_meta = _as_dict(payload.get("run"))
        run_id = _safe_id(payload.get("id") or payload.get("run_id") or run_meta.get("id"), "run")
        now = _now_iso()
        root_question = str(payload.get("rootQuestion") or payload.get("goal") or run_meta.get("goal") or "").strip()
        title = str(payload.get("title") or run_meta.get("title") or "Worldline Agent Run").strip()
        branches = [self._normalize_branch(item) for item in _as_list(payload.get("branches")) if isinstance(item, dict)]
        episodes = [
            self._normalize_episode(item, run_id=run_id)
            for item in _as_list(payload.get("episodes"))
            if isinstance(item, dict)
        ]
        tool_traces = [
            self._normalize_tool_trace(item)
            for item in _as_list(payload.get("toolTraces") or payload.get("tool_traces"))
            if isinstance(item, dict)
        ]
        gate_results = [
            self._normalize_gate_result(item)
            for item in _as_list(payload.get("gateResults") or payload.get("gate_results"))
            if isinstance(item, dict)
        ]
        raw_evidence_refs = _as_list(payload.get("evidenceRefs") or payload.get("evidence_refs"))
        if not raw_evidence_refs:
            raw_evidence_refs = [
                evidence
                for branch in branches
                for evidence in _as_list(_as_dict(branch).get("evidenceRefs") or _as_dict(branch).get("evidence_refs"))
            ]
        evidence_refs = [
            self._normalize_evidence_ref(item)
            for item in raw_evidence_refs
            if isinstance(item, dict)
        ]
        wiki_refs = [
            self._normalize_wiki_ref(item)
            for item in self._raw_knowledge_refs(payload, branches, "wikiRefs", "wiki_refs")
            if isinstance(item, dict)
        ]
        entity_refs = [
            self._normalize_entity_ref(item)
            for item in self._raw_knowledge_refs(payload, branches, "entityRefs", "entity_refs")
            if isinstance(item, dict)
        ]
        timeline_refs = [
            self._normalize_timeline_ref(item)
            for item in self._raw_knowledge_refs(payload, branches, "timelineRefs", "timeline_refs")
            if isinstance(item, dict)
        ]
        skill_proposals = [
            self._normalize_skill_proposal(item, run_id=run_id)
            for item in _as_list(payload.get("skillProposals"))
            if isinstance(item, dict)
        ]

        active_branch_id = str(payload.get("activeBranchId") or run_meta.get("activeBranchId") or "").strip()
        if not active_branch_id and branches:
            active_branch_id = branches[0]["id"]

        return {
            "id": run_id,
            "title": title,
            "goal": root_question or "Inspect and evolve an Agent Worldline run.",
            "status": str(payload.get("status") or run_meta.get("status") or "ready"),
            "createdBy": str(run_meta.get("createdBy") or payload.get("createdBy") or created_by),
            "createdAt": str(payload.get("createdAt") or run_meta.get("createdAt") or now),
            "updatedAt": now,
            "protocolVersion": self.PROTOCOL_VERSION,
            "budget": _as_dict(run_meta.get("budget") or payload.get("budget")),
            "qualitySummary": {
                **_as_dict(run_meta.get("qualitySummary") or payload.get("qualitySummary") or payload.get("quality")),
                "branchCount": len(branches),
                "skillProposalCount": len(skill_proposals),
            },
            "themeId": str(payload.get("themeId") or payload.get("theme_id") or "agent-workbench"),
            "moduleId": str(payload.get("moduleId") or payload.get("module_id") or "agent-workbench"),
            "knowledgeDbId": str(payload.get("knowledgeDbId") or payload.get("knowledge_db_id") or ""),
            "rootQuestion": root_question,
            "branches": branches,
            "episodes": episodes,
            "toolTraces": tool_traces,
            "gateResults": gate_results,
            "evidenceRefs": evidence_refs,
            "wikiRefs": wiki_refs,
            "entityRefs": entity_refs,
            "timelineRefs": timeline_refs,
            "skillProposals": skill_proposals,
            "artifacts": _as_list(payload.get("artifacts")),
            "activeBranchId": active_branch_id,
            "selectedNodeId": str(payload.get("selectedNodeId") or active_branch_id),
            "tree": _as_dict(payload.get("tree")),
            "snapshots": _as_list(payload.get("snapshots")),
            "quality": _as_dict(payload.get("quality")),
            "routeTrace": _as_dict(payload.get("routeTrace")),
            "overview": _as_dict(payload.get("overview")),
            "metadata": {
                "source": "worldline-run-ledger",
                **_as_dict(payload.get("metadata")),
            },
        }

    def _run_summary(self, run: dict[str, Any], *, ledger: dict[str, Any]) -> dict[str, Any]:
        run_id = str(run.get("id") or "").strip()
        events = _as_list(_as_dict(ledger.get("events")).get(run_id))
        artifacts = self._artifacts_for_run(ledger, run_id, run) if run_id else []
        branches = _as_list(run.get("branches"))
        episodes = _as_list(run.get("episodes"))
        tool_traces = _as_list(run.get("toolTraces"))
        gate_results = _as_list(run.get("gateResults"))
        evidence_refs = _as_list(run.get("evidenceRefs"))
        wiki_refs = _as_list(run.get("wikiRefs"))
        entity_refs = _as_list(run.get("entityRefs"))
        timeline_refs = _as_list(run.get("timelineRefs"))
        skill_proposals = _as_list(run.get("skillProposals"))
        return {
            "id": run_id,
            "title": str(run.get("title") or "Worldline Agent Run"),
            "status": str(run.get("status") or "ready"),
            "createdAt": str(run.get("createdAt") or ""),
            "updatedAt": str(run.get("updatedAt") or run.get("createdAt") or ""),
            "createdBy": str(run.get("createdBy") or "system"),
            "themeId": str(run.get("themeId") or ""),
            "moduleId": str(run.get("moduleId") or ""),
            "knowledgeDbId": str(run.get("knowledgeDbId") or ""),
            "rootQuestion": str(run.get("rootQuestion") or run.get("goal") or ""),
            "activeBranchId": str(run.get("activeBranchId") or ""),
            "qualitySummary": _as_dict(run.get("qualitySummary")),
            "protocolVersion": str(run.get("protocolVersion") or self.PROTOCOL_VERSION),
            "counts": {
                "branches": len(branches),
                "episodes": len(episodes),
                "tools": len(tool_traces),
                "gates": len(gate_results),
                "artifacts": len(artifacts),
                "evidence": len(evidence_refs),
                "wiki": len(wiki_refs),
                "graph": len(entity_refs),
                "timeline": len(timeline_refs),
                "skills": len(skill_proposals),
                "events": len(events),
            },
        }

    def _normalize_filter(self, value: Any) -> str:
        return str(value or "").strip()

    def _run_summary_matches_filters(self, summary: dict[str, Any], filters: dict[str, str]) -> bool:
        query = filters.get("query", "").casefold()
        status = filters.get("status", "").casefold()
        theme_id = filters.get("themeId", "").casefold()
        created_by = filters.get("createdBy", "").casefold()

        if status and str(summary.get("status") or "").casefold() != status:
            return False
        if theme_id:
            candidates = [
                summary.get("themeId"),
                summary.get("moduleId"),
                summary.get("knowledgeDbId"),
            ]
            if theme_id not in {str(candidate or "").casefold() for candidate in candidates}:
                return False
        if created_by and created_by not in str(summary.get("createdBy") or "").casefold():
            return False
        if query:
            haystack = " ".join(
                str(summary.get(key) or "")
                for key in (
                    "id",
                    "title",
                    "status",
                    "createdBy",
                    "themeId",
                    "moduleId",
                    "knowledgeDbId",
                    "rootQuestion",
                    "activeBranchId",
                )
            ).casefold()
            if query not in haystack:
                return False
        return True

    def _run_diff_section_labels(self) -> dict[str, str]:
        return {
            "branches": "Branches",
            "episodes": "Episodes",
            "tools": "Tools",
            "gates": "Gates",
            "artifacts": "Artifacts",
            "evidence": "Evidence",
            "wiki": "Wiki",
            "graph": "Graph",
            "timeline": "Timeline",
            "skills": "Skills",
            "events": "Events",
        }

    def _run_resource_indexes(
        self,
        ledger: dict[str, Any],
        run_id: str,
        run: dict[str, Any],
    ) -> dict[str, dict[str, dict[str, Any]]]:
        events = _as_list(_as_dict(ledger.get("events")).get(run_id))
        return {
            "branches": self._resource_index(_as_list(run.get("branches")), kind="branch", id_keys=("id", "branchId")),
            "episodes": self._resource_index(_as_list(run.get("episodes")), kind="episode", id_keys=("id", "episodeId")),
            "tools": self._resource_index(_as_list(run.get("toolTraces")), kind="tool", id_keys=("id", "toolCallId")),
            "gates": self._resource_index(_as_list(run.get("gateResults")), kind="gate", id_keys=("id", "gateId")),
            "artifacts": self._resource_index(self._artifacts_for_run(ledger, run_id, run), kind="artifact", id_keys=("id", "artifactId")),
            "evidence": self._resource_index(_as_list(run.get("evidenceRefs")), kind="evidence", id_keys=("evidenceId", "id")),
            "wiki": self._resource_index(_as_list(run.get("wikiRefs")), kind="wiki", id_keys=("id", "slug")),
            "graph": self._resource_index(_as_list(run.get("entityRefs")), kind="graph", id_keys=("id", "name")),
            "timeline": self._resource_index(_as_list(run.get("timelineRefs")), kind="timeline", id_keys=("id", "temporalFactId")),
            "skills": self._resource_index(_as_list(run.get("skillProposals")), kind="skill", id_keys=("id", "name")),
            "events": self._resource_index(events, kind="event", id_keys=("id", "eventId")),
        }

    def _resource_index(
        self,
        items: list[Any],
        *,
        kind: str,
        id_keys: tuple[str, ...],
    ) -> dict[str, dict[str, Any]]:
        indexed: dict[str, dict[str, Any]] = {}
        for item in items:
            item_dict = _as_dict(item)
            if not item_dict:
                continue
            resource_id = self._resource_id(item_dict, id_keys=id_keys)
            if not resource_id:
                continue
            indexed[resource_id] = self._resource_descriptor(resource_id, item_dict, kind=kind)
        return indexed

    def _resource_id(self, item: dict[str, Any], *, id_keys: tuple[str, ...]) -> str:
        for key in id_keys:
            value = str(item.get(key) or "").strip()
            if value:
                return value
        return ""

    def _resource_descriptor(self, resource_id: str, item: dict[str, Any], *, kind: str) -> dict[str, Any]:
        label = str(item.get("title") or item.get("label") or item.get("name") or item.get("eventType") or resource_id)
        status = str(item.get("status") or item.get("state") or "")
        type_label = str(item.get("branchType") or item.get("type") or item.get("kind") or kind)
        summary = item.get("summary")
        if isinstance(summary, dict):
            summary_text = json.dumps(summary, ensure_ascii=False, sort_keys=True)
        else:
            summary_text = str(summary or item.get("description") or item.get("hypothesis") or "")
        return {
            "id": resource_id,
            "label": label,
            "status": status,
            "type": type_label,
            "summary": summary_text[:280],
            "signature": {
                "label": label,
                "status": status,
                "type": type_label,
                "summary": summary_text,
            },
        }

    def _diff_resource_section(
        self,
        key: str,
        left: dict[str, dict[str, Any]],
        right: dict[str, dict[str, Any]],
    ) -> dict[str, Any]:
        left_ids = set(left)
        right_ids = set(right)
        added_ids = sorted(right_ids - left_ids)
        removed_ids = sorted(left_ids - right_ids)
        shared_ids = sorted(left_ids & right_ids)
        changed_ids = [
            item_id
            for item_id in shared_ids
            if left[item_id].get("signature") != right[item_id].get("signature")
        ]
        unchanged_ids = [item_id for item_id in shared_ids if item_id not in set(changed_ids)]
        labels = self._run_diff_section_labels()
        return {
            "key": key,
            "label": labels.get(key, key.title()),
            "counts": {
                "added": len(added_ids),
                "removed": len(removed_ids),
                "changed": len(changed_ids),
                "shared": len(unchanged_ids),
            },
            "added": [self._public_resource_descriptor(right[item_id]) for item_id in added_ids[:12]],
            "removed": [self._public_resource_descriptor(left[item_id]) for item_id in removed_ids[:12]],
            "changed": [
                {
                    "id": item_id,
                    "before": self._public_resource_descriptor(left[item_id]),
                    "after": self._public_resource_descriptor(right[item_id]),
                }
                for item_id in changed_ids[:12]
            ],
            "shared": [self._public_resource_descriptor(left[item_id]) for item_id in unchanged_ids[:12]],
        }

    def _public_resource_descriptor(self, item: dict[str, Any]) -> dict[str, Any]:
        return {
            "id": item.get("id", ""),
            "label": item.get("label", ""),
            "status": item.get("status", ""),
            "type": item.get("type", ""),
            "summary": item.get("summary", ""),
        }

    def _normalize_branch(self, payload: dict[str, Any]) -> dict[str, Any]:
        branch_id = _safe_id(payload.get("id") or payload.get("branch_id") or payload.get("title"), "branch")
        return {
            **payload,
            "id": branch_id,
            "parentId": str(payload.get("parentId") or payload.get("parent_id") or ""),
            "branchType": str(payload.get("branchType") or payload.get("branch_type") or payload.get("type") or "branch"),
            "hypothesis": str(payload.get("hypothesis") or payload.get("subtitle") or ""),
            "action": _as_dict(payload.get("action")),
            "result": _as_dict(payload.get("result")),
            "evidenceIds": _string_list(payload.get("evidenceIds") or payload.get("evidence_ids")),
            "toolCallIds": _string_list(payload.get("toolCallIds") or payload.get("tool_call_ids")),
            "temporalFactIds": _string_list(payload.get("temporalFactIds") or payload.get("temporal_fact_ids")),
            "status": str(payload.get("status") or _as_dict(payload.get("quality")).get("status") or "ready"),
            "score": float(payload.get("score") or 0),
            "gateResultIds": _string_list(payload.get("gateResultIds") or payload.get("gateResults") or payload.get("gate_result_ids")),
        }

    def _normalize_episode(self, payload: dict[str, Any], *, run_id: str) -> dict[str, Any]:
        return {
            **payload,
            "id": _safe_id(payload.get("id"), "episode"),
            "runId": str(payload.get("runId") or payload.get("run_id") or run_id),
            "branchId": str(payload.get("branchId") or payload.get("branch_id") or ""),
            "actor": str(payload.get("actor") or "agent"),
            "toolCalls": _string_list(payload.get("toolCalls") or payload.get("tool_calls")),
            "diffs": _as_list(payload.get("diffs")),
            "screenshots": _as_list(payload.get("screenshots")),
            "gateResults": _string_list(payload.get("gateResults") or payload.get("gate_results")),
            "artifactIds": _string_list(payload.get("artifactIds") or payload.get("artifact_ids")),
        }

    def _normalize_artifact(self, payload: dict[str, Any]) -> dict[str, Any]:
        artifact_id = _safe_id(payload.get("id") or payload.get("path") or payload.get("uri") or payload.get("label"), "artifact")
        return {
            **payload,
            "id": artifact_id,
            "label": str(payload.get("label") or payload.get("title") or artifact_id),
            "type": str(payload.get("type") or payload.get("kind") or "artifact"),
            "path": str(payload.get("path") or payload.get("uri") or ""),
            "summary": str(payload.get("summary") or payload.get("description") or ""),
        }

    def _normalize_registered_artifact(
        self,
        payload: dict[str, Any],
        *,
        run_id: str,
        actor: str,
    ) -> dict[str, Any]:
        artifact_payload = _as_dict(payload.get("artifact"))
        content = payload.get("content")
        if content is None:
            content = artifact_payload or _as_dict(payload)
        content_dict = _as_dict(content)
        selected_event = _as_dict(content_dict.get("selectedEvent"))
        focused_dossier = _as_dict(content_dict.get("focusedDossier"))
        event_id = str(payload.get("eventId") or selected_event.get("id") or artifact_payload.get("eventId") or "").strip()
        branch_id = str(payload.get("branchId") or selected_event.get("branchId") or artifact_payload.get("branchId") or "").strip()
        kind = str(payload.get("kind") or artifact_payload.get("kind") or "replay_export")
        label = str(
            payload.get("label")
            or artifact_payload.get("label")
            or _as_dict(content_dict.get("run")).get("title")
            or "Worldline Replay Export"
        ).strip()
        now = _now_iso()
        artifact_id = _safe_id(payload.get("id") or artifact_payload.get("id") or f"{kind}-{event_id or label}", "artifact")
        markdown = str(payload.get("markdown") or payload.get("contentMarkdown") or artifact_payload.get("markdown") or "")
        content_size = len(json.dumps(content, ensure_ascii=False, default=str)) if content is not None else 0
        summary = str(payload.get("summary") or artifact_payload.get("summary") or "").strip()
        if not summary:
            summary = self._registered_artifact_summary_text(content_dict, selected_event, focused_dossier)
        return {
            "id": artifact_id,
            "runId": run_id,
            "eventId": event_id,
            "branchId": branch_id,
            "kind": kind,
            "format": str(payload.get("format") or artifact_payload.get("format") or "json+markdown"),
            "label": label,
            "summary": summary,
            "content": content,
            "markdown": markdown,
            "size": content_size + len(markdown),
            "createdBy": actor,
            "createdAt": str(payload.get("createdAt") or artifact_payload.get("createdAt") or now),
            "updatedAt": now,
        }

    def _normalize_tool_trace(self, payload: dict[str, Any]) -> dict[str, Any]:
        name = str(payload.get("name") or payload.get("tool") or payload.get("id") or "worldline.tool").strip()
        artifacts = [
            self._normalize_artifact(item)
            for item in _as_list(payload.get("artifacts"))
            if isinstance(item, dict)
        ]
        artifact_ids = _unique_strings(
            [
                *_string_list(payload.get("artifactIds") or payload.get("artifact_ids")),
                *[item["id"] for item in artifacts],
            ]
        )
        return {
            **payload,
            "id": _safe_id(payload.get("id") or name, "tool"),
            "branchId": str(payload.get("branchId") or payload.get("branch_id") or ""),
            "name": name,
            "status": str(payload.get("status") or "pending"),
            "permission": str(payload.get("permission") or payload.get("requiredPermission") or payload.get("required_permission") or "read"),
            "summary": str(payload.get("summary") or payload.get("description") or ""),
            "result": str(payload.get("result") or payload.get("output") or ""),
            "parameters": _as_dict(payload.get("parameters") or payload.get("input") or payload.get("args")),
            "artifactIds": artifact_ids,
            "artifacts": artifacts,
            "failureReason": str(payload.get("failureReason") or payload.get("failure_reason") or ""),
        }

    def _normalize_gate_result(self, payload: dict[str, Any]) -> dict[str, Any]:
        gate_id = _safe_id(payload.get("id") or payload.get("gateId") or payload.get("gate_id") or payload.get("label"), "gate")
        return {
            **payload,
            "id": gate_id,
            "label": str(payload.get("label") or payload.get("name") or gate_id),
            "status": str(payload.get("status") or "pending"),
            "value": str(payload.get("value") or payload.get("score") or ""),
            "summary": str(payload.get("summary") or payload.get("description") or ""),
            "branchId": str(payload.get("branchId") or payload.get("branch_id") or ""),
            "threshold": str(payload.get("threshold") or payload.get("criteria") or ""),
            "input": str(payload.get("input") or payload.get("inputSummary") or payload.get("input_summary") or ""),
            "toolCallIds": _string_list(payload.get("toolCallIds") or payload.get("tool_call_ids")),
            "artifactIds": _string_list(payload.get("artifactIds") or payload.get("artifact_ids")),
            "failureReason": str(payload.get("failureReason") or payload.get("failure_reason") or ""),
            "remediation": str(payload.get("remediation") or payload.get("fix") or payload.get("nextStep") or payload.get("next_step") or ""),
        }

    def _normalize_evidence_ref(self, payload: dict[str, Any]) -> dict[str, Any]:
        evidence_id = _safe_id(
            payload.get("evidenceId") or payload.get("evidence_id") or payload.get("id") or payload.get("title"),
            "evidence",
        )
        source_ref = _as_dict(payload.get("sourceRef") or payload.get("source_ref"))
        return {
            **payload,
            "id": str(payload.get("id") or evidence_id),
            "evidenceId": evidence_id,
            "title": str(payload.get("title") or evidence_id),
            "type": str(payload.get("type") or "evidence"),
            "typeLabel": str(payload.get("typeLabel") or payload.get("type_label") or "EvidenceAnchor"),
            "summary": str(payload.get("summary") or payload.get("description") or ""),
            "sourceUri": str(payload.get("sourceUri") or payload.get("source_uri") or source_ref.get("sourceUri") or ""),
            "lineStart": payload.get("lineStart") or payload.get("line_start"),
            "lineEnd": payload.get("lineEnd") or payload.get("line_end"),
            "page": payload.get("page"),
            "bbox": payload.get("bbox"),
            "sourceRef": source_ref,
        }

    def _raw_knowledge_refs(
        self,
        payload: dict[str, Any],
        branches: list[dict[str, Any]],
        camel_key: str,
        snake_key: str,
    ) -> list[Any]:
        refs = _as_list(payload.get(camel_key) or payload.get(snake_key))
        if refs:
            return refs
        return [
            item
            for branch in branches
            for item in _as_list(_as_dict(branch).get(camel_key) or _as_dict(branch).get(snake_key))
        ]

    def _normalize_wiki_ref(self, payload: dict[str, Any]) -> dict[str, Any]:
        wiki_id = _safe_id(payload.get("id") or payload.get("slug") or payload.get("title"), "wiki")
        return {
            **payload,
            "id": str(payload.get("id") or wiki_id),
            "title": str(payload.get("title") or payload.get("slug") or wiki_id),
            "slug": str(payload.get("slug") or wiki_id),
            "status": str(payload.get("status") or "draft"),
            "evidenceCoverage": payload.get("evidenceCoverage") or payload.get("evidence_coverage") or 0,
            "summary": str(payload.get("summary") or payload.get("description") or ""),
            "evidenceIds": _string_list(payload.get("evidenceIds") or payload.get("evidence_ids")),
        }

    def _normalize_entity_ref(self, payload: dict[str, Any]) -> dict[str, Any]:
        entity_id = _safe_id(payload.get("id") or payload.get("name") or payload.get("label"), "entity")
        return {
            **payload,
            "id": str(payload.get("id") or entity_id),
            "name": str(payload.get("name") or payload.get("label") or entity_id),
            "type": str(payload.get("type") or payload.get("kind") or "entity"),
            "confidence": payload.get("confidence") or 0,
            "evidenceId": str(payload.get("evidenceId") or payload.get("evidence_id") or ""),
            "summary": str(payload.get("summary") or payload.get("description") or ""),
        }

    def _normalize_timeline_ref(self, payload: dict[str, Any]) -> dict[str, Any]:
        fact_id = _safe_id(payload.get("id") or payload.get("label") or payload.get("title"), "fact")
        return {
            **payload,
            "id": str(payload.get("id") or fact_id),
            "label": str(payload.get("label") or payload.get("title") or fact_id),
            "validFrom": str(payload.get("validFrom") or payload.get("valid_from") or ""),
            "validTo": str(payload.get("validTo") or payload.get("valid_to") or ""),
            "status": str(payload.get("status") or "observed"),
            "evidenceId": str(payload.get("evidenceId") or payload.get("evidence_id") or ""),
            "summary": str(payload.get("summary") or payload.get("description") or ""),
        }

    def _knowledge_refs_for_run(self, run: dict[str, Any], *, kind: str = "all") -> list[dict[str, Any]]:
        normalized_kind = str(kind or "all").strip().lower()
        groups = [
            ("wiki", "wikiRefs"),
            ("graph", "entityRefs"),
            ("timeline", "timelineRefs"),
        ]
        if normalized_kind not in {"all", "wiki", "graph", "timeline"}:
            return []
        items: list[dict[str, Any]] = []
        for item_kind, key in groups:
            if normalized_kind not in {"all", item_kind}:
                continue
            items.extend(
                {"kind": item_kind, **_as_dict(item)}
                for item in _as_list(run.get(key))
                if isinstance(item, dict)
            )
        return items

    def _normalize_skill_proposal(self, payload: dict[str, Any], *, run_id: str) -> dict[str, Any]:
        name = str(payload.get("name") or "Worldline Skill Proposal").strip()
        return {
            **payload,
            "id": _safe_id(payload.get("id") or name, "skill"),
            "name": name,
            "trigger": str(payload.get("trigger") or ""),
            "steps": _string_list(payload.get("steps")),
            "requiredPermissions": _string_list(payload.get("requiredPermissions") or payload.get("required_permissions")),
            "evidenceRunIds": _string_list(payload.get("evidenceRunIds") or payload.get("evidence_run_ids") or [run_id]),
            "evalScore": float(payload.get("evalScore") or payload.get("eval_score") or 0),
            "status": str(payload.get("status") or "candidate"),
        }

    def _run_event_summary(self, run: dict[str, Any]) -> dict[str, Any]:
        branches = [_as_dict(item) for item in _as_list(run.get("branches")) if isinstance(item, dict)]
        evidence_ids = sorted({item for branch in branches for item in _string_list(branch.get("evidenceIds"))})
        tool_call_ids = sorted({item for branch in branches for item in _string_list(branch.get("toolCallIds"))})
        temporal_fact_ids = sorted({item for branch in branches for item in _string_list(branch.get("temporalFactIds"))})
        gate_result_ids = _unique_strings([item.get("id") for item in _as_list(run.get("gateResults")) if _as_dict(item).get("id")])
        artifact_ids = self._artifact_ids_for_tools(run, tool_call_ids)
        return {
            "title": run.get("title"),
            "branch_count": len(branches),
            "episode_count": len(_as_list(run.get("episodes"))),
            "skill_proposal_count": len(_as_list(run.get("skillProposals"))),
            "branch_ids": [branch.get("id") for branch in branches if branch.get("id")],
            "evidence_count": len(evidence_ids),
            "tool_count": len(tool_call_ids),
            "temporal_fact_count": len(temporal_fact_ids),
            "evidenceIds": evidence_ids,
            "toolCallIds": tool_call_ids,
            "temporalFactIds": temporal_fact_ids,
            "requiredPermissions": self._permissions_for_tools(run, tool_call_ids),
            "gateResultIds": gate_result_ids,
            "artifactIds": artifact_ids,
            "toolDetails": self._tool_details_for_ids(run, tool_call_ids),
            "gateDetails": self._gate_details_for_ids(run, gate_result_ids),
            "artifactDetails": self._artifact_details_for_ids(run, artifact_ids),
        }

    def _branch_event_summary(self, run: dict[str, Any], branch: dict[str, Any], *, status: str, reason: str) -> dict[str, Any]:
        quality = _as_dict(branch.get("quality"))
        tool_call_ids = _string_list(branch.get("toolCallIds"))
        gate_result_ids = _unique_strings(
            [
                *_string_list(branch.get("gateResultIds")),
                *[
                    gate_id
                    for episode in _as_list(run.get("episodes"))
                    if _as_dict(episode).get("branchId") == branch.get("id")
                    for gate_id in _string_list(_as_dict(episode).get("gateResults"))
                ],
            ]
        )
        artifact_ids = _unique_strings(
            [
                *self._artifact_ids_for_tools(run, tool_call_ids),
                *[
                    artifact_id
                    for episode in _as_list(run.get("episodes"))
                    if _as_dict(episode).get("branchId") == branch.get("id")
                    for artifact_id in _string_list(_as_dict(episode).get("artifactIds"))
                ],
            ]
        )
        return {
            "status": status,
            "reason": reason,
            "branch_title": branch.get("title") or branch.get("id"),
            "branch_type": branch.get("branchType") or branch.get("branch_type"),
            "quality_status": quality.get("status") or branch.get("status"),
            "score": branch.get("score"),
            "evidenceIds": _string_list(branch.get("evidenceIds")),
            "toolCallIds": tool_call_ids,
            "temporalFactIds": _string_list(branch.get("temporalFactIds")),
            "requiredPermissions": self._permissions_for_tools(run, tool_call_ids),
            "gateResultIds": gate_result_ids,
            "artifactIds": artifact_ids,
            "toolDetails": self._tool_details_for_ids(run, tool_call_ids),
            "gateDetails": self._gate_details_for_ids(run, gate_result_ids),
            "artifactDetails": self._artifact_details_for_ids(run, artifact_ids),
        }

    def _skill_event_summary(self, proposal: dict[str, Any]) -> dict[str, Any]:
        return {
            "skill_id": proposal.get("id"),
            "name": proposal.get("name"),
            "status": proposal.get("status"),
            "eval_score": proposal.get("evalScore"),
            "requiredPermissions": _string_list(proposal.get("requiredPermissions")),
            "evidenceRunIds": _string_list(proposal.get("evidenceRunIds")),
            "steps": _string_list(proposal.get("steps")),
        }

    def _registered_artifact_summary_text(
        self,
        content: dict[str, Any],
        selected_event: dict[str, Any],
        focused_dossier: dict[str, Any],
    ) -> str:
        counts = _as_dict(content.get("counts"))
        replay_steps = len(_as_list(content.get("replayTimeline")))
        parts = [
            selected_event.get("label") or selected_event.get("eventType"),
            focused_dossier.get("title"),
            f"{replay_steps} replay steps" if replay_steps else "",
            f"{counts.get('artifacts')} artifacts" if counts.get("artifacts") is not None else "",
        ]
        return " / ".join(str(item) for item in parts if item) or "Registered Worldline replay artifact."

    def _artifact_event_summary(self, artifact: dict[str, Any]) -> dict[str, Any]:
        content = _as_dict(artifact.get("content"))
        selected_event = _as_dict(content.get("selectedEvent"))
        focused_dossier = _as_dict(content.get("focusedDossier"))
        return {
            "status": "registered",
            "artifactIds": [artifact.get("id")],
            "artifactDetails": [
                {
                    "id": artifact.get("id"),
                    "label": artifact.get("label"),
                    "type": artifact.get("kind"),
                    "path": f"worldline-run-ledger://{artifact.get('runId')}/artifacts/{artifact.get('id')}",
                    "summary": artifact.get("summary"),
                    "eventId": artifact.get("eventId") or "",
                    "format": artifact.get("format") or "",
                }
            ],
            "eventId": artifact.get("eventId") or "",
            "format": artifact.get("format") or "",
            "kind": artifact.get("kind") or "",
            "replay_step_count": len(_as_list(content.get("replayTimeline"))),
            "selected_event_type": selected_event.get("eventType") or "",
            "focused_dossier_title": focused_dossier.get("title") or "",
        }

    def _tool_trace_by_id(self, run: dict[str, Any], tool_id: str) -> dict[str, Any] | None:
        for trace in _as_list(run.get("toolTraces")):
            trace_dict = _as_dict(trace)
            if trace_dict.get("id") == tool_id:
                return trace_dict
        return None

    def _gate_result_by_id(self, run: dict[str, Any], gate_id: str) -> dict[str, Any] | None:
        for gate in _as_list(run.get("gateResults")):
            gate_dict = _as_dict(gate)
            if gate_dict.get("id") == gate_id:
                return gate_dict
        return None

    def _permissions_for_tools(self, run: dict[str, Any], tool_ids: list[str]) -> list[str]:
        return _unique_strings(
            [
                trace.get("permission")
                for tool_id in tool_ids
                if (trace := self._tool_trace_by_id(run, tool_id))
            ]
        )

    def _artifact_ids_for_tools(self, run: dict[str, Any], tool_ids: list[str]) -> list[str]:
        return _unique_strings(
            [
                artifact_id
                for tool_id in tool_ids
                if (trace := self._tool_trace_by_id(run, tool_id))
                for artifact_id in _string_list(trace.get("artifactIds"))
            ]
        )

    def _tool_details_for_ids(self, run: dict[str, Any], tool_ids: list[str]) -> list[dict[str, Any]]:
        details: list[dict[str, Any]] = []
        for tool_id in tool_ids:
            trace = self._tool_trace_by_id(run, tool_id)
            if not trace:
                continue
            details.append(
                {
                    "id": trace.get("id"),
                    "branchId": trace.get("branchId"),
                    "name": trace.get("name"),
                    "status": trace.get("status"),
                    "permission": trace.get("permission"),
                    "summary": trace.get("summary"),
                    "result": trace.get("result"),
                    "artifactIds": _string_list(trace.get("artifactIds")),
                    "failureReason": trace.get("failureReason") or "",
                }
            )
        return details

    def _gate_details_for_ids(self, run: dict[str, Any], gate_ids: list[str]) -> list[dict[str, Any]]:
        details: list[dict[str, Any]] = []
        for gate_id in gate_ids:
            gate = self._gate_result_by_id(run, gate_id)
            if not gate:
                continue
            details.append(
                {
                    "id": gate.get("id"),
                    "label": gate.get("label"),
                    "status": gate.get("status"),
                    "value": gate.get("value"),
                    "summary": gate.get("summary"),
                    "branchId": gate.get("branchId") or "",
                }
            )
        return details

    def _artifact_details_for_ids(self, run: dict[str, Any], artifact_ids: list[str]) -> list[dict[str, Any]]:
        details: list[dict[str, Any]] = []
        for artifact in _as_list(run.get("artifacts")):
            artifact_dict = _as_dict(artifact)
            if artifact_dict.get("id") not in artifact_ids:
                continue
            details.append(
                {
                    "id": artifact_dict.get("id"),
                    "label": artifact_dict.get("label"),
                    "type": artifact_dict.get("kind") or artifact_dict.get("type"),
                    "path": f"worldline-run-ledger://{artifact_dict.get('runId')}/artifacts/{artifact_dict.get('id')}",
                    "summary": artifact_dict.get("summary"),
                    "eventId": artifact_dict.get("eventId") or "",
                    "format": artifact_dict.get("format") or "",
                }
            )
        for trace in _as_list(run.get("toolTraces")):
            trace_dict = _as_dict(trace)
            for artifact in _as_list(trace_dict.get("artifacts")):
                artifact_dict = _as_dict(artifact)
                if artifact_dict.get("id") not in artifact_ids:
                    continue
                details.append(
                    {
                        "id": artifact_dict.get("id"),
                        "label": artifact_dict.get("label"),
                        "type": artifact_dict.get("type"),
                        "path": artifact_dict.get("path"),
                        "summary": artifact_dict.get("summary"),
                        "toolCallId": trace_dict.get("id"),
                    }
                )
        return details

    def _artifacts_for_run(
        self,
        ledger: dict[str, Any],
        run_id: str,
        run: dict[str, Any],
    ) -> list[dict[str, Any]]:
        by_run = _as_dict(ledger.get("artifacts"))
        artifacts = _as_list(by_run.get(run_id))
        if artifacts:
            return [_as_dict(item) for item in artifacts if isinstance(item, dict)]
        return [_as_dict(item) for item in _as_list(run.get("artifacts")) if isinstance(item, dict)]

    def _event(
        self,
        run_id: str,
        *,
        event_type: str,
        actor: str,
        branch_id: str | None = None,
        summary: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        now = _now_iso()
        return {
            "id": f"evt_{uuid.uuid4().hex[:16]}",
            "runId": run_id,
            "branchId": branch_id or "",
            "eventType": event_type,
            "actor": actor,
            "summary": summary or {},
            "createdAt": now,
            "protocolVersion": self.PROTOCOL_VERSION,
        }

    async def _load_ledger(self) -> dict[str, Any]:
        if not self.storage_path.exists():
            return {"runs": {}, "events": {}, "artifacts": {}}

        async with aiofiles.open(self.storage_path, encoding="utf-8") as file:
            content = await file.read()

        try:
            data = json.loads(content or "{}")
        except json.JSONDecodeError:
            return {"runs": {}, "events": {}, "artifacts": {}}

        runs = data.get("runs") if isinstance(data.get("runs"), dict) else {}
        events = data.get("events") if isinstance(data.get("events"), dict) else {}
        artifacts = data.get("artifacts") if isinstance(data.get("artifacts"), dict) else {}
        for run_id, run in runs.items():
            run_artifacts = _as_list(_as_dict(run).get("artifacts"))
            if run_artifacts and run_id not in artifacts:
                artifacts[run_id] = run_artifacts
        return {"runs": runs, "events": events, "artifacts": artifacts}

    async def _save_ledger(self, ledger: dict[str, Any]) -> None:
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "protocolVersion": self.PROTOCOL_VERSION,
            "runs": ledger.get("runs") or {},
            "events": ledger.get("events") or {},
            "artifacts": ledger.get("artifacts") or {},
            "updatedAt": _now_iso(),
        }
        async with aiofiles.open(self.storage_path, "w", encoding="utf-8") as file:
            await file.write(json.dumps(payload, ensure_ascii=False, indent=2))
