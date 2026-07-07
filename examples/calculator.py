"""
A simple calculator module to test our AST analyzer.
"""


def add(a: int, b: int) -> int:
    """Add two numbers together."""
    return a + b


def subtract(a: int, b: int) -> int:
    """Subtract b from a."""
    return a - b


class AdvancedCalculator:
    """A class representing a calculator with memory."""

    def __init__(self, initial_value: float = 0.0):
        """Initialize calculator with a starting value."""
        self.value = initial_value

    def multiply(self, factor: float) -> float:
        """Multiply the current value by factor."""
        self.value *= factor
        return self.value

    def divide(self, divisor: float) -> float:
        """Divide the current value by divisor."""
        if divisor == 0:
            raise ValueError("Cannot divide by zero")
        self.value /= divisor
        return self.value
