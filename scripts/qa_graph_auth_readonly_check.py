#!/usr/bin/env python3
"""
Read-only QA acceptance helper for graph/auth checks.

Design goals:
- Default read-only: only GET requests.
- Never create or modify business data.
- Persist status code and key URL evidence to artifacts/.
- Emit an M1-compatible evidence package while keeping legacy outputs.
- Provide MCP execution hints for manual browser verification.
"""

from __future__ import annotations

import argparse
import json
import os
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable
from urllib import error, request

PACKAGE_PREFIX = "qa-phase4-m1-baseline"
LEGACY_PREFIX = "qa-readonly-graph-auth"
CONTRACT_VERSION = "phase4-m1"
EXIT_SUCCESS = 0
EXIT_FAILURE = 2

TRUE_VALUES = {"1", "true", "yes", "on"}


@dataclass
class CheckResult:
    name: str
    method: str
    url: str
    expected: str
    status_code: int | None
    ok: bool
    note: str = ""
    error: str = ""
    body_preview: str = ""


def _utc_stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")


def _safe_preview(content: bytes, limit: int = 240) -> str:
    try:
        text = content.decode("utf-8", errors="replace")
    except Exception:
        return ""
    return text[:limit].replace("\r", " ").replace("\n", " ")


def _http_get(url: str, headers: dict[str, str], timeout: int) -> tuple[int | None, str, str]:
    req = request.Request(url=url, method="GET", headers=headers)
    try:
        with request.urlopen(req, timeout=timeout) as resp:
            body = resp.read()
            return resp.status, _safe_preview(body), ""
    except error.HTTPError as exc:
        payload = exc.read() if exc.fp else b""
        return exc.code, _safe_preview(payload), ""
    except Exception as exc:  # pragma: no cover
        return None, "", str(exc)


def _build_headers(token: str | None) -> dict[str, str]:
    if not token:
        return {}
    return {"Authorization": f"Bearer {token}"}


def _bool_status(value: bool) -> str:
    return "yes" if value else "no"


def _status_label(ok: bool) -> str:
    return "PASS" if ok else "FAIL"


def _env_str(default: str, *names: str) -> str:
    for name in names:
        value = os.getenv(name)
        if value is not None:
            value = value.strip()
            if value:
                return value
    return default


def _env_int(default: int, *names: str) -> int:
    for name in names:
        value = os.getenv(name)
        if value is None:
            continue
        value = value.strip()
        if not value:
            continue
        try:
            return int(value)
        except ValueError as exc:
            raise ValueError(f"Invalid integer value for {name}: {value}") from exc
    return default


def _env_bool(default: bool, *names: str) -> bool:
    for name in names:
        value = os.getenv(name)
        if value is None:
            continue
        normalized = value.strip().lower()
        if not normalized:
            continue
        return normalized in TRUE_VALUES
    return default


def _check(
    *,
    name: str,
    url: str,
    token: str | None,
    timeout: int,
    expected_codes: Iterable[int],
    expected_desc: str,
    note: str = "",
) -> CheckResult:
    status_code, preview, err = _http_get(url=url, headers=_build_headers(token), timeout=timeout)
    ok = status_code in set(expected_codes)
    return CheckResult(
        name=name,
        method="GET",
        url=url,
        expected=expected_desc,
        status_code=status_code,
        ok=ok,
        note=note,
        error=err,
        body_preview=preview,
    )


def _build_api_matrix(results: list[CheckResult]) -> dict:
    return {
        "contract_version": CONTRACT_VERSION,
        "pass_count": sum(1 for item in results if item.ok),
        "fail_count": sum(1 for item in results if not item.ok),
        "checks": [asdict(item) for item in results],
    }


