"""Easy: pure math functions, no state."""


def clamp(value: float, low: float, high: float) -> float:
    if low > high:
        raise ValueError("low must be <= high")
    return max(low, min(value, high))


def lerp(a: float, b: float, t: float) -> float:
    return a + (b - a) * t


def is_prime(n: int) -> bool:
    if n < 2:
        return False
    if n < 4:
        return True
    if n % 2 == 0 or n % 3 == 0:
        return False
    i = 5
    while i * i <= n:
        if n % i == 0 or n % (i + 2) == 0:
            return False
        i += 6
    return True


def factorial(n: int) -> int:
    if n < 0:
        raise ValueError("n must be non-negative")
    result = 1
    for i in range(2, n + 1):
        result *= i
    return result
