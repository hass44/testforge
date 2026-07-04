"""A text processing module with multiple edge cases."""

import re
from collections import Counter


def word_count(text: str) -> int:
    """Count words in text. Empty or whitespace-only returns 0."""
    if not text or not text.strip():
        return 0
    return len(text.split())


def find_emails(text: str) -> list[str]:
    """Extract all email addresses from text."""
    pattern = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
    return re.findall(pattern, text)


def truncate(text: str, max_length: int, suffix: str = "...") -> str:
    """Truncate text to max_length, appending suffix if truncated."""
    if max_length < 0:
        raise ValueError("max_length must be non-negative")
    if len(text) <= max_length:
        return text
    if max_length < len(suffix):
        return text[:max_length]
    return text[: max_length - len(suffix)] + suffix


def most_common_words(text: str, n: int = 3) -> list[tuple[str, int]]:
    """Return the n most common words (case-insensitive)."""
    if n < 1:
        raise ValueError("n must be at least 1")
    words = re.findall(r"[a-zA-Z]+", text.lower())
    return Counter(words).most_common(n)


class TextAnalyzer:
    """Stateful text analyzer that accumulates text."""

    def __init__(self):
        self._texts: list[str] = []

    def add(self, text: str) -> None:
        """Add text to the analyzer. Ignores empty strings."""
        if text and text.strip():
            self._texts.append(text)

    @property
    def total_words(self) -> int:
        return sum(word_count(t) for t in self._texts)

    @property
    def total_texts(self) -> int:
        return len(self._texts)

    def all_emails(self) -> list[str]:
        """Extract emails from all added texts."""
        emails = []
        for t in self._texts:
            emails.extend(find_emails(t))
        return sorted(set(emails))

    def summary(self) -> dict:
        """Return a summary of all analyzed text."""
        if not self._texts:
            raise RuntimeError("No texts added yet")
        combined = " ".join(self._texts)
        return {
            "total_texts": self.total_texts,
            "total_words": self.total_words,
            "unique_emails": self.all_emails(),
            "top_words": most_common_words(combined),
        }
