import json
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

_TIMEOUT = 30
_PYTHON = sys.executable


def run_tests(
    test_code: str,
    source_file: str,
    project_root: str | None = None,
) -> dict[str, Any]:
    root = Path(project_root) if project_root else Path.cwd()
    source_path = Path(source_file).resolve()

    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp = Path(tmp_dir)

        test_file = tmp / "test_generated.py"
        test_file.write_text(test_code, encoding="utf-8")

        result = _run_pytest_with_coverage(
            test_file=test_file,
            source_path=source_path,
            project_root=root,
            cov_dir=tmp,
        )

    return result


def _run_pytest_with_coverage(
    test_file: Path,
    source_path: Path,
    project_root: Path,
    cov_dir: Path,
) -> dict[str, Any]:
    cov_data_file = cov_dir / ".coverage"
    cov_json_file = cov_dir / "coverage.json"

    pytest_cmd = [
        _PYTHON, "-m", "coverage", "run",
        "--data-file", str(cov_data_file),
        "--include", str(source_path),
        "-m", "pytest", str(test_file),
        "-v", "--tb=short", "--no-header",
    ]

    try:
        proc = subprocess.run(
            pytest_cmd,
            capture_output=True,
            text=True,
            timeout=_TIMEOUT,
            cwd=str(project_root),
        )
    except subprocess.TimeoutExpired:
        return {
            "passed": False,
            "num_passed": 0,
            "num_failed": 0,
            "num_errors": 0,
            "traceback": f"Test execution timed out after {_TIMEOUT}s",
            "coverage_pct": 0.0,
            "uncovered_lines": [],
        }

    test_output = proc.stdout + proc.stderr
    passed, num_passed, num_failed, num_errors = _parse_pytest_summary(test_output)
    traceback = _extract_traceback(test_output) if not passed else ""

    coverage_pct, uncovered_lines = _get_coverage(
        cov_data_file, cov_json_file, source_path
    )

    return {
        "passed": passed,
        "num_passed": num_passed,
        "num_failed": num_failed,
        "num_errors": num_errors,
        "traceback": traceback,
        "coverage_pct": coverage_pct,
        "uncovered_lines": uncovered_lines,
    }


def _parse_pytest_summary(output: str) -> tuple[bool, int, int, int]:
    import re

    num_passed = 0
    num_failed = 0
    num_errors = 0

    match = re.search(r"(\d+) passed", output)
    if match:
        num_passed = int(match.group(1))

    match = re.search(r"(\d+) failed", output)
    if match:
        num_failed = int(match.group(1))

    match = re.search(r"(\d+) error", output)
    if match:
        num_errors = int(match.group(1))

    passed = num_failed == 0 and num_errors == 0 and num_passed > 0
    return passed, num_passed, num_failed, num_errors


def _extract_traceback(output: str) -> str:
    lines = output.splitlines()
    tb_lines: list[str] = []
    capturing = False

    for line in lines:
        if line.startswith("FAILED") or line.startswith("ERROR") or "ERRORS" in line:
            capturing = True
        if capturing:
            tb_lines.append(line)
        if capturing and line.startswith("=") and "short test summary" in line:
            capturing = False

    if tb_lines:
        return "\n".join(tb_lines)

    for i, line in enumerate(lines):
        if "FAILED" in line or "Error" in line:
            start = max(0, i - 5)
            return "\n".join(lines[start:])

    return output[-2000:] if len(output) > 2000 else output


def _get_coverage(
    cov_data_file: Path,
    cov_json_file: Path,
    source_path: Path,
) -> tuple[float, list[int]]:
    if not cov_data_file.exists():
        return 0.0, []

    try:
        json_cmd = [
            _PYTHON, "-m", "coverage", "json",
            "--data-file", str(cov_data_file),
            "-o", str(cov_json_file),
        ]
        subprocess.run(json_cmd, capture_output=True, text=True, timeout=10)
    except (subprocess.TimeoutExpired, subprocess.CalledProcessError):
        return 0.0, []

    if not cov_json_file.exists():
        return 0.0, []

    try:
        data = json.loads(cov_json_file.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return 0.0, []

    source_key = _find_source_key(data, source_path)
    if not source_key:
        return 0.0, []

    file_data = data["files"][source_key]
    summary = file_data.get("summary", {})
    coverage_pct = summary.get("percent_covered", 0.0)
    missing = file_data.get("missing_lines", [])

    return round(coverage_pct, 1), sorted(missing)


def _find_source_key(data: dict, source_path: Path) -> str | None:
    resolved = str(source_path.resolve())
    for key in data.get("files", {}):
        if Path(key).resolve() == source_path.resolve():
            return key
        if resolved.endswith(key) or key.endswith(str(source_path)):
            return key
    return None
