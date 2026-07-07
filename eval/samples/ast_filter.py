"""AST-validity filter for Python source files."""

from __future__ import annotations

import ast
from dataclasses import dataclass


def is_valid_python(source: str) -> bool:
    try:
        ast.parse(source)
        return True
    except (SyntaxError, ValueError, RecursionError, MemoryError):
        return False
    except Exception:
        return False


@dataclass
class FilterStats:
    seen: int = 0
    kept: int = 0
    dropped_empty: int = 0
    dropped_unparseable: int = 0
    dropped_too_short: int = 0

    @property
    def keep_rate(self) -> float:
        return self.kept / self.seen if self.seen else 0.0


def keep_file(source: str, min_chars: int = 32) -> bool:
    if not source or not source.strip():
        return False
    if len(source) < min_chars:
        return False
    return is_valid_python(source)


def filter_with_stats(sources, min_chars: int = 32, ast_check: bool = True):
    stats = FilterStats()

    def _gen():
        for src in sources:
            stats.seen += 1
            if not src or not src.strip():
                stats.dropped_empty += 1
                continue
            if len(src) < min_chars:
                stats.dropped_too_short += 1
                continue
            if ast_check and not is_valid_python(src):
                stats.dropped_unparseable += 1
                continue
            stats.kept += 1
            yield src

    return _gen(), stats
