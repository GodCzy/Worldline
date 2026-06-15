from __future__ import annotations

from fastapi import FastAPI
from fastapi.testclient import TestClient

from server.routers.worldline_public_demo_router import worldline_public_demo
from src.services.worldline_public_demo_service import PUBLIC_DEMO_SHARE_ID, WorldlinePublicDemoService


def test_public_demo_dataset_is_safe_and_deterministic() -> None:
    service = WorldlinePublicDemoService()

    first = service.get_dataset()
    second = service.get_dataset()

    assert first["protocolVersion"] == "worldline-public-demo-v0.1"
    assert first["datasetId"] == "worldline-public-demo-safety-v1"
    assert first["checksum"] == second["checksum"]
    assert first["safety"]["status"] == "passed"
    assert first["safety"]["secretViolations"] == []
    assert first["shareViews"][0]["mode"] == "read_only"


def test_public_branch_share_is_read_only_and_bundle_backed() -> None:
    service = WorldlinePublicDemoService()

    share = service.get_branch_share(PUBLIC_DEMO_SHARE_ID)

    assert share is not None
    assert share["readOnly"] is True
    assert share["mode"] == "read_only"
    assert share["share"]["allowedActions"] == [
        "inspect",
        "download_json_bundle",
        "download_markdown_bundle",
    ]
    assert share["branch"]["id"] == "branch-evidence"
    assert share["worldline"]["activeBranchId"] == "branch-evidence"
    assert "checksum" in share["bundlePreview"]
    assert share["safety"]["status"] == "passed"


def test_public_evidence_bundle_contains_replay_capsule_and_checksum() -> None:
    service = WorldlinePublicDemoService()

    bundle = service.build_evidence_bundle(share_id=PUBLIC_DEMO_SHARE_ID)
    markdown = service.build_bundle_markdown(share_id=PUBLIC_DEMO_SHARE_ID)

    assert bundle["protocolVersion"] == "worldline-evidence-bundle-v0.1"
    assert bundle["readOnly"] is True
    assert bundle["branch"]["id"] == "branch-evidence"
    assert bundle["sections"]["evidence"]
    assert bundle["sections"]["qualityGates"]
    assert bundle["replayCapsule"]["steps"]
    assert bundle["checksum"].startswith("sha256:")
    assert bundle["checksum"] in markdown
    assert "Replay Capsule" in markdown
    assert "Rollback" in markdown


def test_public_demo_router_exposes_read_only_routes_without_auth_dependency() -> None:
    app = FastAPI()
    app.include_router(worldline_public_demo)
    client = TestClient(app)

    dataset_response = client.get("/worldline/public-demo/dataset")
    share_response = client.get(f"/worldline/public-demo/branches/{PUBLIC_DEMO_SHARE_ID}")
    bundle_response = client.get(
        f"/worldline/public-demo/evidence-bundle?share_id={PUBLIC_DEMO_SHARE_ID}&format=markdown"
    )

    assert dataset_response.status_code == 200
    assert dataset_response.json()["safety"]["status"] == "passed"
    assert share_response.status_code == 200
    assert share_response.json()["readOnly"] is True
    assert bundle_response.status_code == 200
    assert "worldline-evidence-bundle-v0.1" in bundle_response.text
    assert client.post("/worldline/public-demo/dataset").status_code == 405
