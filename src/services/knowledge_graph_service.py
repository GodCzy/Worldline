from __future__ import annotations

import re
from collections import Counter, defaultdict
from datetime import datetime
from itertools import combinations
from typing import Any

from src.repositories.knowledge_graph_repository import KnowledgeGraphRepository
from src.utils import hashstr


class KnowledgeGraphService:
    """Deterministic graph, temporal, and stale-page layer for Worldline."""

    STOPWORDS = {
        "and",
        "are",
        "for",
        "from",
        "the",
        "with",
        "this",
        "that",
        "into",
        "worldline",
        "phase",
        "chunk",
        "chunks",
        "evidence",
        "metadata",
        "pages",
        "page",
        "topic",
        "topics",
    }

    DATE_RE = re.compile(r"\b(19\d{2}|20\d{2})(?:[-/](0?[1-9]|1[0-2])(?:[-/](0?[1-9]|[12]\d|3[01]))?)?\b")

    def __init__(self, repository: KnowledgeGraphRepository | None = None) -> None:
        self.repository = repository or KnowledgeGraphRepository()

    async def rebuild_graph(self, db_id: str, *, max_entities: int = 40) -> dict[str, Any]:
        source_chunks = await self.repository.list_source_chunks(db_id)
        max_entities = max(1, min(int(max_entities or 40), 200))

        await self.repository.replace_graph(db_id)
        if not source_chunks:
            return {
                "db_id": db_id,
                "status": "empty",
                "counts": {"entities": 0, "relationships": 0, "temporal_facts": 0},
            }

        entities = self._extract_entities(db_id, source_chunks, max_entities=max_entities)
        entity_by_name = {entity["name"].lower(): entity for entity in entities}
        relationships = self._extract_relationships(db_id, source_chunks, entity_by_name)
        temporal_facts = self._extract_temporal_facts(db_id, source_chunks, entity_by_name)

        await self.repository.insert_entities(entities)
        await self.repository.insert_relationships(relationships)
        await self.repository.insert_temporal_facts(temporal_facts)

        return {
            "db_id": db_id,
            "status": "success",
            "counts": {
                "entities": len(entities),
                "relationships": len(relationships),
                "temporal_facts": len(temporal_facts),
            },
            "evidence_bound": {
                "entities": sum(1 for entity in entities if entity["evidence_ids"]),
                "relationships": sum(1 for rel in relationships if rel["evidence_ids"]),
                "temporal_facts": sum(1 for fact in temporal_facts if fact["evidence_ids"]),
            },
        }

    async def list_entities(self, db_id: str, *, limit: int = 100, offset: int = 0) -> dict[str, Any]:
        return await self.repository.list_entities(db_id, limit=limit, offset=offset)

    async def list_relationships(self, db_id: str, *, limit: int = 100, offset: int = 0) -> dict[str, Any]:
        return await self.repository.list_relationships(db_id, limit=limit, offset=offset)

    async def list_timeline(self, db_id: str, *, limit: int = 100, offset: int = 0) -> dict[str, Any]:
        return await self.repository.list_timeline(db_id, limit=limit, offset=offset)

    async def detect_stale_pages(self, db_id: str) -> dict[str, Any]:
        pages = await self.repository.list_wiki_pages(db_id)
        chunks = await self.repository.list_source_chunks(db_id)
        chunks_by_file: dict[str, list[dict[str, Any]]] = defaultdict(list)
        for chunk in chunks:
            chunks_by_file[chunk["file_id"]].append(chunk)

        stale_pages = []
        fresh_pages = 0
        for page in pages:
            relevant_chunks = chunks_by_file.get(page.source_id, []) if page.page_type == "document" else chunks
            current_chunk_ids = sorted(chunk["chunk_id"] for chunk in relevant_chunks)
            current_doc_versions = sorted({chunk["doc_version_id"] for chunk in relevant_chunks})

            freshness = page.freshness or {}
            previous_chunk_ids = sorted(freshness.get("source_chunk_ids") or [])
            previous_doc_versions = sorted(freshness.get("source_doc_version_ids") or [])
            reasons = []

            if freshness.get("status") != "fresh":
                reasons.append("freshness_status_not_fresh")
            if previous_chunk_ids != current_chunk_ids:
                reasons.append("source_chunk_ids_changed")
            if previous_doc_versions != current_doc_versions:
                reasons.append("source_doc_version_ids_changed")

            payload = {
                "page_id": page.page_id,
                "page_type": page.page_type,
                "title": page.title,
                "source_id": page.source_id,
                "status": "stale" if reasons else "fresh",
                "stale_reasons": reasons,
                "freshness": freshness,
                "current": {
                    "source_chunk_ids": current_chunk_ids,
                    "source_doc_version_ids": current_doc_versions,
                    "source_chunk_count": len(current_chunk_ids),
                },
            }
            if reasons:
                stale_pages.append(payload)
            else:
                fresh_pages += 1

        return {
            "db_id": db_id,
            "total_pages": len(pages),
            "fresh_pages": fresh_pages,
            "stale_pages": stale_pages,
            "stale_count": len(stale_pages),
        }

    def _extract_entities(
        self,
        db_id: str,
        source_chunks: list[dict[str, Any]],
        *,
        max_entities: int,
    ) -> list[dict[str, Any]]:
        counter: Counter[str] = Counter()
        chunk_hits: dict[str, list[dict[str, Any]]] = defaultdict(list)
        for chunk in source_chunks:
            seen_in_chunk = set()
            for token in self._tokens(chunk["text"]):
                normalized = token.lower()
                counter[normalized] += 1
                if normalized not in seen_in_chunk:
                    chunk_hits[normalized].append(chunk)
                    seen_in_chunk.add(normalized)

        selected = [name for name, _count in counter.most_common(max_entities)]
        entities = []
        for name in selected:
            chunks = chunk_hits[name]
            display_name = self._display_name(name, chunks)
            entity_id = self._entity_id(db_id, display_name)
            entities.append(
                {
                    "entity_id": entity_id,
                    "db_id": db_id,
                    "name": display_name,
                    "entity_type": self._entity_type(display_name),
                    "aliases": sorted({display_name, name}),
                    "evidence_ids": self._collect_evidence_ids(chunks),
                    "source_chunk_ids": [chunk["chunk_id"] for chunk in chunks[:50]],
                    "status": "active",
                    "entity_metadata": {
                        "mention_count": counter[name],
                        "file_ids": sorted({chunk["file_id"] for chunk in chunks}),
                    },
                }
            )
        return entities

    def _extract_relationships(
        self,
        db_id: str,
        source_chunks: list[dict[str, Any]],
        entity_by_name: dict[str, dict[str, Any]],
    ) -> list[dict[str, Any]]:
        pair_chunks: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
        entity_names = set(entity_by_name.keys())

        for chunk in source_chunks:
            present = sorted({token.lower() for token in self._tokens(chunk["text"]) if token.lower() in entity_names})
            for left, right in combinations(present[:8], 2):
                pair_chunks[(left, right)].append(chunk)

        relationships = []
        for (left, right), chunks in sorted(pair_chunks.items()):
            left_entity = entity_by_name[left]
            right_entity = entity_by_name[right]
            relationships.append(
                {
                    "relationship_id": self._relationship_id(
                        db_id,
                        left_entity["entity_id"],
                        right_entity["entity_id"],
                        "co_mentions",
                    ),
                    "db_id": db_id,
                    "source_entity_id": left_entity["entity_id"],
                    "target_entity_id": right_entity["entity_id"],
                    "relation_type": "co_mentions",
                    "weight": float(len(chunks)),
                    "evidence_ids": self._collect_evidence_ids(chunks),
                    "source_chunk_ids": [chunk["chunk_id"] for chunk in chunks[:50]],
                    "status": "active",
                    "relationship_metadata": {
                        "source_name": left_entity["name"],
                        "target_name": right_entity["name"],
                        "co_mention_count": len(chunks),
                    },
                }
            )
        return relationships

    def _extract_temporal_facts(
        self,
        db_id: str,
        source_chunks: list[dict[str, Any]],
        entity_by_name: dict[str, dict[str, Any]],
    ) -> list[dict[str, Any]]:
        facts = []
        for chunk in source_chunks:
            text = chunk["text"]
            present_entities = [token.lower() for token in self._tokens(text) if token.lower() in entity_by_name]
            subject_entity = entity_by_name[present_entities[0]] if present_entities else None
            subject = subject_entity["name"] if subject_entity else chunk.get("filename") or chunk["file_id"]
            for match in self.DATE_RE.finditer(text):
                occurred_at = self._parse_date_match(match)
                object_text = self._trim(self._first_sentence(text), 280)
                facts.append(
                    {
                        "fact_id": self._temporal_fact_id(db_id, subject, occurred_at.isoformat(), chunk["chunk_id"]),
                        "db_id": db_id,
                        "subject": subject,
                        "predicate": "mentioned_on",
                        "object": object_text,
                        "occurred_at": occurred_at,
                        "source_entity_id": subject_entity["entity_id"] if subject_entity else None,
                        "evidence_ids": list(chunk.get("evidence_ids") or []),
                        "source_chunk_ids": [chunk["chunk_id"]],
                        "confidence": 1.0,
                        "fact_metadata": {
                            "file_id": chunk["file_id"],
                            "filename": chunk.get("filename"),
                            "matched_text": match.group(0),
                        },
                    }
                )
        return facts

    def _tokens(self, text: str) -> list[str]:
        raw_tokens = re.findall(r"[A-Za-z][A-Za-z0-9_-]{2,}|[\u4e00-\u9fff]{2,8}", text or "")
        tokens = []
        for token in raw_tokens:
            normalized = token.strip().lower()
            if normalized in self.STOPWORDS:
                continue
            if len(normalized) < 3 and not re.search(r"[\u4e00-\u9fff]", normalized):
                continue
            tokens.append(token.strip())
        return tokens

    def _collect_evidence_ids(self, chunks: list[dict[str, Any]]) -> list[str]:
        evidence_ids: list[str] = []
        for chunk in chunks:
            for evidence_id in chunk.get("evidence_ids") or []:
                if evidence_id not in evidence_ids:
                    evidence_ids.append(evidence_id)
        return evidence_ids

    def _display_name(self, normalized: str, chunks: list[dict[str, Any]]) -> str:
        for chunk in chunks:
            for token in self._tokens(chunk["text"]):
                if token.lower() == normalized:
                    return token
        return normalized

    def _entity_type(self, name: str) -> str:
        if re.fullmatch(r"[A-Z][A-Za-z0-9_-]+", name):
            return "proper_noun"
        if re.search(r"[\u4e00-\u9fff]", name):
            return "concept"
        return "concept"

    def _parse_date_match(self, match: re.Match[str]) -> datetime:
        year = int(match.group(1))
        month = int(match.group(2) or 1)
        day = int(match.group(3) or 1)
        return datetime(year, month, day)

    def _first_sentence(self, value: str) -> str:
        text = " ".join((value or "").split())
        if not text:
            return ""
        for delimiter in ("\u3002", ".", "\n"):
            if delimiter in text:
                return text.split(delimiter, 1)[0].strip() + delimiter
        return text

    def _trim(self, value: str | None, limit: int) -> str:
        text = value or ""
        if len(text) <= limit:
            return text
        return f"{text[:limit].rstrip()}..."

    def _entity_id(self, db_id: str, name: str) -> str:
        return f"ent_{hashstr(f'{db_id}:entity:{name.lower()}', length=32)}"

    def _relationship_id(self, db_id: str, source_id: str, target_id: str, relation_type: str) -> str:
        return f"rel_{hashstr(f'{db_id}:relationship:{source_id}:{target_id}:{relation_type}', length=32)}"

    def _temporal_fact_id(self, db_id: str, subject: str, occurred_at: str, chunk_id: str) -> str:
        return f"tf_{hashstr(f'{db_id}:temporal:{subject}:{occurred_at}:{chunk_id}', length=32)}"
