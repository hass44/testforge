"""Structural correctness metrics for Python code analysis."""

from __future__ import annotations

import ast
import io
import tokenize
from dataclasses import dataclass


def ast_parse_ok(code: str) -> bool:
    try:
        ast.parse(code)
        return True
    except (SyntaxError, ValueError):
        return False


_OPEN = {")": "(", "]": "[", "}": "{"}


def bracket_balanced(code: str) -> bool:
    stack = []
    try:
        toks = tokenize.generate_tokens(io.StringIO(code).readline)
        for tok in toks:
            if tok.type != tokenize.OP:
                continue
            s = tok.string
            if s in "([{":
                stack.append(s)
            elif s in ")]}":
                if not stack or stack.pop() != _OPEN[s]:
                    return False
    except (tokenize.TokenError, IndentationError):
        return False
    return not stack


def indentation_ok(code: str) -> bool:
    uses_tab = uses_space = False
    for line in code.splitlines():
        stripped = line.lstrip(" \t")
        if not stripped:
            continue
        indent = line[: len(line) - len(stripped)]
        if "\t" in indent and " " in indent:
            return False
        if "\t" in indent:
            uses_tab = True
        elif " " in indent:
            uses_space = True
    return not (uses_tab and uses_space)


@dataclass
class LengthMatch:
    gen_mean: float
    ref_mean: float
    mean_ratio: float
    ks_statistic: float


def _ks_statistic(a: list[float], b: list[float]) -> float:
    if not a or not b:
        return 1.0
    sa, sb = sorted(a), sorted(b)
    vals = sorted(set(sa) | set(sb))

    def cdf(s, x):
        lo, hi = 0, len(s)
        while lo < hi:
            mid = (lo + hi) // 2
            if s[mid] <= x:
                lo = mid + 1
            else:
                hi = mid
        return lo / len(s)

    return max(abs(cdf(sa, v) - cdf(sb, v)) for v in vals)


def length_distribution_match(gen_lengths, ref_lengths) -> LengthMatch:
    gen = list(gen_lengths)
    ref = list(ref_lengths)
    gm = sum(gen) / len(gen) if gen else 0.0
    rm = sum(ref) / len(ref) if ref else 0.0
    return LengthMatch(
        gen_mean=gm,
        ref_mean=rm,
        mean_ratio=(gm / rm) if rm else 0.0,
        ks_statistic=_ks_statistic(gen, ref),
    )


def structural_metrics(code: str) -> dict:
    return {
        "ast_parse_ok": ast_parse_ok(code),
        "bracket_balanced": bracket_balanced(code),
        "indentation_ok": indentation_ok(code),
        "n_lines": len(code.splitlines()),
    }
