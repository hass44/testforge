"""Code extraction and pass@k computation for LLM evaluation."""

from __future__ import annotations

HUMANEVAL_STOPS = (
    "\nclass ",
    "\ndef ",
    "\n#",
    "\nif __name__",
    "\nprint(",
    "\n@",
    "\nassert ",
    "\nimport ",
    "\nfrom ",
)


def truncate_at_stops(text: str, stops=HUMANEVAL_STOPS) -> str:
    cut = len(text)
    for s in stops:
        i = text.find(s)
        if i != -1:
            cut = min(cut, i)
    return text[:cut]


def extract_code(text: str) -> str:
    if "```" not in text:
        return text
    parts = text.split("```")
    blocks = []
    for i in range(1, len(parts), 2):
        block = parts[i]
        if block.startswith("python"):
            block = block[len("python") :]
        elif block.startswith("py"):
            block = block[len("py") :]
        blocks.append(block.lstrip("\n"))
    return blocks[0] if blocks else text


def pass_at_k(n: int, c: int, k: int) -> float:
    if k > n:
        raise ValueError("k must be <= n")
    if n - c < k:
        return 1.0
    prod = 1.0
    for i in range(n - c + 1, n + 1):
        prod *= 1.0 - k / i
    return 1.0 - prod
