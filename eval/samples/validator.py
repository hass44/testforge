"""Medium: input validation with regex and rules."""
import re


def validate_email(email: str) -> bool:
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return bool(re.match(pattern, email))


def validate_password(password: str) -> list[str]:
    errors = []
    if len(password) < 8:
        errors.append("Must be at least 8 characters")
    if not re.search(r"[A-Z]", password):
        errors.append("Must contain an uppercase letter")
    if not re.search(r"[a-z]", password):
        errors.append("Must contain a lowercase letter")
    if not re.search(r"\d", password):
        errors.append("Must contain a digit")
    return errors


def validate_username(username: str) -> bool:
    if len(username) < 3 or len(username) > 20:
        return False
    return bool(re.match(r"^[a-zA-Z][a-zA-Z0-9_]*$", username))


def sanitize_html(text: str) -> str:
    return re.sub(r"<[^>]+>", "", text)
