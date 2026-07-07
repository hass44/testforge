"""
Structured logging for TestForge agent runs.

Provides per-iteration traces: which strategy was used, how long
the LLM call took, what the test results were, and what decision
the agent made. Each run binds a unique run_id so logs from
concurrent runs can be filtered apart.
"""

import time
import uuid

import structlog

_configured = False


def configure_logging(json_output: bool = True) -> None:
    """
    Set up structlog processors once.

    json_output=True  → machine-readable JSON lines (production / files)
    json_output=False → human-readable colored console output (development)
    """
    global _configured
    if _configured:
        return

    if json_output:
        renderer = structlog.processors.JSONRenderer()
    else:
        renderer = structlog.dev.ConsoleRenderer()

    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            renderer,
        ],
        wrapper_class=structlog.make_filtering_bound_logger(0),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=True,
    )
    _configured = True


def get_logger(name: str) -> structlog.stdlib.BoundLogger:
    configure_logging(json_output=False)
    return structlog.get_logger(name)


class AgentTimer:
    """Context manager that measures elapsed time for a block."""

    def __init__(self):
        self.elapsed: float = 0.0

    def __enter__(self):
        self._start = time.perf_counter()
        return self

    def __exit__(self, *args):
        self.elapsed = round(time.perf_counter() - self._start, 2)


def new_run_id() -> str:
    return uuid.uuid4().hex[:8]
