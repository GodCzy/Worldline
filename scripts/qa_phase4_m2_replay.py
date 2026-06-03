#!/usr/bin/env python3
"""
Unified graph/auth replay entry.

This script hardens process orchestration only:
- L0 runtime checks
- L1 readonly API matrix via qa_graph_auth_readonly_check.py
- L2 UI guard evidence validation from provided source directory

No business route logic is changed here.
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from urllib import error, request

EXIT_SUCCESS = 0
EXIT_RUNTIME_FAILED = 2
EXIT_API_FAILED = 3
EXIT_UI_FAILED = 4
EXIT_SUMMARY_FAILED = 5
EXIT_PRECONDITION_FAILED = 6

DEFAULT_PREFIX = "qa-graph-auth-replay"
BLOCKER_RULE = "first failing item in order: precondition -> L0-runtime -> L1-api-matrix -> L2-ui-guard -> summary"
SECRET_FILE_RETRY_ATTEMPTS = 1
SECRET_FILE_RETRY_DELAY_SECONDS = 1.0
SECRET_SOURCE_ORDER = "cli -> cli-file -> manifest -> manifest-file -> env -> env-file"
REQUIRED_UI_FILES = [
    "30-ui-graph-guard.png",
    "31-ui-network-graph-guard.txt",
    "32-ui-final-url-assertion.json",
]
ERROR_PREFIX = "[m2-replay-error]"


@dataclass
class StageResult:
    name: str
    ok: bool
    note: str = ""


@dataclass
class ReplayError:
    code: int
    kind: str
    message: str
    details: dict[str, object]


def _utc_stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")


def _env_str(default: str, *names: str) -> str:
    for name in names:
        value = os.getenv(name)
        if value is None:
            continue
        stripped = value.strip()
        if stripped:
            return stripped
    return default


def _env_bool(default: bool, *names: str) -> bool:
    for name in names:
        value = os.getenv(name)
        if value is None:
            continue
        stripped = value.strip().lower()
        if stripped in {"1", "true", "yes", "on"}:
            return True
        if stripped in {"0", "false", "no", "off"}:
            return False
    return default


def _env_int(default: int, *names: str) -> int:
    for name in names:
        value = os.getenv(name)
        if value is None:
            continue
        stripped = value.strip()
        if not stripped:
            continue
        try:
            return int(stripped)
        except ValueError:
            continue
    return default


def _first_non_empty(*values: object) -> str | None:
    for value in values:
        if value is None:
            continue
        if isinstance(value, str):
            stripped = value.strip()
            if stripped:
                return stripped
        else:
            text = str(value).strip()
            if text:
                return text
    return None


def _read_text_file(path_str: str) -> tuple[str | None, str | None]:
    if not path_str:
        return None, None

    path = Path(path_str).expanduser()
    if not path.exists():
        return None, f"credential file does not exist: {path}"
    if path.is_dir():
        return None, f"credential file is a directory: {path}"

    try:
        content = path.read_text(encoding="utf-8-sig")
    except Exception as exc:
        return None, f"failed to read credential file {path}: {exc}"

    value = content.strip()
    if not value:
        return None, f"credential file is empty: {path}"
    return value, None


def _read_text_file_with_retry(path_str: str, retry_attempts: int = SECRET_FILE_RETRY_ATTEMPTS, retry_delay_seconds: float = SECRET_FILE_RETRY_DELAY_SECONDS) -> tuple[str | None, str | None, int]:
    attempts = 0
    last_error: str | None = None

    while attempts <= retry_attempts:
        attempts += 1
        value, error_message = _read_text_file(path_str)
        if error_message is None:
            return value, None, attempts
        last_error = error_message
        if attempts <= retry_attempts:
            time.sleep(retry_delay_seconds)

    return None, last_error, attempts


def _read_json_file(path_str: str) -> tuple[dict[str, object] | None, str | None]:
    if not path_str:
        return None, None

    path = Path(path_str).expanduser()
    if not path.exists():
        return None, f"manifest does not exist: {path}"
    if path.is_dir():
        return None, f"manifest is a directory: {path}"

    try:
        payload = json.loads(path.read_text(encoding="utf-8-sig"))
    except Exception as exc:
        return None, f"failed to read manifest {path}: {exc}"

    if not isinstance(payload, dict):
        return None, f"manifest must be a JSON object: {path}"
    return payload, None


def _coerce_bool(value: object) -> bool | None:
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return bool(value)
    if isinstance(value, str):
        stripped = value.strip().lower()
        if stripped in {"1", "true", "yes", "on"}:
            return True
        if stripped in {"0", "false", "no", "off"}:
            return False
    return None


def _coerce_int(value: object) -> int | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, int):
        return value
    if isinstance(value, float) and value.is_integer():
        return int(value)
    if isinstance(value, str):
        stripped = value.strip()
        if not stripped:
            return None
        try:
            return int(stripped)
        except ValueError:
            return None
    return None


def _resolve_value(*, cli_value: object, manifest_value: object, env_name: str, default: str) -> tuple[str, str]:
    value = _first_non_empty(cli_value)
    if value is not None:
        return value, "cli"

    value = _first_non_empty(manifest_value)
    if value is not None:
        return value, "manifest"

    value = _first_non_empty(_env_str("", env_name))
    if value is not None:
        return value, "env"

    return default, "default"


def _resolve_bool(*, cli_value: object, manifest_value: object, env_name: str, default: bool) -> tuple[bool, str]:
    cli_bool = _coerce_bool(cli_value)
    if cli_bool is not None:
        return cli_bool, "cli"

    manifest_bool = _coerce_bool(manifest_value)
    if manifest_bool is not None:
        return manifest_bool, "manifest"

    if env_name and env_name in os.environ:
        return _env_bool(default, env_name), "env"

    return default, "default"


def _resolve_int(*, cli_value: object, manifest_value: object, env_name: str, default: int) -> tuple[int, str]:
    cli_int = _coerce_int(cli_value)
    if cli_int is not None:
        return cli_int, "cli"

    manifest_int = _coerce_int(manifest_value)
    if manifest_int is not None:
        return manifest_int, "manifest"

    if env_name and env_name in os.environ:
        return _env_int(default, env_name), "env"

    return default, "default"


def _run_cmd(cmd: list[str]) -> tuple[int, str, str]:
    proc = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    return proc.returncode, proc.stdout, proc.stderr


def _http_status(url: str, timeout: int) -> tuple[int | None, str]:
    req = request.Request(url=url, method="GET")
    try:
        with request.urlopen(req, timeout=timeout) as resp:
            return resp.status, ""
    except error.HTTPError as exc:
        return exc.code, ""
    except Exception as exc:  # pragma: no cover
        return None, str(exc)


def _write_text(path: Path, content: str) -> None:
    path.write_text(content, encoding="utf-8")


def _write_json(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def _extract_run_dir(stdout: str) -> str | None:
    for line in stdout.splitlines():
        marker = "[qa-readonly] run_dir:"
        if marker in line:
            return line.split(marker, 1)[1].strip()
    return None


def _validate_ui_assertion(path: Path) -> tuple[bool, str]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        return False, f"failed to parse ui assertion json: {exc}"
    if isinstance(payload, dict):
        if payload.get("isAllowedFallback") is True:
            return True, "isAllowedFallback=true"
        if str(payload.get("assertion", "")).upper() == "PASS":
            return True, "assertion=PASS"
    return False, "ui assertion does not indicate pass"


def _emit_error(error_payload: ReplayError) -> None:
    print(f"{ERROR_PREFIX} {json.dumps(error_payload.__dict__, ensure_ascii=False, sort_keys=True)}")


def _main_blocker(
    *,
    stage: str,
    code: int,
    kind: str,
    message: str,
    details: dict[str, object] | None = None,
) -> dict[str, object]:
    return {
        "rule": BLOCKER_RULE,
        "stage": stage,
        "code": code,
        "kind": kind,
        "message": message,
        "details": details or {},
    }


def _resolve_credential(
    *,
    label: str,
    cli_value: object,
    cli_file_path: object,
    manifest_value: object,
    manifest_file_path: object,
    env_value_name: str,
    env_file_name: str,
) -> tuple[str | None, str | None, str | None, dict[str, object]]:
    value = _first_non_empty(cli_value)
    if value is not None:
        return value, "cli", None, {"source": "cli", "retry_attempts": 0}

    file_path = _first_non_empty(cli_file_path)
    if file_path is not None:
        file_value, error_message, attempts = _read_text_file_with_retry(file_path)
        if error_message:
            return None, None, error_message, {
                "source": "cli-file",
                "path": file_path,
                "retry_attempts": attempts,
                "retry_delay_seconds": SECRET_FILE_RETRY_DELAY_SECONDS,
            }
        return file_value, "cli-file", None, {
            "source": "cli-file",
            "path": file_path,
            "retry_attempts": attempts,
            "retry_delay_seconds": SECRET_FILE_RETRY_DELAY_SECONDS,
        }

    value = _first_non_empty(manifest_value)
    if value is not None:
        return value, "manifest", None, {"source": "manifest", "retry_attempts": 0}

    file_path = _first_non_empty(manifest_file_path)
    if file_path is not None:
        file_value, error_message, attempts = _read_text_file_with_retry(file_path)
        if error_message:
            return None, None, error_message, {
                "source": "manifest-file",
                "path": file_path,
                "retry_attempts": attempts,
                "retry_delay_seconds": SECRET_FILE_RETRY_DELAY_SECONDS,
            }
        return file_value, "manifest-file", None, {
            "source": "manifest-file",
            "path": file_path,
            "retry_attempts": attempts,
            "retry_delay_seconds": SECRET_FILE_RETRY_DELAY_SECONDS,
        }

    env_value = _env_str("", env_value_name)
    if env_value:
        return env_value, "env", None, {"source": "env", "retry_attempts": 0}

    env_file = _env_str("", env_file_name)
    if env_file:
        file_value, error_message, attempts = _read_text_file_with_retry(env_file)
        if error_message:
            return None, None, error_message, {
                "source": "env-file",
                "path": env_file,
                "retry_attempts": attempts,
                "retry_delay_seconds": SECRET_FILE_RETRY_DELAY_SECONDS,
            }
        return file_value, "env-file", None, {
            "source": "env-file",
            "path": env_file,
            "retry_attempts": attempts,
            "retry_delay_seconds": SECRET_FILE_RETRY_DELAY_SECONDS,
        }

    return None, None, f"missing required {label} credential after checking all supported sources", {
        "sources_checked": SECRET_SOURCE_ORDER,
        "retry_attempts": 0,
        "retry_delay_seconds": 0,
    }


def _resolve_runtime_inputs(args: argparse.Namespace) -> tuple[dict[str, object], ReplayError | None]:
    manifest_path = _first_non_empty(args.replay_manifest, _env_str("", "WORLDLINE_QA_REPLAY_MANIFEST"))
    manifest_data: dict[str, object] = {}
    manifest_source = "default"
    if manifest_path:
        loaded_manifest, manifest_error = _read_json_file(manifest_path)
        if manifest_error:
            return {}, ReplayError(
                code=EXIT_PRECONDITION_FAILED,
                kind="manifest_error",
                message="replay manifest resolution failed",
                details={"replay_manifest": manifest_path, "error": manifest_error},
            )
        manifest_data = loaded_manifest or {}
        manifest_source = "cli" if _first_non_empty(args.replay_manifest) else "env"

    api_base, api_source = _resolve_value(
        cli_value=args.api_base,
        manifest_value=manifest_data.get("api_base"),
        env_name="WORLDLINE_QA_API_BASE",
        default="http://127.0.0.1:5050",
    )
    frontend_base, frontend_source = _resolve_value(
        cli_value=args.frontend_base,
        manifest_value=manifest_data.get("frontend_base"),
        env_name="WORLDLINE_QA_FRONTEND_BASE",
        default="http://127.0.0.1:5173",
    )
    out_dir, out_dir_source = _resolve_value(
        cli_value=args.out_dir,
        manifest_value=manifest_data.get("out_dir"),
        env_name="WORLDLINE_QA_OUT_DIR",
        default="artifacts",
    )
    artifact_prefix, prefix_source = _resolve_value(
        cli_value=args.artifact_prefix,
        manifest_value=manifest_data.get("artifact_prefix"),
        env_name="WORLDLINE_QA_M2_PREFIX",
        default=DEFAULT_PREFIX,
    )
    timeout_seconds, timeout_source = _resolve_int(
        cli_value=args.timeout_seconds,
        manifest_value=manifest_data.get("timeout_seconds"),
        env_name="WORLDLINE_QA_TIMEOUT_SECONDS",
        default=12,
    )
    skip_runtime, skip_runtime_source = _resolve_bool(
        cli_value=args.skip_runtime,
        manifest_value=manifest_data.get("skip_runtime"),
        env_name="WORLDLINE_QA_SKIP_RUNTIME",
        default=False,
    )
    ui_source_dir, ui_source_dir_source = _resolve_value(
        cli_value=args.ui_source_dir,
        manifest_value=manifest_data.get("ui_source_dir"),
        env_name="WORLDLINE_QA_UI_SOURCE_DIR",
        default="",
    )

    admin_token, admin_source, admin_error, admin_details = _resolve_credential(
        label="admin token",
        cli_value=args.admin_token,
        cli_file_path=args.admin_token_file,
        manifest_value=manifest_data.get("admin_token"),
        manifest_file_path=manifest_data.get("admin_token_file"),
        env_value_name="WORLDLINE_QA_ADMIN_TOKEN",
        env_file_name="WORLDLINE_QA_ADMIN_TOKEN_FILE",
    )
    if admin_error:
        return {}, ReplayError(
            code=EXIT_PRECONDITION_FAILED,
            kind="credential_file_error" if "credential file" in admin_error else "credential_missing",
            message="admin credential resolution failed",
            details={"credential": "admin_token", "error": admin_error, **admin_details},
        )

    user_token, user_source, user_error, user_details = _resolve_credential(
        label="user token",
        cli_value=args.user_token,
        cli_file_path=args.user_token_file,
        manifest_value=manifest_data.get("user_token"),
        manifest_file_path=manifest_data.get("user_token_file"),
        env_value_name="WORLDLINE_QA_USER_TOKEN",
        env_file_name="WORLDLINE_QA_USER_TOKEN_FILE",
    )
    if user_error:
        return {}, ReplayError(
            code=EXIT_PRECONDITION_FAILED,
            kind="credential_file_error" if "credential file" in user_error else "credential_missing",
            message="user credential resolution failed",
            details={"credential": "user_token", "error": user_error, **user_details},
        )

    resolved = {
        "replay_manifest": manifest_path or "",
        "replay_manifest_source": manifest_source,
        "api_base": api_base,
        "api_base_source": api_source,
        "frontend_base": frontend_base,
        "frontend_base_source": frontend_source,
        "out_dir": out_dir,
        "out_dir_source": out_dir_source,
        "artifact_prefix": artifact_prefix,
        "artifact_prefix_source": prefix_source,
        "timeout_seconds": timeout_seconds,
        "timeout_source": timeout_source,
        "skip_runtime": skip_runtime,
        "skip_runtime_source": skip_runtime_source,
        "ui_source_dir": ui_source_dir,
        "ui_source_dir_source": ui_source_dir_source,
        "admin_token": admin_token or "",
        "admin_token_source": admin_source or "unknown",
        "user_token": user_token or "",
        "user_token_source": user_source or "unknown",
    }
    return resolved, None


def _finalize_precondition_failure(
    *,
    run_dir: Path,
    metadata: dict,
    failure: ReplayError,
    main_blocker: dict[str, object],
    summary_lines: list[str],
) -> int:
    metadata["final_exit_code"] = failure.code
    metadata["failure"] = failure.__dict__
    metadata["main_blocker"] = main_blocker
    _write_json(run_dir / "00-run-metadata.json", metadata)
    _write_json(run_dir / "01-precondition-error.json", failure.__dict__)
    _write_json(run_dir / "02-main-blocker.json", main_blocker)
    _write_text(run_dir / "99-evidence-summary.md", "\n".join(summary_lines) + "\n")
    _emit_error(failure)
    print(f"[m2-replay] run_dir: {run_dir}")
    print(f"[m2-replay] exit_code: {failure.code}")
    return failure.code


def _build_runtime_report(api_base: str, timeout: int) -> tuple[bool, str]:
    checks: list[tuple[str, bool, str]] = []

    rc, out, err = _run_cmd(["docker", "compose", "ps"])
    checks.append(("docker_compose_ps", rc == 0, (out + err).strip()))

    rc, out, err = _run_cmd(["docker", "inspect", "--format", "{{.State.Status}}", "api-dev"])
    status_ok = rc == 0 and out.strip() in {"running"}
    checks.append(("docker_api_dev_status", status_ok, (out + err).strip()))

    rc, out, err = _run_cmd(["docker", "inspect", "--format", "{{.State.Health.Status}}", "graph"])
    health_ok = rc == 0 and out.strip() == "healthy"
    checks.append(("docker_graph_health", health_ok, (out + err).strip()))

    http_code, http_err = _http_status(f"{api_base.rstrip('/')}/api/system/health", timeout=timeout)
    checks.append(("api_system_health", http_code == 200, f"status={http_code} err={http_err}".strip()))

    lines = ["# Runtime Health (L0)", ""]
    all_ok = True
    for name, ok, detail in checks:
        lines.append(f"- [{'PASS' if ok else 'FAIL'}] {name}")
        if detail:
            lines.append(f"  detail: {detail}")
        all_ok = all_ok and ok
    lines.append("")
    lines.append(f"- final: {'PASS' if all_ok else 'FAIL'}")
    return all_ok, "\n".join(lines) + "\n"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Unified graph/auth replay entry.")
    parser.add_argument("--api-base", default=None)
    parser.add_argument("--frontend-base", default=None)
    parser.add_argument("--out-dir", default=None)
    parser.add_argument("--artifact-prefix", default=None)
    parser.add_argument("--timeout-seconds", type=int, default=None)
    parser.add_argument("--replay-manifest", default=None, help="JSON manifest for non-interactive replay inputs.")
    parser.add_argument("--admin-token", default=None)
    parser.add_argument("--admin-token-file", default=None)
    parser.add_argument("--user-token", default=None)
    parser.add_argument("--user-token-file", default=None)
    parser.add_argument(
        "--ui-source-dir",
        default=None,
        help="Directory containing 30/31/32 UI evidence files.",
    )
    parser.add_argument(
        "--skip-runtime",
        action="store_true",
        default=None,
        help="Skip L0 runtime checks (for controlled debugging only).",
    )
    parser.add_argument(
        "--runtime-prewarm-failed-reason",
        default=None,
        help="When provided, force L0 runtime failure with this prewarm reason.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    resolved_inputs, input_error = _resolve_runtime_inputs(args)

    default_out_dir = _env_str("artifacts", "WORLDLINE_QA_OUT_DIR")
    default_prefix = _env_str(DEFAULT_PREFIX, "WORLDLINE_QA_M2_PREFIX")
    out_root = Path(str(resolved_inputs.get("out_dir", default_out_dir) if resolved_inputs else default_out_dir)).resolve()
    out_root.mkdir(parents=True, exist_ok=True)
    run_dir = out_root / f"{(resolved_inputs.get('artifact_prefix', default_prefix) if resolved_inputs else default_prefix)}-{_utc_stamp()}"
    run_dir.mkdir(parents=True, exist_ok=True)

    metadata: dict[str, object] = {
        "contract_version": "graph-auth-replay-v1",
        "run_id": run_dir.name,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "exit_codes": {
            "success": EXIT_SUCCESS,
            "runtime_failed": EXIT_RUNTIME_FAILED,
            "api_failed": EXIT_API_FAILED,
            "ui_failed": EXIT_UI_FAILED,
            "summary_failed": EXIT_SUMMARY_FAILED,
            "precondition_failed": EXIT_PRECONDITION_FAILED,
        },
    }

    if input_error:
        metadata["inputs"] = {
            "replay_manifest": _first_non_empty(args.replay_manifest, _env_str("", "WORLDLINE_QA_REPLAY_MANIFEST")),
            "replay_manifest_source": "cli"
            if _first_non_empty(args.replay_manifest)
            else ("env" if _first_non_empty(_env_str("", "WORLDLINE_QA_REPLAY_MANIFEST")) else "default"),
        }
        return _finalize_precondition_failure(
            run_dir=run_dir,
            metadata=metadata,
            failure=input_error,
            main_blocker=_main_blocker(
                stage="precondition",
                code=input_error.code,
                kind=input_error.kind,
                message=input_error.message,
                details=input_error.details,
            ),
            summary_lines=[
                "# M2 Replay Summary",
                "",
                f"- [FAIL] precondition: {input_error.message}",
                f"- detail: {input_error.details.get('error', '')}",
                f"- sources_checked: {input_error.details.get('sources_checked', 'n/a')}",
                f"- main_blocker: precondition",
                f"- blocker_rule: {BLOCKER_RULE}",
            ],
        )

    api_base = str(resolved_inputs["api_base"])
    frontend_base = str(resolved_inputs["frontend_base"])
    timeout_seconds = int(resolved_inputs["timeout_seconds"])
    skip_runtime = bool(resolved_inputs["skip_runtime"])
    admin_token = str(resolved_inputs["admin_token"])
    user_token = str(resolved_inputs["user_token"])
    artifact_prefix = str(resolved_inputs["artifact_prefix"])

    metadata["inputs"] = {
        "replay_manifest": resolved_inputs["replay_manifest"],
        "replay_manifest_source": resolved_inputs["replay_manifest_source"],
        "api_base": api_base,
        "api_base_source": resolved_inputs["api_base_source"],
        "frontend_base": frontend_base,
        "frontend_base_source": resolved_inputs["frontend_base_source"],
        "out_dir": resolved_inputs["out_dir"],
        "out_dir_source": resolved_inputs["out_dir_source"],
        "artifact_prefix": artifact_prefix,
        "artifact_prefix_source": resolved_inputs["artifact_prefix_source"],
        "timeout_seconds": timeout_seconds,
        "timeout_source": resolved_inputs["timeout_source"],
        "has_admin_token": bool(admin_token),
        "has_user_token": bool(user_token),
        "admin_token_file": args.admin_token_file or "",
        "user_token_file": args.user_token_file or "",
        "admin_token_source": resolved_inputs["admin_token_source"],
        "user_token_source": resolved_inputs["user_token_source"],
        "ui_source_dir": str(resolved_inputs["ui_source_dir"]),
        "ui_source_dir_source": resolved_inputs["ui_source_dir_source"],
        "skip_runtime": skip_runtime,
        "skip_runtime_source": resolved_inputs["skip_runtime_source"],
        "runtime_prewarm_failed_reason": _first_non_empty(args.runtime_prewarm_failed_reason) or "",
    }

    if not str(resolved_inputs["ui_source_dir"]):
        failure = ReplayError(
            code=EXIT_PRECONDITION_FAILED,
            kind="ui_source_missing",
            message="missing ui evidence directory",
            details={"ui_source_dir": "", "error": "missing ui_source_dir"},
        )
        return _finalize_precondition_failure(
            run_dir=run_dir,
            metadata=metadata,
            failure=failure,
            main_blocker=_main_blocker(
                stage="precondition",
                code=failure.code,
                kind=failure.kind,
                message=failure.message,
                details=failure.details,
            ),
            summary_lines=[
                "# M2 Replay Summary",
                "",
                f"- [FAIL] precondition: {failure.message}",
                f"- detail: {failure.details['error']}",
                f"- sources_checked: {failure.details.get('sources_checked', 'n/a')}",
                f"- main_blocker: precondition",
                f"- blocker_rule: {BLOCKER_RULE}",
            ],
        )

    ui_source_dir = Path(str(resolved_inputs["ui_source_dir"])).resolve()
    if not ui_source_dir.exists():
        failure = ReplayError(
            code=EXIT_PRECONDITION_FAILED,
            kind="ui_source_missing",
            message="ui evidence directory does not exist",
            details={"ui_source_dir": str(ui_source_dir), "error": "ui_source_dir does not exist"},
        )
        return _finalize_precondition_failure(
            run_dir=run_dir,
            metadata=metadata,
            failure=failure,
            main_blocker=_main_blocker(
                stage="precondition",
                code=failure.code,
                kind=failure.kind,
                message=failure.message,
                details=failure.details,
            ),
            summary_lines=[
                "# M2 Replay Summary",
                "",
                f"- [FAIL] precondition: {failure.message}",
                f"- detail: {failure.details['error']}",
                "- main_blocker: precondition",
                f"- blocker_rule: {BLOCKER_RULE}",
            ],
        )
    if not ui_source_dir.is_dir():
        failure = ReplayError(
            code=EXIT_PRECONDITION_FAILED,
            kind="ui_source_invalid",
            message="ui evidence source is not a directory",
            details={"ui_source_dir": str(ui_source_dir), "error": "ui_source_dir is not a directory"},
        )
        return _finalize_precondition_failure(
            run_dir=run_dir,
            metadata=metadata,
            failure=failure,
            main_blocker=_main_blocker(
                stage="precondition",
                code=failure.code,
                kind=failure.kind,
                message=failure.message,
                details=failure.details,
            ),
            summary_lines=[
                "# M2 Replay Summary",
                "",
                f"- [FAIL] precondition: {failure.message}",
                f"- detail: {failure.details['error']}",
                "- main_blocker: precondition",
                f"- blocker_rule: {BLOCKER_RULE}",
            ],
        )

    stage_results: list[StageResult] = []
    runtime_prewarm_failed_reason = _first_non_empty(args.runtime_prewarm_failed_reason)
    if runtime_prewarm_failed_reason is not None:
        _write_text(
            run_dir / "10-runtime-health.txt",
            "\n".join(
                [
                    "# Runtime Health (L0)",
                    "",
                    "- [FAIL] runtime_prewarm",
                    f"  detail: {runtime_prewarm_failed_reason}",
                    "",
                    "- final: FAIL",
                ]
            )
            + "\n",
        )
        stage_results.append(StageResult("L0-runtime", False, f"prewarm failed: {runtime_prewarm_failed_reason}"))
        metadata["stages"] = [r.__dict__ for r in stage_results]
        metadata["main_blocker"] = _main_blocker(
            stage="L0-runtime",
            code=EXIT_RUNTIME_FAILED,
            kind="runtime_failed",
            message="runtime prewarm failed before runtime checks",
            details={"prewarm_error": runtime_prewarm_failed_reason},
        )
        metadata["final_exit_code"] = EXIT_RUNTIME_FAILED
        _write_json(run_dir / "00-run-metadata.json", metadata)
        _write_json(run_dir / "02-main-blocker.json", metadata["main_blocker"])
        _write_text(
            run_dir / "99-evidence-summary.md",
            "\n".join(
                [
                    "# M2 Replay Summary",
                    "",
                    "- [FAIL] L0 runtime prewarm",
                    f"- reason: {runtime_prewarm_failed_reason}",
                    "- main_blocker: L0-runtime",
                    f"- blocker_rule: {BLOCKER_RULE}",
                ]
            )
            + "\n",
        )
        print(f"[m2-replay] run_dir: {run_dir}")
        print(f"[m2-replay] exit_code: {EXIT_RUNTIME_FAILED}")
        return EXIT_RUNTIME_FAILED

    if not skip_runtime:
        runtime_ok, runtime_text = _build_runtime_report(api_base, timeout_seconds)
        _write_text(run_dir / "10-runtime-health.txt", runtime_text)
        stage_results.append(StageResult("L0-runtime", runtime_ok))
        if not runtime_ok:
            metadata["stages"] = [r.__dict__ for r in stage_results]
            metadata["main_blocker"] = _main_blocker(
                stage="L0-runtime",
                code=EXIT_RUNTIME_FAILED,
                kind="runtime_failed",
                message="runtime checks failed",
                details={"stage": "L0-runtime"},
            )
            metadata["final_exit_code"] = EXIT_RUNTIME_FAILED
            _write_json(run_dir / "00-run-metadata.json", metadata)
            _write_json(run_dir / "02-main-blocker.json", metadata["main_blocker"])
            _write_text(
                run_dir / "99-evidence-summary.md",
                "\n".join(
                    [
                        "# M2 Replay Summary",
                        "",
                        "- [FAIL] L0 runtime",
                        "- main_blocker: L0-runtime",
                        f"- blocker_rule: {BLOCKER_RULE}",
                    ]
                )
                + "\n",
            )
            print(f"[m2-replay] run_dir: {run_dir}")
            print(f"[m2-replay] exit_code: {EXIT_RUNTIME_FAILED}")
            return EXIT_RUNTIME_FAILED

    api_cmd = [
        sys.executable,
        "scripts/qa_graph_auth_readonly_check.py",
        "--api-base",
        api_base,
        "--frontend-base",
        frontend_base,
        "--output-dir",
        str(out_root),
        "--artifact-prefix",
        f"{artifact_prefix}-api",
        "--admin-token",
        admin_token,
        "--user-token",
        user_token,
        "--timeout",
        str(timeout_seconds),
    ]
    api_rc, api_stdout, api_stderr = _run_cmd(api_cmd)
    _write_text(run_dir / "11-api-run.log", api_stdout + ("\n" + api_stderr if api_stderr else ""))
    api_run_dir_str = _extract_run_dir(api_stdout)
    api_ok = api_rc == 0 and bool(api_run_dir_str)
    stage_results.append(StageResult("L1-api-matrix", api_ok, f"rc={api_rc}"))
    if not api_ok:
        metadata["stages"] = [r.__dict__ for r in stage_results]
        metadata["main_blocker"] = _main_blocker(
            stage="L1-api-matrix",
            code=EXIT_API_FAILED,
            kind="api_failed",
            message="readonly API matrix failed",
            details={"stage": "L1-api-matrix", "rc": str(api_rc)},
        )
        metadata["final_exit_code"] = EXIT_API_FAILED
        _write_json(run_dir / "00-run-metadata.json", metadata)
        _write_json(run_dir / "02-main-blocker.json", metadata["main_blocker"])
        _write_text(
            run_dir / "99-evidence-summary.md",
            "\n".join(
                [
                    "# M2 Replay Summary",
                    "",
                    "- [FAIL] L1 API matrix",
                    "- main_blocker: L1-api-matrix",
                    f"- blocker_rule: {BLOCKER_RULE}",
                ]
            )
            + "\n",
        )
        print(f"[m2-replay] run_dir: {run_dir}")
        print(f"[m2-replay] exit_code: {EXIT_API_FAILED}")
        return EXIT_API_FAILED

    api_run_dir = Path(api_run_dir_str).resolve()
    for name in [
        "20-api-matrix.json",
        "21-api-matrix.txt",
        "result.json",
        "result.txt",
        "run_config.json",
        "90-mcp-next-steps.md",
        "mcp_next_steps.md",
    ]:
        src = api_run_dir / name
        if src.exists():
            shutil.copy2(src, run_dir / name)

    missing_ui = [name for name in REQUIRED_UI_FILES if not (ui_source_dir / name).exists()]
    if missing_ui:
        stage_results.append(StageResult("L2-ui-guard", False, f"missing files: {', '.join(missing_ui)}"))
        metadata["stages"] = [r.__dict__ for r in stage_results]
        metadata["main_blocker"] = _main_blocker(
            stage="L2-ui-guard",
            code=EXIT_UI_FAILED,
            kind="ui_failed",
            message="missing required UI evidence files",
            details={"missing_files": ", ".join(missing_ui)},
        )
        metadata["final_exit_code"] = EXIT_UI_FAILED
        _write_json(run_dir / "00-run-metadata.json", metadata)
        _write_json(run_dir / "02-main-blocker.json", metadata["main_blocker"])
        _write_text(
            run_dir / "99-evidence-summary.md",
            "\n".join(
                [
                    "# M2 Replay Summary",
                    "",
                    "- [FAIL] L2 UI guard",
                    "- reason: missing required UI evidence files",
                    "- main_blocker: L2-ui-guard",
                    f"- blocker_rule: {BLOCKER_RULE}",
                ]
            )
            + "\n",
        )
        print(f"[m2-replay] run_dir: {run_dir}")
        print(f"[m2-replay] exit_code: {EXIT_UI_FAILED}")
        return EXIT_UI_FAILED

    for name in REQUIRED_UI_FILES:
        shutil.copy2(ui_source_dir / name, run_dir / name)

    ui_ok, ui_note = _validate_ui_assertion(run_dir / "32-ui-final-url-assertion.json")
    stage_results.append(StageResult("L2-ui-guard", ui_ok, ui_note))
    if not ui_ok:
        metadata["stages"] = [r.__dict__ for r in stage_results]
        metadata["main_blocker"] = _main_blocker(
            stage="L2-ui-guard",
            code=EXIT_UI_FAILED,
            kind="ui_failed",
            message="ui guard assertion failed",
            details={"assertion_file": "32-ui-final-url-assertion.json"},
        )
        metadata["final_exit_code"] = EXIT_UI_FAILED
        _write_json(run_dir / "00-run-metadata.json", metadata)
        _write_json(run_dir / "02-main-blocker.json", metadata["main_blocker"])
        _write_text(
            run_dir / "99-evidence-summary.md",
            "\n".join(
                [
                    "# M2 Replay Summary",
                    "",
                    "- [FAIL] L2 UI guard assertion",
                    "- main_blocker: L2-ui-guard",
                    f"- blocker_rule: {BLOCKER_RULE}",
                ]
            )
            + "\n",
        )
        print(f"[m2-replay] run_dir: {run_dir}")
        print(f"[m2-replay] exit_code: {EXIT_UI_FAILED}")
        return EXIT_UI_FAILED

    summary_lines = ["# M2 Replay Summary", ""]
    for stage in stage_results:
        summary_lines.append(f"- [{'PASS' if stage.ok else 'FAIL'}] {stage.name} {('- ' + stage.note) if stage.note else ''}")
    summary_lines.append("")
    summary_lines.append("- main_blocker: none")
    summary_lines.append(f"- blocker_rule: {BLOCKER_RULE}")
    summary_lines.append(f"- api_source_run_dir: `{api_run_dir}`")
    summary_lines.append(f"- ui_source_dir: `{ui_source_dir}`")
    summary_lines.append(f"- merged_output_dir: `{run_dir}`")
    summary_lines.append("- final: PASS")
    try:
        _write_text(run_dir / "99-evidence-summary.md", "\n".join(summary_lines) + "\n")
    except Exception:
        metadata["stages"] = [r.__dict__ for r in stage_results]
        metadata["main_blocker"] = _main_blocker(
            stage="summary",
            code=EXIT_SUMMARY_FAILED,
            kind="summary_failed",
            message="failed to write evidence summary",
            details={"summary_file": "99-evidence-summary.md"},
        )
        metadata["final_exit_code"] = EXIT_SUMMARY_FAILED
        _write_json(run_dir / "00-run-metadata.json", metadata)
        _write_json(run_dir / "02-main-blocker.json", metadata["main_blocker"])
        print(f"[m2-replay] run_dir: {run_dir}")
        print(f"[m2-replay] exit_code: {EXIT_SUMMARY_FAILED}")
        return EXIT_SUMMARY_FAILED

    metadata["stages"] = [r.__dict__ for r in stage_results]
    metadata["api_source_run_dir"] = str(api_run_dir)
    metadata["ui_source_dir"] = str(ui_source_dir)
    metadata["merged_output_dir"] = str(run_dir)
    metadata["main_blocker"] = None
    metadata["final_exit_code"] = EXIT_SUCCESS
    _write_json(run_dir / "00-run-metadata.json", metadata)
    _write_json(run_dir / "02-main-blocker.json", {"rule": BLOCKER_RULE, "main_blocker": None})

    print(f"[m2-replay] run_dir: {run_dir}")
    print(f"[m2-replay] exit_code: {EXIT_SUCCESS}")
    return EXIT_SUCCESS


if __name__ == "__main__":
    raise SystemExit(main())
