from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Awaitable, Callable, TypeVar

T = TypeVar("T")


class CircuitOpenError(RuntimeError):
    pass


@dataclass(frozen=True)
class CircuitBreakerConfig:
    failure_threshold: int = 3
    recovery_timeout: float = 10.0
    success_threshold: int = 1


class CircuitBreaker:
    def __init__(self, config: CircuitBreakerConfig) -> None:
        self._config = config
        self._state = "closed"
        self._failure_count = 0
        self._success_count = 0
        self._opened_at = 0.0

    @property
    def state(self) -> str:
        return self._state

    async def call(self, func: Callable[[], Awaitable[T]]) -> T:
        self._before_call()
        try:
            result = await func()
        except Exception:
            self._record_failure()
            raise
        else:
            self._record_success()
            return result

    def _before_call(self) -> None:
        if self._state != "open":
            return
        elapsed = time.monotonic() - self._opened_at
        if elapsed >= self._config.recovery_timeout:
            self._transition_to_half_open()
            return
        raise CircuitOpenError("circuit breaker is open")

    def _record_success(self) -> None:
        if self._state == "half_open":
            self._success_count += 1
            if self._success_count >= self._config.success_threshold:
                self._transition_to_closed()
            return
        self._failure_count = 0

    def _record_failure(self) -> None:
        if self._state == "half_open":
            self._transition_to_open()
            return
        self._failure_count += 1
        if self._failure_count >= self._config.failure_threshold:
            self._transition_to_open()

    def _transition_to_open(self) -> None:
        self._state = "open"
        self._opened_at = time.monotonic()
        self._failure_count = 0
        self._success_count = 0

    def _transition_to_half_open(self) -> None:
        self._state = "half_open"
        self._failure_count = 0
        self._success_count = 0

    def _transition_to_closed(self) -> None:
        self._state = "closed"
        self._failure_count = 0
        self._success_count = 0
