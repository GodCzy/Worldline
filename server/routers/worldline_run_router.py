from __future__ import annotations

from fastapi import APIRouter, Body, Depends, HTTPException, Query

from server.utils.auth_middleware import get_admin_user
from src.services.worldline_run_ledger_service import WorldlineRunLedgerService
from src.storage.postgres.models_business import User

worldline_runs = APIRouter(prefix="/worldline/runs", tags=["worldline-runs"])


def _actor(current_user: User) -> str:
    return getattr(current_user, "username", None) or getattr(current_user, "user_id", None) or "admin"


@worldline_runs.post("")
async def create_worldline_run(
    payload: dict | None = Body(None),
    current_user: User = Depends(get_admin_user),
):
    """Create a durable Agent Worldline run without requiring DB schema changes."""
    return await WorldlineRunLedgerService().create_run(payload or {}, created_by=_actor(current_user))


@worldline_runs.get("")
async def list_worldline_runs(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    query: str = Query(""),
    status: str = Query(""),
    theme_id: str = Query(""),
    created_by: str = Query(""),
    current_user: User = Depends(get_admin_user),
):
    """List durable Agent Worldline runs as compact read-only summaries."""
    return await WorldlineRunLedgerService().list_runs(
        limit=limit,
        offset=offset,
        query=query,
        status=status,
        theme_id=theme_id,
        created_by=created_by,
    )


@worldline_runs.get("/compare")
async def compare_worldline_runs(
    left_run_id: str = Query(...),
    right_run_id: str = Query(...),
    current_user: User = Depends(get_admin_user),
):
    """Compare two durable Agent Worldline runs without mutating either run."""
    result = await WorldlineRunLedgerService().compare_runs(left_run_id, right_run_id)
    if result is None:
        raise HTTPException(status_code=404, detail=f"Worldline run comparison target not found: {left_run_id}/{right_run_id}")
    return result


@worldline_runs.get("/{run_id}")
async def get_worldline_run(run_id: str, current_user: User = Depends(get_admin_user)):
    run = await WorldlineRunLedgerService().get_run(run_id)
    if run is None:
        raise HTTPException(status_code=404, detail=f"Worldline run '{run_id}' not found")
    return run


@worldline_runs.get("/{run_id}/events")
async def list_worldline_run_events(
    run_id: str,
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_admin_user),
):
    result = await WorldlineRunLedgerService().list_events(run_id, limit=limit, offset=offset)
    if result is None:
        raise HTTPException(status_code=404, detail=f"Worldline run '{run_id}' not found")
    return result


@worldline_runs.get("/{run_id}/artifacts")
async def list_worldline_run_artifacts(
    run_id: str,
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_admin_user),
):
    result = await WorldlineRunLedgerService().list_artifacts(run_id, limit=limit, offset=offset)
    if result is None:
        raise HTTPException(status_code=404, detail=f"Worldline run '{run_id}' not found")
    return result


@worldline_runs.get("/{run_id}/manifest")
async def inspect_worldline_run_manifest(
    run_id: str,
    include_resources: bool = Query(True),
    limit: int = Query(50, ge=1, le=100),
    audit_db_id: str | None = Query(None),
    current_user: User = Depends(get_admin_user),
):
    from src.services.worldline_agent_workflow_service import WorldlineAgentWorkflowService

    result = await WorldlineAgentWorkflowService().inspect_run_manifest(
        run_id,
        include_resources=include_resources,
        limit=limit,
        audit_db_id=audit_db_id,
        actor=_actor(current_user),
    )
    if result.get("status") == "not_found":
        raise HTTPException(status_code=404, detail=f"Worldline run '{run_id}' not found")
    return result


def _raise_not_found_if_needed(result: dict, run_id: str, resource_label: str) -> None:
    if result.get("status") == "not_found":
        raise HTTPException(status_code=404, detail=f"Worldline run resource not found: {run_id}/{resource_label}")


@worldline_runs.get("/{run_id}/artifacts/read")
async def inspect_worldline_run_artifacts(
    run_id: str,
    artifact_id: str | None = Query(None),
    include_content: bool = Query(False),
    limit: int = Query(20, ge=1, le=100),
    audit_db_id: str | None = Query(None),
    current_user: User = Depends(get_admin_user),
):
    from src.services.worldline_agent_workflow_service import WorldlineAgentWorkflowService

    result = await WorldlineAgentWorkflowService().inspect_run_artifacts(
        run_id,
        artifact_id=artifact_id,
        include_content=include_content,
        limit=limit,
        audit_db_id=audit_db_id,
        actor=_actor(current_user),
    )
    _raise_not_found_if_needed(result, run_id, artifact_id or "artifacts")
    return result


@worldline_runs.get("/{run_id}/gates")
async def inspect_worldline_run_gates(
    run_id: str,
    gate_id: str | None = Query(None),
    limit: int = Query(20, ge=1, le=100),
    audit_db_id: str | None = Query(None),
    current_user: User = Depends(get_admin_user),
):
    from src.services.worldline_agent_workflow_service import WorldlineAgentWorkflowService

    result = await WorldlineAgentWorkflowService().inspect_run_gates(
        run_id,
        gate_id=gate_id,
        limit=limit,
        audit_db_id=audit_db_id,
        actor=_actor(current_user),
    )
    _raise_not_found_if_needed(result, run_id, gate_id or "gates")
    return result