def _write_text_report(path: Path, results: list[CheckResult], key_urls: list[str]) -> None:
    lines = []
    lines.append("# QA Read-Only Graph/Auth Report")
    lines.append("")
    lines.append("## Key URLs")
    for url in key_urls:
        lines.append(f"- {url}")
    lines.append("")
    lines.append("## Checks")
    for item in results:
        lines.append(
            f"- [{'PASS' if item.ok else 'FAIL'}] {item.name} | {item.method} {item.url} | "
            f"status={item.status_code} | expected={item.expected}"
        )
        if item.note:
            lines.append(f"  note: {item.note}")
        if item.error:
            lines.append(f"  error: {item.error}")
        if item.body_preview:
            lines.append(f"  body: {item.body_preview}")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _write_api_matrix_txt(path: Path, results: list[CheckResult]) -> None:
    lines = []
    lines.append("# API Matrix")
    lines.append("")
    lines.append("| Name | Method | URL | Expected | Status | Result |")
    lines.append("| --- | --- | --- | --- | --- | --- |")
    for item in results:
        lines.append(
            f"| {item.name} | {item.method} | {item.url} | {item.expected} | {item.status_code} | {_status_label(item.ok)} |"
        )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _write_run_metadata(
    path: Path,
    *,
    run_dir: Path,
    package_prefix: str,
    api_base: str,
    frontend_base: str,
    key_urls: list[str],
    args: argparse.Namespace,
) -> None:
    payload = {
        "contract_version": CONTRACT_VERSION,
        "package_prefix": package_prefix,
        "legacy_prefix": LEGACY_PREFIX,
        "exit_codes": {"success": EXIT_SUCCESS, "failure": EXIT_FAILURE},
        "run_id": run_dir.name,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "readonly_mode": True,
        "self_check": bool(args.self_check),
        "api_base": api_base,
        "frontend_base": frontend_base,
        "key_urls": key_urls,
        "inputs": {
            "timeout_seconds": args.timeout_seconds,
            "has_admin_token": bool(args.admin_token),
            "has_user_token": bool(args.user_token),
            "allow_temp_user": bool(args.allow_temp_user),
        },
        "artifact_contract": {
            "runtime": "generated by controller shell or runtime probe",
            "api": "generated by this read-only checker",
            "ui": "may be inherited or refreshed by controller Playwright run",
            "summary": "generated by this read-only checker",
        },
        "note": "No create/update/delete API is called in this script.",
    }
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def _write_summary_md(path: Path, results: list[CheckResult], run_dir: Path) -> None:
    lines = []
    lines.append("# M1 Read-Only QA Evidence Summary")
    lines.append("")
    lines.append(f"- package: `{run_dir.name}`")
    lines.append(f"- contract: `{CONTRACT_VERSION}`")
    lines.append(f"- pass_count: {sum(1 for item in results if item.ok)}")
    lines.append(f"- fail_count: {sum(1 for item in results if not item.ok)}")
    lines.append(f"- readonly: `{_bool_status(True)}`")
    lines.append("")
    lines.append("## Checks")
    for item in results:
        lines.append(
            f"- [{_status_label(item.ok)}] {item.name} | {item.method} {item.url} | status={item.status_code} | expected={item.expected}"
        )
    lines.append("")
    lines.append("## Compatibility")
    lines.append("- Legacy compatibility files remain available: `result.json`, `result.txt`, `run_config.json`, `mcp_next_steps.md`.")
    lines.append("- This package is read-only and does not create, update, or delete business data.")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _write_mcp_steps(path: Path, api_base: str, frontend_base: str) -> None:
    content = f"""# MCP suggested steps (manual)

This script only runs read-only API checks. Use MCP Playwright to verify UI guard behavior:
1. Open `{frontend_base}/login` and sign in with a QA account that has `role=user`.
2. Navigate directly to `{frontend_base}/graph`.
3. Expected: frontend guard redirects to `/agent` or `/agent/{{agent_id}}`.
4. In Network panel, filter `api/graph` and confirm no successful admin-only graph access.
5. If unexpected behavior appears (for example `role=user` gets `200`), capture URL, status code, and response summary.

Key backend URLs:
- {api_base}/api/auth/me
- {api_base}/api/graph/list
- {api_base}/api/graph/neo4j/info
"""
    path.write_text(content, encoding="utf-8")


