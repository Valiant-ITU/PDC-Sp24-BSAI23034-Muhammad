import asyncio

import pytest

from app.circuit_breaker import CircuitBreaker, CircuitBreakerConfig, CircuitOpenError


async def _fail() -> None:
    raise RuntimeError("boom")


async def _ok() -> str:
    return "ok"


def test_opens_after_failures() -> None:
    breaker = CircuitBreaker(
        CircuitBreakerConfig(failure_threshold=2, recovery_timeout=30.0, success_threshold=1)
    )
    for _ in range(2):
        with pytest.raises(RuntimeError):
            asyncio.run(breaker.call(_fail))
    with pytest.raises(CircuitOpenError):
        asyncio.run(breaker.call(_ok))
