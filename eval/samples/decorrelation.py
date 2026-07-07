"""Quantify error-independence between actor and critic agents."""

from __future__ import annotations

import math


def _phi(a: list[bool], b: list[bool]) -> float:
    n = len(a)
    if n == 0 or len(b) != n:
        return float("nan")
    n11 = sum(1 for x, y in zip(a, b) if x and y)
    n10 = sum(1 for x, y in zip(a, b) if x and not y)
    n01 = sum(1 for x, y in zip(a, b) if not x and y)
    n00 = sum(1 for x, y in zip(a, b) if not x and not y)
    num = n11 * n00 - n10 * n01
    den = math.sqrt((n11 + n10) * (n01 + n00) * (n11 + n01) * (n10 + n00))
    return num / den if den > 0 else 0.0


def error_correlation(actor_correct: list[bool], critic_correct: list[bool]) -> float:
    actor_wrong = [not c for c in actor_correct]
    critic_wrong = [not c for c in critic_correct]
    return _phi(actor_wrong, critic_wrong)


def catch_rate(actor_correct: list[bool], critic_flag: list[bool]) -> float:
    wrong = [i for i, c in enumerate(actor_correct) if not c]
    if not wrong:
        return float("nan")
    return sum(1 for i in wrong if critic_flag[i]) / len(wrong)


def false_block_rate(actor_correct: list[bool], critic_flag: list[bool]) -> float:
    right = [i for i, c in enumerate(actor_correct) if c]
    if not right:
        return float("nan")
    return sum(1 for i in right if critic_flag[i]) / len(right)


def summary(
    actor_correct: list[bool], critic_flag: list[bool], critic_correct: list[bool]
) -> dict:
    return {
        "n": len(actor_correct),
        "actor_acc": sum(actor_correct) / len(actor_correct)
        if actor_correct
        else float("nan"),
        "error_correlation": error_correlation(actor_correct, critic_correct),
        "catch_rate": catch_rate(actor_correct, critic_flag),
        "false_block_rate": false_block_rate(actor_correct, critic_flag),
    }