@worldline_runs.get("/{run_id}/evidence")
async def inspect_worldline_run_evidence(
    run_id: str,
    evidence_id: str | None = Query(None),
    source_id: str | None = Query(None),
    limit: int = Query(20, ge=1, le=100),
    audit_db_id: str | None = Query(None),
    current_user: User = Depends(get_admin_user),
):
    from src.services.worldline_agent_workflow_service import WorldlineAgentWorkflowService

    result = await WorldlineAgentWorkflowService().inspect_run_evidence(
        run_id,
        evidence_id=evidence_id,
        source_id=source_id,
        limit=limit,
        audit_db_id=audit_db_id,
        actor=_actor(current_user),
    )
    _raise_not_found_if_needed(result, run_id, evidence_id or source_id or "evidence")
    return result


@worldline_runs.get("/{run_id}/knowledge")
async def inspect_worldline_run_knowledge(
    run_id: str,
    kind: str = Query("all"),
    item_id: str | None = Query(None),
    limit: int = Query(20, ge=1, le=100),
    audit_db_id: str | None = Query(None),
    current_user: User = Depends(get_admin_user),
):
    from src.services.worldline_agent_workflow_service import WorldlineAgentWorkflowService

    result = await WorldlineAgentWorkflowService().inspect_run_knowledge(
        run_id,
        kind=kind,
        item_id=item_id,
        limit=limit,
        audit_db_id=audit_db_id,
        actor=_actor(current_user),
    )
    _raise_not_found_if_needed(result, run_id, item_id or kind or "knowledge")
    return result


@worldline_runs.post("/{run_id}/artifacts")
async def register_worldline_run_artifact(
    run_id: str,
    payload: dict | None = Body(None),
    current_user: User = Depends(get_admin_user),
):
    result = await WorldlineRunLedgerService().register_artifact(run_id, payload or {}, actor=_actor(current_user))
    if result is None:
        raise HTTPException(status_code=404, detail=f"Worldline run '{run_id}' not found")
    return result


@worldline_runs.post("/{run_id}/rename")
async def rename_worldline_run(
    run_id: str,
    payload: dict | None = Body(None),
    current_user: User = Depends(get_admin_user),
):
    title = str((payload or {}).get("title") or (payload or {}).get("name") or "").strip()
    if not title:
        raise HTTPException(status_code=400, detail="Worldline run rename requires a non-empty title")
    result = await WorldlineRunLedgerService().rename_run(run_id, payload or {}, actor=_actor(current_user))
    if result is None:
        raise HTTPException(status_code=404, detail=f"Worldline run '{run_id}' not found")
    return result


@worldline_runs.post("/{run_id}/archive")
async def archive_worldline_run(
    run_id: str,
    payload: dict | None = Body(None),
    current_user: User = Depends(get_admin_user),
):
    result = await WorldlineRunLedgerService().archive_run(run_id, payload or {}, actor=_actor(current_user))
    if result is None:
        raise HTTPException(status_code=404, detail=f"Worldline run '{run_id}' not found")
    return result


@worldline_runs.post("/{run_id}/restore")
async def restore_worldline_run(
    run_id: str,
    payload: dict | None = Body(None),
    current_user: User = Depends(get_admin_user),
):
    result = await WorldlineRunLedgerService().restore_run(run_id, payload or {}, actor=_actor(current_user))
    if result is None:
        raise HTTPException(status_code=404, detail=f"Worldline run '{run_id}' not found")
    return result


@worldline_runs.post("/{run_id}/branches/{branch_id}/approve")
async def approve_worldline_branch(
    run_id: str,
    branch_id: str,
    payload: dict | None = Body(None),
    current_user: User = Depends(get_admin_user),
):
    result = await WorldlineRunLedgerService().approve_branch(
        run_id,
        branch_id,
        payload or {},
        actor=_actor(current_user),
    )
    if result is None:
        raise HTTPException(status_code=404, detail=f"Worldline run or branch not found: {run_id}/{branch_id}")
    return result


@worldline_runs.post("/{run_id}/branches/{branch_id}/reject")
async def reject_worldline_branch(
    run_id: str,
    branch_id: str,
    payload: dict | None = Body(None),
    current_user: User = Depends(get_admin_user),
):
    result = await WorldlineRunLedgerService().reject_branch(
        run_id,
        branch_id,
        payload or {},
        actor=_actor(current_user),
    )
    if result is None:
        raise HTTPException(status_code=404, detail=f"Worldline run or branch not found: {run_id}/{branch_id}")
    return result


@worldline_runs.post("/{run_id}/skills/propose")
async def propose_worldline_skill(
    run_id: str,
    payload: dict | None = Body(None),
    current_user: User = Depends(get_admin_user),
):
    result = await WorldlineRunLedgerService().propose_skill(run_id, payload or {}, actor=_actor(current_user))
    if result is None:
        raise HTTPException(status_code=404, detail=f"Worldline run '{run_id}' not found")
    return result
