"""Medium: LRU cache implementation with eviction."""
from collections import OrderedDict
from typing import Any


class LRUCache:
    def __init__(self, capacity: int):
        if capacity <= 0:
            raise ValueError("Capacity must be positive")
        self._capacity = capacity
        self._store: OrderedDict[str, Any] = OrderedDict()

    def get(self, key: str) -> Any:
        if key not in self._store:
            raise KeyError(key)
        self._store.move_to_end(key)
        return self._store[key]

    def put(self, key: str, value: Any) -> None:
        if key in self._store:
            self._store.move_to_end(key)
        self._store[key] = value
        if len(self._store) > self._capacity:
            self._store.popitem(last=False)

    @property
    def size(self) -> int:
        return len(self._store)

    def contains(self, key: str) -> bool:
        return key in self._store

    def clear(self) -> None:
        self._store.clear()
