"""Hard: token bucket rate limiter with time dependency."""
import time


class RateLimiter:
    def __init__(self, max_tokens: int, refill_rate: float):
        if max_tokens <= 0:
            raise ValueError("max_tokens must be positive")
        if refill_rate <= 0:
            raise ValueError("refill_rate must be positive")
        self._max_tokens = max_tokens
        self._refill_rate = refill_rate
        self._tokens = float(max_tokens)
        self._last_refill = time.monotonic()

    def _refill(self) -> None:
        now = time.monotonic()
        elapsed = now - self._last_refill
        self._tokens = min(
            self._max_tokens,
            self._tokens + elapsed * self._refill_rate,
        )
        self._last_refill = now

    def allow(self, tokens: int = 1) -> bool:
        if tokens <= 0:
            raise ValueError("tokens must be positive")
        self._refill()
        if self._tokens >= tokens:
            self._tokens -= tokens
            return True
        return False

    @property
    def available_tokens(self) -> float:
        self._refill()
        return self._tokens

    def reset(self) -> None:
        self._tokens = float(self._max_tokens)
        self._last_refill = time.monotonic()