def run(args: argparse.Namespace) -> int:
    if args.allow_temp_user:
        print("[WARN] --allow-temp-user is enabled, but this script still runs read-only checks only.")

    out_root = Path(args.out_dir).resolve()
    out_root.mkdir(parents=True, exist_ok=True)
    package_prefix = args.package_prefix.strip() or PACKAGE_PREFIX
    run_dir = out_root / f"{package_prefix}-{_utc_stamp()}"
    run_dir.mkdir(parents=True, exist_ok=True)

    api_base = args.api_base.rstrip("/")
    frontend_base = args.frontend_base.rstrip("/")

    key_urls = [
        f"{api_base}/api/system/health",
        f"{api_base}/api/graph/list",
        f"{api_base}/api/graph/neo4j/info",
        f"{frontend_base}/graph",
    ]

    if args.self_check:
        results = [
            CheckResult(
                name="self_check_artifact_write",
                method="LOCAL",
                url=str(run_dir),
                expected="local file writes succeed",
                status_code=0,
                ok=True,
                note="Self-check mode skips network requests.",
            )
        ]
    else:
        results: list[CheckResult] = []
        timeout = args.timeout_seconds

        results.append(
            _check(
                name="anonymous_health",
                url=f"{api_base}/api/system/health",
                token=None,
                timeout=timeout,
                expected_codes=(200,),
                expected_desc="200",
            )
        )
        results.append(
            _check(
                name="anonymous_graph_list",
                url=f"{api_base}/api/graph/list",
                token=None,
                timeout=timeout,
                expected_codes=(401,),
                expected_desc="401",
            )
        )
        results.append(
            _check(
                name="anonymous_graph_neo4j_info",
                url=f"{api_base}/api/graph/neo4j/info",
                token=None,
                timeout=timeout,
                expected_codes=(401,),
                expected_desc="401",
            )
        )

        if args.user_token:
            results.append(
                _check(
                    name="user_token_graph_list_negative",
                    url=f"{api_base}/api/graph/list",
                    token=args.user_token,
                    timeout=timeout,
                    expected_codes=(403,),
                    expected_desc="403",
                    note="role=user negative path.",
                )
            )
            results.append(
                _check(
                    name="user_token_graph_neo4j_info_negative",
                    url=f"{api_base}/api/graph/neo4j/info",
                    token=args.user_token,
                    timeout=timeout,
                    expected_codes=(403,),
                    expected_desc="403",
                    note="role=user negative path.",
                )
            )

        if args.admin_token:
            results.append(
                _check(
                    name="admin_token_graph_list_positive",
                    url=f"{api_base}/api/graph/list",
                    token=args.admin_token,
                    timeout=timeout,
                    expected_codes=(200,),
                    expected_desc="200",
                    note="admin positive path.",
                )
            )
            results.append(
                _check(
                    name="admin_token_graph_neo4j_info_positive",
                    url=f"{api_base}/api/graph/neo4j/info",
                    token=args.admin_token,
                    timeout=timeout,
                    expected_codes=(200,),
                    expected_desc="200",
                    note="admin positive path.",
                )
            )

    report_json = run_dir / "result.json"
    report_txt = run_dir / "result.txt"
    mcp_steps = run_dir / "mcp_next_steps.md"
    mcp_steps_90 = run_dir / "90-mcp-next-steps.md"
    config_json = run_dir / "run_config.json"
    run_metadata_json = run_dir / "00-run-metadata.json"
    api_matrix_json = run_dir / "20-api-matrix.json"
    api_matrix_txt = run_dir / "21-api-matrix.txt"
    summary_md = run_dir / "99-evidence-summary.md"

    api_matrix = _build_api_matrix(results)
    report_json.write_text(
        json.dumps(
            {
                "run_id": run_dir.name,
                "generated_at_utc": datetime.now(timezone.utc).isoformat(),
                "readonly_mode": True,
                "contract_version": CONTRACT_VERSION,
                "self_check": bool(args.self_check),
                "key_urls": key_urls,
                "checks": api_matrix["checks"],
                "pass_count": api_matrix["pass_count"],
                "fail_count": api_matrix["fail_count"],
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    _write_text_report(report_txt, results, key_urls)
    _write_run_metadata(
        run_metadata_json,
        run_dir=run_dir,
        package_prefix=package_prefix,
        api_base=api_base,
        frontend_base=frontend_base,
        key_urls=key_urls,
        args=args,
    )
    api_matrix_json.write_text(json.dumps(api_matrix, ensure_ascii=False, indent=2), encoding="utf-8")
    _write_api_matrix_txt(api_matrix_txt, results)
    _write_mcp_steps(mcp_steps, api_base, frontend_base)
    _write_mcp_steps(mcp_steps_90, api_base, frontend_base)
    _write_summary_md(summary_md, results, run_dir)
    config_json.write_text(
        json.dumps(
            {
                "contract_version": CONTRACT_VERSION,
                "package_prefix": package_prefix,
                "api_base": api_base,
                "frontend_base": frontend_base,
                "out_dir": str(run_dir),
                "timeout_seconds": args.timeout_seconds,
                "has_admin_token": bool(args.admin_token),
                "has_user_token": bool(args.user_token),
                "allow_temp_user": bool(args.allow_temp_user),
                "self_check": bool(args.self_check),
                "note": "No create/update/delete API is called in this script.",
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    print(f"[qa-readonly] run_dir: {run_dir}")
    print(f"[qa-readonly] report: {report_json}")
    print(f"[qa-readonly] text: {report_txt}")
    print(f"[qa-readonly] run_metadata: {run_metadata_json}")
    print(f"[qa-readonly] api_matrix: {api_matrix_json}")
    print(f"[qa-readonly] api_matrix_txt: {api_matrix_txt}")
    print(f"[qa-readonly] mcp: {mcp_steps}")
    print(f"[qa-readonly] mcp_90: {mcp_steps_90}")
    print(f"[qa-readonly] summary: {summary_md}")

    failed = [item for item in results if not item.ok]
    if failed:
        print(f"[qa-readonly] done with failures: {len(failed)}")
        for item in failed:
            print(f"  - {item.name}: got={item.status_code}, expected={item.expected}")
        print(f"[qa-readonly] exit_code: {EXIT_FAILURE}")
        return EXIT_FAILURE

    print("[qa-readonly] done, all checks passed")
    print(f"[qa-readonly] exit_code: {EXIT_SUCCESS}")
    return EXIT_SUCCESS


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Worldline graph/auth read-only acceptance checker (no business data writes)."
    )
    parser.add_argument(
        "--api-base",
        default=_env_str("http://127.0.0.1:5050", "WORLDLINE_QA_API_BASE", "WORLDLINE_API_BASE"),
    )
    parser.add_argument(
        "--frontend-base",
        default=_env_str("http://127.0.0.1:5173", "WORLDLINE_QA_FRONTEND_BASE", "WORLDLINE_FRONTEND_BASE"),
    )
    parser.add_argument(
        "--out-dir",
        "--output-dir",
        dest="out_dir",
        default=_env_str("artifacts", "WORLDLINE_QA_OUT_DIR", "WORLDLINE_QA_ARTIFACT_DIR"),
    )
    parser.add_argument(
        "--package-prefix",
        "--artifact-prefix",
        dest="package_prefix",
        default=_env_str(PACKAGE_PREFIX, "WORLDLINE_QA_PACKAGE_PREFIX", "WORLDLINE_QA_PREFIX"),
    )
    parser.add_argument(
        "--timeout-seconds",
        "--timeout",
        dest="timeout_seconds",
        type=int,
        default=_env_int(12, "WORLDLINE_QA_TIMEOUT_SECONDS", "WORLDLINE_QA_TIMEOUT"),
    )
    parser.add_argument(
        "--admin-token",
        default=_env_str("", "WORLDLINE_QA_ADMIN_TOKEN", "WORLDLINE_ADMIN_TOKEN"),
    )
    parser.add_argument(
        "--user-token",
        default=_env_str("", "WORLDLINE_QA_USER_TOKEN", "WORLDLINE_USER_TOKEN"),
    )
    parser.add_argument(
        "--allow-temp-user",
        action="store_true",
        default=_env_bool(False, "WORLDLINE_QA_ALLOW_TEMP_USER"),
        help="Disabled-by-default risk switch. Reserved for future non-readonly extensions.",
    )
    parser.add_argument(
        "--self-check",
        action="store_true",
        default=_env_bool(False, "WORLDLINE_QA_SELF_CHECK"),
        help="Do not call network; only validate artifact generation path.",
    )
    return parser.parse_args()


if __name__ == "__main__":
    raise SystemExit(run(parse_args()))
