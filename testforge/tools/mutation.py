"""
Mutation testing for generated test suites.

Runs mutmut against the source file using the generated tests.
Reports how many injected bugs the tests actually catch (kill rate).

On Windows, runs via WSL since mutmut requires a POSIX environment.
"""

import platform
import re
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

_PYTHON = sys.executable
_IS_WINDOWS = platform.system() == "Windows"


def run_mutation_tests(
    test_code: str,
    source_file: str,
    source_code: str | None = None,
    timeout: int = 120,
) -> dict[str, Any]:
    with tempfile.TemporaryDirectory(prefix="testforge_mut_") as tmp:
        tmp_path = Path(tmp)

        src_path = tmp_path / "source.py"
        if source_code:
            src_path.write_text(source_code, encoding="utf-8")
        else:
            src_path.write_text(
                Path(source_file).read_text(encoding="utf-8"),
                encoding="utf-8",
            )

        test_path = tmp_path / "test_source.py"
        test_code_fixed = test_code.replace(_find_import_module(test_code), "source")
        test_path.write_text(test_code_fixed, encoding="utf-8")

        setup_cfg = tmp_path / "setup.cfg"
        setup_cfg.write_text(
            "[mutmut]\nsource_paths=source.py\n",
            encoding="utf-8",
        )

        if _IS_WINDOWS:
            return _run_via_wsl(tmp_path, src_path, timeout)
        return _run_native(tmp_path, src_path, timeout)


def _wsl_path(win_path: Path) -> str:
    """Convert a Windows path to WSL /mnt/ path."""
    resolved = str(win_path.resolve()).replace("\\", "/")
    drive = resolved[0].lower()
    rest = resolved[2:]
    return f"/mnt/{drive}{rest}"


def _run_via_wsl(tmp_path: Path, src_path: Path, timeout: int) -> dict[str, Any]:
    wsl_tmp = _wsl_path(tmp_path)

    import uuid

    venv_id = uuid.uuid4().hex[:8]
    venv_dir = f"/tmp/tf_venv_{venv_id}"
    script = (
        f"python3 -m venv {venv_dir} && "
        f". {venv_dir}/bin/activate && "
        f"pip install mutmut pytest > /dev/null 2>&1 && "
        f"cd {wsl_tmp} && "
        f"python -m mutmut run 2>&1; "
        f"echo '---RESULTS---'; "
        f"python -m mutmut results 2>&1 || true; "
        f"rm -rf {venv_dir}"
    )

    try:
        proc = subprocess.run(
            ["wsl", "bash", "-c", script],
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
            encoding="utf-8",
            errors="replace",
        )
    except subprocess.TimeoutExpired:
        return _timeout_result(timeout)

    output = proc.stdout + proc.stderr
    run_stats = _parse_from_run_output(output)

    if "---RESULTS---" in output:
        results_section = output.split("---RESULTS---", 1)[1]
        results_parsed = _parse_results(results_section)
        survived = results_parsed["survived"]
        survivors = results_parsed["survivors"]
        if run_stats["total"] > 0:
            killed = run_stats["total"] - survived
            total = run_stats["total"]
        elif results_parsed["total"] > 0:
            killed = results_parsed["killed"]
            total = results_parsed["total"]
        else:
            return run_stats
        kill_rate = (killed / total * 100) if total > 0 else 0.0
        return {
            "killed": killed,
            "survived": survived,
            "total": total,
            "kill_rate": round(kill_rate, 1),
            "survivors": survivors,
        }

    return run_stats


def _run_native(tmp_path: Path, src_path: Path, timeout: int) -> dict[str, Any]:
    try:
        proc = subprocess.run(
            [_PYTHON, "-m", "mutmut", "run"],
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=str(tmp_path),
            check=False,
        )
    except subprocess.TimeoutExpired:
        return _timeout_result(timeout)

    try:
        results_proc = subprocess.run(
            [_PYTHON, "-m", "mutmut", "results"],
            capture_output=True,
            text=True,
            timeout=30,
            cwd=str(tmp_path),
            check=False,
        )
        return _parse_results(results_proc.stdout)
    except (subprocess.TimeoutExpired, Exception):
        return _parse_from_run_output(proc.stdout + proc.stderr)


def _timeout_result(timeout: int) -> dict[str, Any]:
    return {
        "killed": 0,
        "survived": 0,
        "total": 0,
        "kill_rate": 0.0,
        "survivors": [],
        "error": f"Mutation testing timed out after {timeout}s",
    }


def _find_import_module(test_code: str) -> str:
    match = re.search(r"from\s+([\w.]+)\s+import", test_code)
    if match:
        return match.group(1)
    match = re.search(r"import\s+([\w.]+)", test_code)
    if match:
        return match.group(1)
    return "module"


def _parse_results(output: str) -> dict[str, Any]:
    """Parse mutmut v3 results output (lines ending with ': survived' or ': killed')."""
    killed = 0
    survived = 0
    survivors = []

    for raw_line in output.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        lower = line.lower()
        if lower.endswith(": killed") or lower.startswith("killed"):
            killed += 1
        elif lower.endswith(": survived") or lower.startswith("survived"):
            survived += 1
            survivors.append(line)

    total = killed + survived
    kill_rate = (killed / total * 100) if total > 0 else 0.0

    return {
        "killed": killed,
        "survived": survived,
        "total": total,
        "kill_rate": round(kill_rate, 1),
        "survivors": survivors[:10],
    }


def _parse_from_run_output(output: str) -> dict[str, Any]:
    """Parse stats from mutmut run progress output."""
    killed = 0
    survived = 0
    total = 0

    for m in re.finditer(r"(\d+)/(\d+)", output):
        done = int(m.group(1))
        t = int(m.group(2))
        if t > total:
            total = t
            killed = done

    m = re.search(r"(\d+)\s+killed", output, re.IGNORECASE)
    if m:
        killed = int(m.group(1))

    m = re.search(r"(\d+)\s+survived", output, re.IGNORECASE)
    if m:
        survived = int(m.group(1))

    if total > 0 and survived == 0:
        survived = total - killed

    kill_rate = (killed / total * 100) if total > 0 else 0.0

    return {
        "killed": killed,
        "survived": survived,
        "total": total,
        "kill_rate": round(kill_rate, 1),
        "survivors": [],
    }
