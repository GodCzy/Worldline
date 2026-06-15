from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import PlainTextResponse

from src.services.worldline_public_demo_service import PUBLIC_DEMO_SHARE_ID, WorldlinePublicDemoService

worldline_public_demo = APIRouter(prefix="/worldline/public-demo", tags=["worldline-public-demo"])


@worldline_public_demo.get("/dataset")
async def get_worldline_public_demo_dataset():
    """Return the deterministic, safe public demo dataset."""
    return WorldlinePublicDemoService().get_dataset()


@worldline_public_demo.get("/branches/{share_id}")
async def get_worldline_public_demo_branch(share_id: str):
    """Return a read-only branch share payload."""
    result = WorldlinePublicDemoService().get_branch_share(share_id)
    if result is None:
        raise HTTPException(status_code=404, detail=f"Worldline public demo share not found: {share_id}")
    return result


@worldline_public_demo.get("/evidence-bundle")
async def export_worldline_public_demo_evidence_bundle(
    share_id: str = Query(PUBLIC_DEMO_SHARE_ID),
    format: str = Query("json", pattern="^(json|markdown)$"),
):
    """Export a read-only evidence/replay capsule as JSON or Markdown."""
    service = WorldlinePublicDemoService()
    try:
        if format == "markdown":
            return PlainTextResponse(
                service.build_bundle_markdown(share_id=share_id),
                media_type="text/markdown; charset=utf-8",
            )
        return service.build_evidence_bundle(share_id=share_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
