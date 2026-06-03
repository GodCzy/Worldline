from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]

SERVICE_PATH = PROJECT_ROOT / "src" / "services" / "worldline_release_gate_service.py"
SERVICE_SPEC = importlib.util.spec_from_file_location("worldline_release_gate_service", SERVICE_PATH)
if SERVICE_SPEC is None or SERVICE_SPEC.loader is None:
    raise RuntimeError(f"Unable to load release gate service from {SERVICE_PATH}")
SERVICE_MODULE = importlib.util.module_from_spec(SERVICE_SPEC)
sys.modules[SERVICE_SPEC.name] = SERVICE_MODULE
SERVICE_SPEC.loader.exec_module(SERVICE_MODULE)
WorldlineReleaseGateService = SERVICE_MODULE.WorldlineReleaseGateService


DEFAULT_OUTPUT = ".ai/tasks/2026-06-03-phase6-7-governance-release/release-gate-report.json"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the Worldline Phase 6/7 static release gate.")
    parser.add_argument("--project-root", default=str(PROJECT_ROOT), help="Worldline project root.")
    parser.add_argument("--codex-skills-root", default=None, help="Codex skills root override.")
    parser.add_argument("--output", default=DEFAULT_OUTPUT, help="JSON report output path.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    service = WorldlineReleaseGateService(
        project_root=args.project_root,
        codex_skills_root=args.codex_skills_root,
    )
    report = service.write_report(args.output)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
