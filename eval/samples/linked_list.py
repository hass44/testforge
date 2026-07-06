"""Hard: linked list with multiple operations."""


class Node:
    def __init__(self, value, next_node=None):
        self.value = value
        self.next = next_node


class LinkedList:
    def __init__(self):
        self._head: Node | None = None
        self._size: int = 0

    def append(self, value) -> None:
        if self._head is None:
            self._head = Node(value)
        else:
            current = self._head
            while current.next:
                current = current.next
            current.next = Node(value)
        self._size += 1

    def prepend(self, value) -> None:
        self._head = Node(value, self._head)
        self._size += 1

    def remove(self, value) -> bool:
        if self._head is None:
            return False
        if self._head.value == value:
            self._head = self._head.next
            self._size -= 1
            return True
        current = self._head
        while current.next:
            if current.next.value == value:
                current.next = current.next.next
                self._size -= 1
                return True
            current = current.next
        return False

    def find(self, value) -> int:
        current = self._head
        index = 0
        while current:
            if current.value == value:
                return index
            current = current.next
            index += 1
        return -1

    def to_list(self) -> list:
        result = []
        current = self._head
        while current:
            result.append(current.value)
            current = current.next
        return result

    def reverse(self) -> None:
        prev = None
        current = self._head
        while current:
            next_node = current.next
            current.next = prev
            prev = current
            current = next_node
        self._head = prev

    @property
    def size(self) -> int:
        return self._size

    @property
    def is_empty(self) -> bool:
        return self._head is None
