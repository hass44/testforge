"""Medium: class with state and error handling."""


class Stack:
    def __init__(self, max_size: int | None = None):
        self._items: list = []
        self._max_size = max_size

    def push(self, item) -> None:
        if self._max_size and len(self._items) >= self._max_size:
            raise OverflowError("Stack is full")
        self._items.append(item)

    def pop(self):
        if not self._items:
            raise IndexError("Pop from empty stack")
        return self._items.pop()

    def peek(self):
        if not self._items:
            raise IndexError("Peek at empty stack")
        return self._items[-1]

    @property
    def size(self) -> int:
        return len(self._items)

    @property
    def is_empty(self) -> bool:
        return len(self._items) == 0

    def clear(self) -> None:
        self._items.clear()
