"""Easy: string manipulation functions."""


def reverse_words(text: str) -> str:
    return " ".join(text.split()[::-1])


def is_palindrome(text: str) -> bool:
    cleaned = "".join(c.lower() for c in text if c.isalnum())
    return cleaned == cleaned[::-1]


def truncate(text: str, max_len: int, suffix: str = "...") -> str:
    if max_len < len(suffix):
        raise ValueError("max_len must be >= len(suffix)")
    if len(text) <= max_len:
        return text
    return text[: max_len - len(suffix)] + suffix


def count_vowels(text: str) -> int:
    return sum(1 for c in text.lower() if c in "aeiou")
