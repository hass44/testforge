"""Hard: recursive JSON flattening and unflattening."""

from typing import Any


def flatten(data: dict, separator: str = ".") -> dict[str, Any]:
    result = {}
    _flatten_recursive(data, "", separator, result)
    return result


def _flatten_recursive(obj: Any, prefix: str, sep: str, result: dict) -> None:
    if isinstance(obj, dict):
        for key, value in obj.items():
            new_key = f"{prefix}{sep}{key}" if prefix else key
            _flatten_recursive(value, new_key, sep, result)
    elif isinstance(obj, list):
        for i, value in enumerate(obj):
            new_key = f"{prefix}{sep}{i}" if prefix else str(i)
            _flatten_recursive(value, new_key, sep, result)
    else:
        result[prefix] = obj


def unflatten(data: dict[str, Any], separator: str = ".") -> dict:
    result: dict = {}
    for key, value in data.items():
        parts = key.split(separator)
        current = result
        for part in parts[:-1]:
            if part not in current:
                current[part] = {}
            current = current[part]
        current[parts[-1]] = value
    return result
