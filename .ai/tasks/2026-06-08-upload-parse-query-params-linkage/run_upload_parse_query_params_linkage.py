from __future__ import annotations

import asyncio
import json
import os
import time
from pathlib import Path
from typing import Any

import httpx

from src.repositories.knowledge_base_repository import KnowledgeBaseRepository
from src.repositories.knowledge_file_repository import KnowledgeFileRepository
from src.storage.postgres.manager import pg_manager


API_BASE_URL = os.getenv("TEST_BASE_URL", "http://127.0.0.1:5050").rstrip("/")
TEST_USERNAME = os.environ["TEST_USERNAME"]
TEST_PASSWORD = os.environ["TEST_PASSWORD"]
RUN_STAMP = os.getenv("WORLDLINE_P2_STAMP") or str(int(time.time()))
DB_NAME = f"pytest_upload_parse_{RUN_STAMP}"
HTTP_TIMEOUT = httpx.Timeout(60.0, connect=10.0)


def _expect(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


async def _login(client: httpx.AsyncClient) -> dict[str, str]:
    response = await client.post("/api/auth/token", data={"username": TEST_USERNAME, "password": TEST_PASSWORD})
    _expect(response.status_code == 200, f"Login failed: {response.status_code} {response.text}")
    token = response.json().get("access_token")
    _expect(bool(token), "Login response did not include access_token")
    return {"Authorization": f"Bearer {token}"}


async def _wait_task(client: httpx.AsyncClient, headers: dict[str, str], task_id: str) -> dict[str, Any]:
    for _ in range(90):
        response = await client.get(f"/api/tasks/{task_id}", headers=headers)
        _expect(response.status_code == 200, f"Task fetch failed: {response.status_code} {response.text}")
        task = response.json()["task"]
        if task["status"] in {"success", "failed", "cancelled"}:
            return task
        await asyncio.sleep(1)
    raise RuntimeError(f"Task {task_id} did not finish in time")


def _processing_assertions(processing_params: dict[str, Any]) -> dict[str, Any]:
    parser_config = processing_params.get("chunk_parser_config") or {}
    checks = {
        "content_type": processing_params.get("content_type"),
        "enable_ocr": processing_params.get("enable_ocr"),
        "chunk_preset_id": processing_params.get("chunk_preset_id"),
        "chunk_size": processing_params.get("chunk_size"),
        "chunk_overlap": processing_params.get("chunk_overlap"),
        "qa_separator": processing_params.get("qa_separator"),
        "chunk_token_num": parser_config.get("chunk_token_num"),
        "overlapped_percent": parser_config.get("overlapped_percent"),
        "delimiter": parser_config.get("delimiter"),
        "has_document_compile": "document_compile" in processing_params,
    }
    _expect(checks["content_type"] == "file", f"content_type mismatch: {checks}")
    _expect(checks["enable_ocr"] == "disable", f"enable_ocr mismatch: {checks}")
    _expect(checks["chunk_preset_id"] == "qa", f"chunk_preset_id mismatch: {checks}")
    _expect(checks["chunk_size"] == 321, f"chunk_size mismatch: {checks}")
    _expect(checks["chunk_overlap"] == 33, f"chunk_overlap mismatch: {checks}")
    _expect(checks["qa_separator"] == "\n@@\n", f"qa_separator mismatch: {checks}")
    _expect(checks["chunk_token_num"] == 321, f"chunk_token_num mismatch: {checks}")
    _expect(checks["overlapped_percent"] == 10, f"overlapped_percent mismatch: {checks}")
    _expect(checks["delimiter"] == "\n@@\n", f"delimiter mismatch: {checks}")
    _expect(checks["has_document_compile"] is True, f"document_compile missing: {checks}")
    return checks


async def run() -> dict[str, Any]:
    pg_manager.initialize()
    await pg_manager.ensure_knowledge_schema()

    async with httpx.AsyncClient(base_url=API_BASE_URL, timeout=HTTP_TIMEOUT, follow_redirects=True, trust_env=False) as client:
        headers = await _login(client)

        create_response = await client.post(
            "/api/knowledge/databases",
            json={
                "database_name": DB_NAME,
                "description": "P2 upload parse params live verification",
                "embed_model_name": "siliconflow/BAAI/bge-m3",
                "kb_type": "lightrag",
                "additional_params": {"chunk_preset_id": "general"},
            },
            headers=headers,
        )
        _expect(create_response.status_code == 200, f"Create DB failed: {create_response.status_code} {create_response.text}")
        db_id = create_response.json()["db_id"]

        try:
            source_text = "\n".join(
                [
                    "# Codex P2 Upload Parse",
                    "",
                    "This file verifies upload and parse parameter persistence.",
                    "The qa separator and chunk parser config must survive the full add-document task.",
                ]
            )
            upload_response = await client.post(
                f"/api/knowledge/files/upload?db_id={db_id}",
                files={"file": ("codex-p2-upload.txt", source_text.encode("utf-8"), "text/plain")},
                headers=headers,
            )
            _expect(
                upload_response.status_code == 200,
                f"Upload failed: {upload_response.status_code} {upload_response.text}",
            )
            upload_payload = upload_response.json()
            file_path = upload_payload["file_path"]
            content_hash = upload_payload["content_hash"]

            add_params = {
                "content_type": "file",
                "content_hashes": {file_path: content_hash},
                "enable_ocr": "disable",
                "chunk_size": 321,
                "chunk_overlap": 33,
                "qa_separator": "\n@@\n",
                "chunk_preset_id": "qa",
                "chunk_parser_config": {
                    "chunk_token_num": 321,
                    "overlapped_percent": 5,
                    "delimiter": "\n@@\n",
                },
            }
            add_response = await client.post(
                f"/api/knowledge/databases/{db_id}/documents",
                json={"items": [file_path], "params": add_params},
                headers=headers,
            )
            _expect(add_response.status_code == 200, f"Add documents failed: {add_response.status_code} {add_response.text}")
            add_payload = add_response.json()
            _expect(add_payload.get("status") == "queued", f"Add task was not queued: {add_payload}")

            task = await _wait_task(client, headers, add_payload["task_id"])
            _expect(task["status"] == "success", f"Add/parse task failed: {task}")

            file_rows = await KnowledgeFileRepository().list_by_db_id(db_id)
            _expect(len(file_rows) == 1, f"Expected one file row, got {len(file_rows)}")
            file_row = file_rows[0]
            _expect(file_row.status == "parsed", f"Expected parsed status, got {file_row.status}")
            checks = _processing_assertions(file_row.processing_params or {})

            return {
                "status": "ok",
                "db_id": db_id,
                "task_id": add_payload["task_id"],
                "file_id": file_row.file_id,
                "file_status": file_row.status,
                "processing_checks": checks,
            }
        finally:
            delete_response = await client.delete(f"/api/knowledge/databases/{db_id}", headers=headers)
            if delete_response.status_code not in {200, 404}:
                raise RuntimeError(f"Cleanup failed for {db_id}: {delete_response.status_code} {delete_response.text}")
            kb_row = await KnowledgeBaseRepository().get_by_id(db_id)
            _expect(kb_row is None, f"Temporary KB row still exists after cleanup: {db_id}")


async def main() -> int:
    result = await run()
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
