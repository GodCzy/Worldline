from __future__ import annotations

import re
from collections import Counter, defaultdict
from typing import Any

from src.repositories.wiki_repository import WikiRepository


class AutoWikiService:
    """Deterministic Auto-Wiki generator backed by evidence-bound chunks."""

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
    }

    def __init__(self, repository: WikiRepository | None = None) -> None:
        self.repository = repository or WikiRepository()

    async def rebuild_wiki(
        self,
        db_id: str,
        *,
        file_id: str | None = None,
        max_topics: int = 8,
    ) -> dict[str, Any]:
        source_chunks = await self.repository.list_source_chunks(db_id, file_id=file_id)
        max_topics = max(1, min(int(max_topics or 8), 20))

        if file_id:
            await self.repository.replace_pages_for_scope(db_id, file_id=file_id, page_types=["document"])
        else:
            await self.repository.replace_pages_for_scope(db_id)

        if not source_chunks:
            return {
                "db_id": db_id,
                "scope": "file" if file_id else "database",
                "file_id": file_id,
                "pages": [],
                "page_counts": {},
                "status": "empty",
            }

        pages = self._build_document_pages(db_id, source_chunks)
        if not file_id:
            topics = self._extract_topics(source_chunks, max_topics=max_topics)
            topic_pages = self._build_topic_pages(db_id, source_chunks, topics)
            glossary_page = self._build_glossary_page(db_id, source_chunks, topics)
            home_page = self._build_home_page(db_id, source_chunks, pages, topic_pages, glossary_page)
            pages = [home_page, *pages, *topic_pages, glossary_page]
            pages = self._attach_backlinks(pages)

        await self.repository.upsert_pages(db_id, pages)
        counts = Counter(page["page_type"] for page in pages)

        return {
            "db_id": db_id,
            "scope": "file" if file_id else "database",
            "file_id": file_id,
            "pages": [
                {
                    "page_id": page["page_id"],
                    "page_type": page["page_type"],
                    "title": page["title"],
                    "slug": page["slug"],
                    "source_id": page.get("source_id"),
                    "evidence_ids": page.get("evidence_ids") or [],
                    "freshness": page.get("freshness") or {},
                }
                for page in pages
            ],
            "page_counts": dict(counts),
            "status": "success",
        }

    def _build_document_pages(self, db_id: str, source_chunks: list[dict[str, Any]]) -> list[dict[str, Any]]:
        grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
        for chunk in source_chunks:
            grouped[chunk["file_id"]].append(chunk)

        pages: list[dict[str, Any]] = []
        for file_id, chunks in grouped.items():
            chunks.sort(key=lambda item: item["chunk_index"])
            filename = chunks[0].get("filename") or file_id
            slug = self._slug(f"document-{file_id}")
            page_id = self.repository.make_page_id(db_id, "document", file_id, slug)
            evidence_ids = self._collect_evidence_ids(chunks)
            intelligence = self._page_intelligence("document", filename, chunks, evidence_ids)
            markdown = self._document_markdown(filename, chunks, evidence_ids, intelligence)
            pages.append(
                {
                    "page_id": page_id,
                    "page_type": "document",
                    "slug": slug,
                    "title": filename,
                    "source_id": file_id,
                    "markdown": markdown,
                    "evidence_ids": evidence_ids,
                    "freshness": self._freshness(chunks),
                    "metadata": {
                        "source_chunk_count": len(chunks),
                        "doc_version_ids": sorted({chunk["doc_version_id"] for chunk in chunks}),
                        **intelligence,
                    },
                    "backlinks": [],
                }
            )
        return pages

    def _build_topic_pages(
        self,
        db_id: str,
        source_chunks: list[dict[str, Any]],
        topics: list[str],
    ) -> list[dict[str, Any]]:
        pages: list[dict[str, Any]] = []
        for topic in topics:
            related = [chunk for chunk in source_chunks if topic.lower() in chunk["text"].lower()]
            if not related:
                continue
            slug = self._slug(f"topic-{topic}")
            page_id = self.repository.make_page_id(db_id, "topic", topic, slug)
            evidence_ids = self._collect_evidence_ids(related)
            intelligence = self._page_intelligence("topic", topic, related, evidence_ids)
            pages.append(
                {
                    "page_id": page_id,
                    "page_type": "topic",
                    "slug": slug,
                    "title": topic,
                    "source_id": topic,
                    "markdown": self._topic_markdown(topic, related, evidence_ids, intelligence),
                    "evidence_ids": evidence_ids,
                    "freshness": self._freshness(related),
                    "metadata": {
                        "related_file_ids": sorted({chunk["file_id"] for chunk in related}),
                        "source_chunk_count": len(related),
                        **intelligence,
                    },
                    "backlinks": [],
                }
            )
        return pages

    def _build_glossary_page(
        self,
        db_id: str,
        source_chunks: list[dict[str, Any]],
        topics: list[str],
    ) -> dict[str, Any]:
        slug = "glossary"
        page_id = self.repository.make_page_id(db_id, "glossary", None, slug)
        definitions = []
        for topic in topics:
            chunk = next((item for item in source_chunks if topic.lower() in item["text"].lower()), None)
            if chunk:
                definitions.append((topic, self._first_sentence(chunk["text"])))

        evidence_ids = self._collect_evidence_ids(source_chunks)
        intelligence = self._page_intelligence("glossary", "Glossary", source_chunks, evidence_ids, topics=topics)
        lines = ["# Glossary", ""]
        if definitions:
            for topic, definition in definitions:
                lines.append(f"- **{topic}**: {definition}")
        else:
            lines.append("No glossary terms were generated from the current evidence-bound chunks.")

        return {
            "page_id": page_id,
            "page_type": "glossary",
            "slug": slug,
            "title": "Glossary",
            "source_id": None,
            "markdown": "\n".join(lines),
            "evidence_ids": evidence_ids[:50],
            "freshness": self._freshness(source_chunks),
            "metadata": {"term_count": len(definitions), **intelligence},
            "backlinks": [],
        }

    def _build_home_page(
        self,
        db_id: str,
        source_chunks: list[dict[str, Any]],
        document_pages: list[dict[str, Any]],
        topic_pages: list[dict[str, Any]],
        glossary_page: dict[str, Any],
    ) -> dict[str, Any]:
        slug = "home"
        page_id = self.repository.make_page_id(db_id, "home", None, slug)
        evidence_ids = self._collect_evidence_ids(source_chunks)
        intelligence = self._page_intelligence("home", "Auto-Wiki Home", source_chunks, evidence_ids)
        lines = [
            "# Auto-Wiki Home",
            "",
            "## Documents",
            "",
        ]
        for page in document_pages:
            lines.append(f"- [{page['title']}](wiki:{page['page_id']})")
        lines.extend(["", "## Topics", ""])
        for page in topic_pages:
            lines.append(f"- [{page['title']}](wiki:{page['page_id']})")
        lines.extend(["", "## Glossary", "", f"- [Glossary](wiki:{glossary_page['page_id']})"])

        return {
            "page_id": page_id,
            "page_type": "home",
            "slug": slug,
            "title": "Auto-Wiki Home",
            "source_id": None,
            "markdown": "\n".join(lines),
            "evidence_ids": evidence_ids[:50],
            "freshness": self._freshness(source_chunks),
            "metadata": {
                "document_count": len(document_pages),
                "topic_count": len(topic_pages),
                "glossary_page_id": glossary_page["page_id"],
                **intelligence,
            },
            "backlinks": [],
        }

    def _attach_backlinks(self, pages: list[dict[str, Any]]) -> list[dict[str, Any]]:
        page_refs = {
            page["page_id"]: {
                "page_id": page["page_id"],
                "title": page["title"],
                "page_type": page["page_type"],
                "slug": page["slug"],
            }
            for page in pages
        }
        home = next((page for page in pages if page["page_type"] == "home"), None)
        glossary = next((page for page in pages if page["page_type"] == "glossary"), None)
        topics = [page for page in pages if page["page_type"] == "topic"]

        for page in pages:
            backlinks = []
            if home and page["page_id"] != home["page_id"]:
                backlinks.append(page_refs[home["page_id"]])
            if page["page_type"] == "document":
                backlinks.extend(page_refs[topic["page_id"]] for topic in topics if self._page_mentions(page, topic))
                if glossary:
                    backlinks.append(page_refs[glossary["page_id"]])
            if page["page_type"] == "topic":
                backlinks.extend(
                    page_refs[doc["page_id"]]
                    for doc in pages
                    if doc["page_type"] == "document" and self._page_mentions(doc, page)
                )
            page["backlinks"] = self._unique_backlinks(backlinks)
        return pages

    def _page_mentions(self, source: dict[str, Any], target: dict[str, Any]) -> bool:
        return target["title"].lower() in source["markdown"].lower()

    def _document_markdown(
        self,
        filename: str,
        chunks: list[dict[str, Any]],
        evidence_ids: list[str],
        intelligence: dict[str, Any],
    ) -> str:
        lines = [
            f"# {filename}",
            "",
            "## STORM Outline",
            "",
        ]
        for section in intelligence["outline"]["sections"]:
            lines.append(f"- **{section['title']}**: {section['purpose']}")
        lines.extend(
            [
                "",
                "## Summary",
                "",
            ]
        )
        for chunk in chunks[:5]:
            lines.append(f"- {self._trim(self._first_sentence(chunk['text']), 220)}")
        lines.extend(
            [
                "",
                "## Claims",
                "",
            ]
        )
        for claim in intelligence["claims"][:8]:
            lines.append(f"- {claim['claim']} {self._citation_suffix(claim.get('evidence_ids') or [])}")
        lines.extend(
            [
                "",
                "## Open Questions",
                "",
            ]
        )
        for question in intelligence["open_questions"]:
            lines.append(f"- {question['question']}")
        lines.extend(
            [
                "",
                "## Evidence",
                "",
            ]
        )
        for evidence_id in evidence_ids[:20]:
            lines.append(f"- `{evidence_id}`")
        return "\n".join(lines)

    def _topic_markdown(
        self,
        topic: str,
        chunks: list[dict[str, Any]],
        evidence_ids: list[str],
        intelligence: dict[str, Any],
    ) -> str:
        lines = [
            f"# {topic}",
            "",
            "## STORM Outline",
            "",
        ]
        for section in intelligence["outline"]["sections"]:
            lines.append(f"- **{section['title']}**: {section['purpose']}")
        lines.extend(
            [
                "",
                "## Evidence-backed notes",
                "",
            ]
        )
        for chunk in chunks[:8]:
            lines.append(f"- {self._trim(self._first_sentence(chunk['text']), 260)}")
        lines.extend(["", "## Citations", ""])
        for citation in intelligence["citations"][:20]:
            lines.append(f"- `{citation['evidence_id']}` from `{citation['chunk_id']}`")
        return "\n".join(lines)

    def _page_intelligence(
        self,
        page_type: str,
        title: str,
        chunks: list[dict[str, Any]],
        evidence_ids: list[str],
        *,
        topics: list[str] | None = None,
    ) -> dict[str, Any]:
        claims = self._claims(chunks)
        citations = self._citations(chunks)
        return {
            "outline": self._storm_outline(page_type, title, chunks, evidence_ids, topics=topics),
            "sections": self._wiki_sections(page_type, chunks, evidence_ids),
            "claims": claims,
            "citations": citations,
            "disputes": self._disputes(chunks),
            "open_questions": self._open_questions(page_type, title, chunks),
            "review": self._review_state(),
            "evidence_coverage": self._evidence_coverage(claims, citations, evidence_ids),
            "rag_role": {
                "primary": False,
                "role": "evidence_candidate_recall",
                "candidate_chunk_ids": [chunk["chunk_id"] for chunk in chunks[:20]],
            },
            "generation_strategy": {
                "style": "storm-lite",
                "external_model_calls": 0,
                "deterministic": True,
            },
        }

    def _storm_outline(
        self,
        page_type: str,
        title: str,
        chunks: list[dict[str, Any]],
        evidence_ids: list[str],
        *,
        topics: list[str] | None = None,
    ) -> dict[str, Any]:
        return {
            "style": "storm-lite",
            "title": title,
            "page_type": page_type,
            "perspectives": [
                {"id": "source", "label": "Source Summary", "role": "summarize evidence-bound sources"},
                {"id": "claims", "label": "Supported Claims", "role": "separate claims from citations"},
                {"id": "review", "label": "Review Queue", "role": "surface disputes and open questions"},
            ],
            "sections": [
                {
                    "id": "summary",
                    "title": "Multi-perspective Summary",
                    "purpose": "建立读者对来源、主题和上下文的第一层理解。",
                    "evidence_ids": evidence_ids[:8],
                },
                {
                    "id": "claims",
                    "title": "Evidence-backed Claims",
                    "purpose": "只列出能回连 EvidenceAnchor 的主张。",
                    "evidence_ids": evidence_ids[:20],
                },
                {
                    "id": "questions",
                    "title": "Disputes And Open Questions",
                    "purpose": "暴露未确认、可能冲突或需要人工审核的点。",
                    "evidence_ids": evidence_ids[:20],
                },
            ],
            "topic_candidates": topics or self._extract_topics(chunks, max_topics=5),
        }

    def _wiki_sections(
        self,
        page_type: str,
        chunks: list[dict[str, Any]],
        evidence_ids: list[str],
    ) -> list[dict[str, Any]]:
        return [
            {
                "id": f"{page_type}-summary",
                "title": "Summary",
                "claim_count": min(len(chunks), 5),
                "evidence_ids": evidence_ids[:10],
                "status": "supported" if evidence_ids else "needs_evidence",
            },
            {
                "id": f"{page_type}-citations",
                "title": "Citations",
                "claim_count": len(evidence_ids),
                "evidence_ids": evidence_ids[:20],
                "status": "supported" if evidence_ids else "needs_evidence",
            },
        ]

    def _claims(self, chunks: list[dict[str, Any]]) -> list[dict[str, Any]]:
        claims = []
        for chunk in chunks[:12]:
            evidence_ids = list(chunk.get("evidence_ids") or [])
            claims.append(
                {
                    "claim": self._trim(self._first_sentence(chunk["text"]), 260),
                    "status": "supported" if evidence_ids else "needs_evidence",
                    "evidence_ids": evidence_ids[:8],
                    "source_chunk_id": chunk["chunk_id"],
                    "doc_version_id": chunk["doc_version_id"],
                }
            )
        return claims

    def _citations(self, chunks: list[dict[str, Any]]) -> list[dict[str, Any]]:
        citations: list[dict[str, Any]] = []
        seen = set()
        for chunk in chunks:
            for evidence_id in chunk.get("evidence_ids") or []:
                if evidence_id in seen:
                    continue
                seen.add(evidence_id)
                citations.append(
                    {
                        "evidence_id": evidence_id,
                        "chunk_id": chunk["chunk_id"],
                        "file_id": chunk["file_id"],
                        "doc_version_id": chunk["doc_version_id"],
                        "source": "EvidenceAnchor",
                    }
                )
        return citations

    def _disputes(self, chunks: list[dict[str, Any]]) -> list[dict[str, Any]]:
        dispute_markers = ("conflict", "dispute", "contradict", "风险", "冲突", "争议")
        disputes = []
        for chunk in chunks:
            text = chunk["text"]
            if any(marker in text.lower() for marker in dispute_markers):
                disputes.append(
                    {
                        "status": "needs_review",
                        "summary": self._trim(self._first_sentence(text), 220),
                        "source_chunk_id": chunk["chunk_id"],
                        "evidence_ids": list(chunk.get("evidence_ids") or [])[:8],
                    }
                )
        if disputes:
            return disputes
        return [
            {
                "status": "none_detected",
                "summary": "No explicit contradiction markers were found in the current evidence bundle.",
                "evidence_ids": self._collect_evidence_ids(chunks)[:8],
            }
        ]

    def _open_questions(self, page_type: str, title: str, chunks: list[dict[str, Any]]) -> list[dict[str, Any]]:
        evidence_ids = self._collect_evidence_ids(chunks)
        return [
            {
                "question": f"Which claims on {title} still need human review before publication?",
                "reason": "manual_review_required",
                "evidence_ids": evidence_ids[:8],
            },
            {
                "question": f"Has any source chunk for this {page_type} changed since the latest DocumentVersion?",
                "reason": "freshness_check",
                "evidence_ids": evidence_ids[:8],
            },
        ]

    def _review_state(self) -> dict[str, Any]:
        return {
            "status": "pending_review",
            "required": True,
            "reviewed_by": None,
            "reviewed_at": None,
        }

    def _evidence_coverage(
        self,
        claims: list[dict[str, Any]],
        citations: list[dict[str, Any]],
        evidence_ids: list[str],
    ) -> dict[str, Any]:
        claim_count = len(claims)
        covered_claim_count = sum(1 for claim in claims if claim.get("evidence_ids"))
        ratio = 1.0 if claim_count == 0 else covered_claim_count / claim_count
        return {
            "status": "covered" if evidence_ids and ratio >= 1.0 else "partial",
            "ratio": round(ratio, 6),
            "claim_count": claim_count,
            "covered_claim_count": covered_claim_count,
            "citation_count": len(citations),
            "evidence_count": len(evidence_ids),
        }

    def _citation_suffix(self, evidence_ids: list[str]) -> str:
        if not evidence_ids:
            return "`unsupported`"
        return " ".join(f"`{evidence_id}`" for evidence_id in evidence_ids[:3])

    def _extract_topics(self, source_chunks: list[dict[str, Any]], *, max_topics: int) -> list[str]:
        counter: Counter[str] = Counter()
        for chunk in source_chunks:
            for token in self._tokens(chunk["text"]):
                counter[token] += 1
        return [token for token, _count in counter.most_common(max_topics)]

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

    def _freshness(self, chunks: list[dict[str, Any]]) -> dict[str, Any]:
        evidence_ids = self._collect_evidence_ids(chunks)
        return {
            "status": "fresh",
            "source_chunk_count": len(chunks),
            "source_doc_version_ids": sorted({chunk["doc_version_id"] for chunk in chunks}),
            "source_chunk_ids": [chunk["chunk_id"] for chunk in chunks[:50]],
            "evidence_count": len(evidence_ids),
        }

    def _collect_evidence_ids(self, chunks: list[dict[str, Any]]) -> list[str]:
        evidence_ids: list[str] = []
        for chunk in chunks:
            for evidence_id in chunk.get("evidence_ids") or []:
                if evidence_id not in evidence_ids:
                    evidence_ids.append(evidence_id)
        return evidence_ids

    def _first_sentence(self, value: str) -> str:
        text = " ".join((value or "").split())
        if not text:
            return ""
        for delimiter in ("\u3002", ".", "\n"):
            if delimiter in text:
                return text.split(delimiter, 1)[0].strip() + delimiter
        return text

    def _unique_backlinks(self, backlinks: list[dict[str, str]]) -> list[dict[str, str]]:
        seen = set()
        unique = []
        for backlink in backlinks:
            page_id = backlink["page_id"]
            if page_id in seen:
                continue
            seen.add(page_id)
            unique.append(backlink)
        return unique

    def _slug(self, value: str) -> str:
        slug = re.sub(r"[^A-Za-z0-9\u4e00-\u9fff]+", "-", value.strip()).strip("-").lower()
        return slug or "page"

    def _trim(self, value: str | None, limit: int) -> str:
        text = value or ""
        if len(text) <= limit:
            return text
        return f"{text[:limit].rstrip()}..."
