"""
Docker-based sandboxed test runner.

Runs generated tests inside a locked-down container:
- No network access (--network=none)
- Memory capped (--memory=512m)
- CPU capped (--cpus=1)
- Timeout enforced (killed after N seconds)
- Ephemeral filesystem (--rm)

The container receives source + test files via a bind-mounted temp dir,
runs pytest+coverage inside, and prints a JSON result to stdout.
"""

import json
import subprocess
import tempfile
from pathlib import Path
from typing import Any

_IMAGE = "testforge-sandbox"
_TIMEOUT = 45
_MEMORY = "512m"
_CPUS = "1"

_RUNNER_SCRIPT = """\
import json
import subprocess
import sys
from pathlib import Path

test_file = Path("/workspace/test_generated.py")
source_file = Path("/workspace/source.py")

proc = subprocess.run(
    [sys.executable, "-m", "coverage", "run",
     "--data-file", "/workspace/.coverage",
     "--include", str(source_file),
     "-m", "pytest", str(test_file),
     "-v", "--tb=short", "--no-header"],
    capture_output=True, text=True, timeout=30,
    cwd="/workspace",
)

test_output = proc.stdout + proc.stderr

import re
num_passed = int(m.group(1)) if (m := re.search(r"(\\d+) passed", test_output)) else 0
num_failed = int(m.group(1)) if (m := re.search(r"(\\d+) failed", test_output)) else 0
num_errors = int(m.group(1)) if (m := re.search(r"(\\d+) error", test_output)) else 0
passed = num_failed == 0 and num_errors == 0 and num_passed > 0

traceback = ""
if not passed:
    lines = test_output.splitlines()
    for i, line in enumerate(lines):
        if "FAILED" in line or "ERROR" in line:
            traceback = "\\n".join(lines[max(0, i-3):])
            break
    if not traceback:
        traceback = test_output[-2000:]

# Generate coverage JSON
subprocess.run(
    [sys.executable, "-m", "coverage", "json",
     "--data-file", "/workspace/.coverage",
     "-o", "/workspace/coverage.json"],
    capture_output=True, text=True, timeout=10,
)

coverage_pct = 0.0
uncovered_lines = []
cov_path = Path("/workspace/coverage.json")
if cov_path.exists():
    data = json.loads(cov_path.read_text())
    for key, file_data in data.get("files", {}).items():
        summary = file_data.get("summary", {})
        coverage_pct = summary.get("percent_covered", 0.0)
        uncovered_lines = sorted(file_data.get("missing_lines", []))
        break

result = {
    "passed": passed,
    "num_passed": num_passed,
    "num_failed": num_failed,
    "num_errors": num_errors,
    "traceback": traceback,
    "coverage_pct": round(coverage_pct, 1),
    "uncovered_lines": uncovered_lines,
}
print(json.dumps(result))
"""


def is_docker_available() -> bool:
    try:
        proc = subprocess.run(
            ["docker", "info"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        return proc.returncode == 0
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False


def is_image_built() -> bool:
    try:
        proc = subprocess.run(
            ["docker", "image", "inspect", _IMAGE],
            capture_output=True,
            text=True,
            timeout=5,
        )
        return proc.returncode == 0
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False


def build_image() -> None:
    dockerfile = (
        "FROM python:3.11-slim\n"
        "RUN pip install --no-cache-dir pytest coverage\n"
        "WORKDIR /workspace\n"
    )
    with tempfile.TemporaryDirectory() as tmp:
        df_path = Path(tmp) / "Dockerfile"
        df_path.write_text(dockerfile)
        subprocess.run(
            ["docker", "build", "-t", _IMAGE, "-f", str(df_path), tmp],
            check=True,
            capture_output=True,
            text=True,
            timeout=120,
        )


def run_in_docker(
    test_code: str,
    source_code: str,
    timeout: int = _TIMEOUT,
) -> dict[str, Any]:
    if not is_image_built():
        build_image()

    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp = Path(tmp_dir)

        (tmp / "source.py").write_text(source_code, encoding="utf-8")
        (tmp / "test_generated.py").write_text(test_code, encoding="utf-8")
        (tmp / "runner.py").write_text(_RUNNER_SCRIPT, encoding="utf-8")

        docker_cmd = [
            "docker",
            "run",
            "--rm",
            "--network=none",
            f"--memory={_MEMORY}",
            f"--cpus={_CPUS}",
            "-v",
            f"{tmp}:/workspace",
            _IMAGE,
            "python",
            "/workspace/runner.py",
        ]

        try:
            proc = subprocess.run(
                docker_cmd,
                capture_output=True,
                text=True,
                timeout=timeout,
            )
        except subprocess.TimeoutExpired:
            return {
                "passed": False,
                "num_passed": 0,
                "num_failed": 0,
                "num_errors": 0,
                "traceback": f"Docker execution timed out after {timeout}s",
                "coverage_pct": 0.0,
                "uncovered_lines": [],
            }

        if proc.returncode != 0 and not proc.stdout.strip():
            return {
                "passed": False,
                "num_passed": 0,
                "num_failed": 0,
                "num_errors": 0,
                "traceback": f"Docker container error:\n{proc.stderr[-2000:]}",
                "coverage_pct": 0.0,
                "uncovered_lines": [],
            }

        try:
            output_lines = proc.stdout.strip().splitlines()
            result = json.loads(output_lines[-1])
            return result
        except (json.JSONDecodeError, IndexError):
            return {
                "passed": False,
                "num_passed": 0,
                "num_failed": 0,
                "num_errors": 0,
                "traceback": (
                    f"Failed to parse output:\n"
                    f"{proc.stdout[-1000:]}\n"
                    f"{proc.stderr[-1000:]}"
                ),
                "coverage_pct": 0.0,
                "uncovered_lines": [],
            }
