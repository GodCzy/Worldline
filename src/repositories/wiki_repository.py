from __future__ import annotations

from typing import Any

from sqlalchemy import delete, select

from src.storage.postgres.manager import pg_manager
from src.storage.postgres.models_knowledge import KnowledgeChunk, KnowledgeFile, WikiPage
from src.utils import hashstr


class WikiRepository:
    """Persistence boundary for Auto-Wiki pages."""

    async def upsert_pages(self, db_id: str, pages: list[dict[str, Any]]) -> list[dict[str, Any]]:
        if not pages:
            return []

        page_ids = [page["page_id"] for page in pages]
        async with pg_manager.get_async_session_context() as session:
            existing_result = await session.execute(
                select(WikiPage).where(WikiPage.db_id == db_id, WikiPage.page_id.in_(page_ids))
            )
            existing = {page.page_id: page for page in existing_result.scalars().all()}

            for page in pages:
                payload = self._normalize_page_payload(db_id, page)
                wiki_page = existing.get(payload["page_id"])
                if wiki_page is None:
                    session.add(WikiPage(**payload))
                else:
                    for key, value in payload.items():
                        if key != "page_id":
                            setattr(wiki_page, key, value)

        return pages

    async def replace_pages_for_scope(
        self,
        db_id: str,
        *,
        file_id: str | None = None,
        page_types: list[str] | None = None,
    ) -> None:
        async with pg_manager.get_async_session_context() as session:
            stmt = delete(WikiPage).where(WikiPage.db_id == db_id)
            if file_id:
                stmt = stmt.where(WikiPage.source_id == file_id)
            if page_types:
                stmt = stmt.where(WikiPage.page_type.in_(page_types))
            await session.execute(stmt)

    async def list_pages(
        self,
        db_id: str,
        *,
        page_type: str | None = None,
        source_id: str | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> dict[str, Any]:
        limit = max(1, min(int(limit or 50), 200))
        offset = max(0, int(offset or 0))

        async with pg_manager.get_async_session_context() as session:
            stmt = (
                select(WikiPage)
                .where(WikiPage.db_id == db_id)
                .order_by(WikiPage.page_type, WikiPage.title)
                .offset(offset)
                .limit(limit + 1)
            )
            if page_type:
                stmt = stmt.where(WikiPage.page_type == page_type)
            if source_id:
                stmt = stmt.where(WikiPage.source_id == source_id)
            rows = (await session.execute(stmt)).scalars().all()

        return {
            "items": [self.serialize_page(page, include_markdown=False) for page in rows[:limit]],
            "limit": limit,
            "offset": offset,
            "has_more": len(rows) > limit,
        }

    async def get_page(self, db_id: str, page_id: str) -> dict[str, Any] | None:
        async with pg_manager.get_async_session_context() as session:
            result = await session.execute(
                select(WikiPage).where(WikiPage.db_id == db_id, WikiPage.page_id == page_id).limit(1)
            )
            page = result.scalar_one_or_none()
        return self.serialize_page(page, include_markdown=True) if page else None

    async def get_page_by_slug(self, db_id: str, slug: str) -> dict[str, Any] | None:
        async with pg_manager.get_async_session_context() as session:
            result = await session.execute(
                select(WikiPage).where(WikiPage.db_id == db_id, WikiPage.slug == slug).limit(1)
            )
            page = result.scalar_one_or_none()
        return self.serialize_page(page, include_markdown=True) if page else None

    async def list_source_chunks(self, db_id: str, *, file_id: str | None = None) -> list[dict[str, Any]]:
        async with pg_manager.get_async_session_context() as session:
            stmt = (
                select(KnowledgeChunk, KnowledgeFile)
                .join(KnowledgeFile, KnowledgeChunk.file_id == KnowledgeFile.file_id)
                .where(KnowledgeChunk.db_id == db_id)
                .order_by(KnowledgeFile.filename, KnowledgeChunk.chunk_index)
            )
            if file_id:
                stmt = stmt.where(KnowledgeChunk.file_id == file_id)
            rows = (await session.execute(stmt)).all()

        source_chunks: list[dict[str, Any]] = []
        for chunk, file_record in rows:
            source_chunks.append(
                {
                    "chunk_id": chunk.chunk_id,
                    "db_id": chunk.db_id,
                    "file_id": chunk.file_id,
                    "filename": file_record.filename,
                    "doc_version_id": chunk.doc_version_id,
                    "chunk_index": chunk.chunk_index,
                    "text": chunk.text,
                    "evidence_ids": list(chunk.evidence_ids or []),
                    "metadata": chunk.chunk_metadata or {},
                }
            )
        return source_chunks

    def make_page_id(self, db_id: str, page_type: str, source_id: str | None, slug: str) -> str:
        stable_source = source_id or ""
        return f"wiki_{hashstr(f'{db_id}:{page_type}:{stable_source}:{slug}', length=32)}"

    def serialize_page(self, page: WikiPage, *, include_markdown: bool) -> dict[str, Any]:
        payload = {
            "page_id": page.page_id,
            "db_id": page.db_id,
            "page_type": page.page_type,
            "slug": page.slug,
            "title": page.title,
            "source_id": page.source_id,
            "backlinks": page.backlinks or [],
            "evidence_ids": page.evidence_ids or [],
            "freshness": page.freshness or {},
            "status": page.status,
            "metadata": page.page_metadata or {},
            "generated_at": page.generated_at.isoformat() if page.generated_at else None,
            "updated_at": page.updated_at.isoformat() if page.updated_at else None,
        }
        if include_markdown:
            payload["markdown"] = page.markdown
        else:
            payload["markdown_preview"] = self._trim(page.markdown, 500)
        return payload

    def _normalize_page_payload(self, db_id: str, page: dict[str, Any]) -> dict[str, Any]:
        return {
            "page_id": page["page_id"],
            "db_id": db_id,
            "page_type": page["page_type"],
            "slug": page["slug"],
            "title": page["title"],
            "source_id": page.get("source_id"),
            "markdown": page["markdown"],
            "backlinks": page.get("backlinks") or [],
            "evidence_ids": page.get("evidence_ids") or [],
            "freshness": page.get("freshness") or {},
            "status": page.get("status") or "active",
            "page_metadata": page.get("metadata") or {},
        }

    def _trim(self, value: str | None, limit: int) -> str:
        text = value or ""
        if len(text) <= limit:
            return text
        return f"{text[:limit].rstrip()}..."
