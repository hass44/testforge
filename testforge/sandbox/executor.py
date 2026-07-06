"""
Unified test execution interface.

Tries Docker (full isolation) first. Falls back to subprocess (timeout only)
if Docker is unavailable.
"""
import logging
from typing import Any

from testforge.sandbox.docker_runner import is_docker_available, run_in_docker
from testforge.sandbox.subprocess_runner import run_in_subprocess

logger = logging.getLogger(__name__)

_docker_checked = False
_docker_available = False


def execute_tests(
    test_code: str,
    source_file: str,
    source_code: str | None = None,
    project_root: str | None = None,
    use_docker: bool | None = None,
) -> dict[str, Any]:
    """
    Run generated tests and return structured results.

    Automatically selects Docker (sandboxed) or subprocess (fallback).
    Override with use_docker=True/False to force a backend.
    """
    should_use_docker = _should_use_docker(use_docker)

    if should_use_docker:
        if source_code is None:
            with open(source_file, encoding="utf-8") as f:
                source_code = f.read()
        logger.info("Running tests in Docker sandbox")
        return run_in_docker(test_code=test_code, source_code=source_code)
    else:
        logger.info("Running tests in subprocess (no Docker)")
        return run_in_subprocess(
            test_code=test_code,
            source_file=source_file,
            project_root=project_root,
        )


def _should_use_docker(override: bool | None) -> bool:
    if override is not None:
        return override

    global _docker_checked, _docker_available
    if not _docker_checked:
        _docker_available = is_docker_available()
        _docker_checked = True
        if _docker_available:
            logger.info("Docker detected — using sandboxed execution")
        else:
            logger.info("Docker not available — falling back to subprocess")

    return _docker_available
