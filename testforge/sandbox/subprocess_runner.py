"""
Subprocess-based test runner — the fallback when Docker isn't available.

Runs tests in a subprocess on the host machine. Provides timeout protection
but NOT filesystem/network isolation. Suitable for development; use Docker
runner in production.
"""
from typing import Any

from testforge.tools.run_tests import run_tests


def run_in_subprocess(
    test_code: str,
    source_file: str,
    project_root: str | None = None,
    timeout: int = 30,
) -> dict[str, Any]:
    return run_tests(
        test_code=test_code,
        source_file=source_file,
        project_root=project_root,
    )
