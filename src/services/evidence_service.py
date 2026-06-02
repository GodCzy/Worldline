from __future__ import annotations

from typing import Any

from src.repositories.knowledge_object_repository import KnowledgeObjectRepository


class EvidenceQueryService:
    """Build evidence-aware retrieval responses for Phase 3."""

    def __init__(self, repository: KnowledgeObjectRepository | None = None) -> None:
        self.repository = repository or KnowledgeObjectRepository()

    async def query_with_evidence(self, db_id: str, query: str, meta: dict[str, Any] | None = None) -> dict[str, Any]:
        from src import knowledge_base

        query_meta = dict(meta or {})
        query_meta.setdefault("search_mode", "hybrid")
        query_meta["include_evidence"] = True

        raw_result = await knowledge_base.aquery(query, db_id=db_id, **query_meta)
        retrieved_chunks = self._extract_retrieved_chunks(raw_result)
        retrieved_chunks = await self.repository.decorate_retrieval_results(db_id, retrieved_chunks)

        citations = self._collect_citations(retrieved_chunks)
        claims = self._build_claims(retrieved_chunks)
        answer = self._build_extractive_answer(retrieved_chunks)
        route_trace = self._build_route_trace(query_meta, retrieved_chunks, citations)

        return {
            "answer": answer,
            "claims": claims,
            "citations": citations,
            "route_trace": route_trace,
            "retrieved_chunks": self._serialize_retrieved_chunks(retrieved_chunks),
            "status": "success",
        }

    def _extract_retrieved_chunks(self, raw_result: Any) -> list[dict[str, Any]]:
        if isinstance(raw_result, list):
            return [item for item in raw_result if isinstance(item, dict)]
        if not isinstance(raw_result, dict):
            return []

        if isinstance(raw_result.get("result"), list):
            return [item for item in raw_result["result"] if isinstance(item, dict)]
        if isinstance(raw_result.get("chunks"), list):
            return [item for item in raw_result["chunks"] if isinstance(item, dict)]

        data = raw_result.get("data")
        if isinstance(data, dict) and isinstance(data.get("chunks"), list):
            return [item for item in data["chunks"] if isinstance(item, dict)]

        return []

    def _collect_citations(self, chunks: list[dict[str, Any]]) -> list[dict[str, Any]]:
        citations_by_id: dict[str, dict[str, Any]] = {}
        for chunk in chunks:
            for citation in chunk.get("citations") or []:
                evidence_id = citation.get("evidence_id")
                if evidence_id and evidence_id not in citations_by_id:
                    citations_by_id[evidence_id] = citation
        return list(citations_by_id.values())

    def _build_claims(self, chunks: list[dict[str, Any]]) -> list[dict[str, Any]]:
        claims: list[dict[str, Any]] = []
        for chunk in chunks:
            evidence_ids = list(chunk.get("metadata", {}).get("evidence_ids") or [])
            if not evidence_ids:
                continue
            text = self._first_sentence(str(chunk.get("content") or ""))
            if not text:
                continue
            score = chunk.get("rerank_score", chunk.get("score", chunk.get("keyword_score", 0.0)))
            claims.append(
                {
                    "claim": self._trim(text, 360),
                    "confidence": self._normalize_confidence(score),
                    "evidence_ids": evidence_ids,
                }
            )
        return claims

    def _build_extractive_answer(self, chunks: list[dict[str, Any]]) -> str:
        snippets = []
        for chunk in chunks[:3]:
            text = self._trim(str(chunk.get("content") or "").strip(), 320)
            if text:
                snippets.append(text)
        return "\n\n".join(snippets)

    def _build_route_trace(
        self,
        meta: dict[str, Any],
        chunks: list[dict[str, Any]],
        citations: list[dict[str, Any]],
    ) -> dict[str, Any]:
        search_mode = str(meta.get("search_mode") or "vector").lower()
        if search_mode not in {"vector", "keyword", "hybrid"}:
            search_mode = "vector"

        channels = []
        if search_mode in {"vector", "hybrid"}:
            channels.append("dense")
        if search_mode in {"keyword", "hybrid"}:
            channels.append("sparse_keyword")

        return {
            "dense": search_mode in {"vector", "hybrid"},
            "sparse": search_mode in {"keyword", "hybrid"},
            "bm25": search_mode in {"keyword", "hybrid"},
            "channels": channels,
            "sparse_strategy": "keyword_bm25_proxy" if search_mode in {"keyword", "hybrid"} else None,
            "graph": False,
            "timeline": False,
            "reranker": bool(meta.get("use_reranker")),
            "embedding_model": meta.get("embedding_model") or meta.get("embedding_model_id"),
            "reranker_model": meta.get("reranker_model"),
            "search_mode": search_mode,
            "recall_top_k": meta.get("recall_top_k"),
            "final_top_k": meta.get("final_top_k"),
            "retrieved_count": len(chunks),
            "citation_count": len(citations),
            "evidence_enriched": bool(citations),
        }

    def _serialize_retrieved_chunks(self, chunks: list[dict[str, Any]]) -> list[dict[str, Any]]:
        serialized: list[dict[str, Any]] = []
        for chunk in chunks:
            item = dict(chunk)
            item["content"] = self._trim(str(item.get("content") or ""), 1000)
            serialized.append(item)
        return serialized

    def _first_sentence(self, value: str) -> str:
        text = " ".join((value or "").split())
        if not text:
            return ""
        for delimiter in ("。", ".", "\n"):
            if delimiter in text:
                return text.split(delimiter, 1)[0].strip() + delimiter
        return text

    def _normalize_confidence(self, score: Any) -> float:
        try:
            value = float(score)
        except (TypeError, ValueError):
            return 0.0
        return max(0.0, min(value, 1.0))

    def _trim(self, value: str | None, limit: int) -> str:
        text = value or ""
        if len(text) <= limit:
            return text
        return f"{text[:limit].rstrip()}..."
