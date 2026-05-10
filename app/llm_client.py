import os

import httpx

from .circuit_breaker import CircuitBreaker, CircuitBreakerConfig

LLM_URL = os.getenv("LLM_URL", "http://127.0.0.1:8001/llm")
LLM_TIMEOUT = float(os.getenv("LLM_TIMEOUT", "2.0"))
BREAKER_ENABLED = os.getenv("BREAKER_ENABLED", "1") == "1"


def _breaker_config() -> CircuitBreakerConfig:
    return CircuitBreakerConfig(
        failure_threshold=int(os.getenv("BREAKER_FAILURE_THRESHOLD", "3")),
        recovery_timeout=float(os.getenv("BREAKER_RECOVERY_TIMEOUT", "10")),
        success_threshold=int(os.getenv("BREAKER_SUCCESS_THRESHOLD", "1")),
    )


breaker = CircuitBreaker(_breaker_config())


async def _do_llm_call(prompt: str) -> dict:
    async with httpx.AsyncClient(timeout=LLM_TIMEOUT) as client:
        response = await client.post(LLM_URL, json={"prompt": prompt})
        response.raise_for_status()
        return response.json()


async def call_llm(prompt: str) -> dict:
    if not BREAKER_ENABLED:
        return await _do_llm_call(prompt)
    return await breaker.call(lambda: _do_llm_call(prompt))
