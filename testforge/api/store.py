"""
In-memory run store — tracks agent jobs by run ID.

Each entry:
  {
    "status": "running" | "passed" | "failed" | "error",
    "file_path": str,
    "result": { ... } | None,    # final agent result, set when done
    "error_msg": str | None,     # set only if status == "error"
    "created_at": float,         # timestamp
  }

Not persistent — restarts lose all runs. Fine for v1 demo.
"""

import time
import uuid
from typing import Any

_runs: dict[str, dict[str, Any]] = {}


def create_run(file_path: str) -> str:
    run_id = uuid.uuid4().hex[:12]
    _runs[run_id] = {
        "status": "running",
        "file_path": file_path,
        "result": None,
        "error_msg": None,
        "created_at": time.time(),
    }
    return run_id


def complete_run(run_id: str, final_state: dict[str, Any]) -> None:
    if run_id not in _runs:
        return
    result = final_state.get("test_result", {})
    coverage_target = final_state.get("coverage_target", 80.0)
    cov = result.get("coverage_pct", 0)
    passed = result.get("passed", False) and cov >= coverage_target

    _runs[run_id]["status"] = "passed" if passed else "failed"
    _runs[run_id]["result"] = {
        "iterations": final_state.get("iteration", 0),
        "strategy": final_state.get("strategy", ""),
        "num_passed": result.get("num_passed", 0),
        "num_failed": result.get("num_failed", 0),
        "num_errors": result.get("num_errors", 0),
        "coverage_pct": result.get("coverage_pct", 0.0),
        "uncovered_lines": result.get("uncovered_lines", []),
        "test_code": final_state.get("test_code", ""),
    }


def fail_run(run_id: str, error_msg: str) -> None:
    if run_id not in _runs:
        return
    _runs[run_id]["status"] = "error"
    _runs[run_id]["error_msg"] = error_msg


def get_run(run_id: str) -> dict[str, Any] | None:
    return _runs.get(run_id)


def list_runs() -> dict[str, dict[str, Any]]:
    return dict(_runs)
