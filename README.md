Hafiz Abdullah Muhammad - BSAI23034

# StudySync - Circuit Breaker Fix

This project demonstrates a circuit breaker + fallback response for unreliable LLM calls in a
FastAPI app.

## Setup

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## Run the main API

```bash
uvicorn app.main:app --reload --port 8000
```

The API always includes the required `X-Student-ID: BSAI23034` header on every response.

## Run the mock LLM server

```bash
uvicorn scripts.mock_llm_server:app --reload --port 8001
```

Optional environment variables for the mock server:
- `MOCK_LLM_DELAY=5` adds a delay to trigger timeouts.
- `MOCK_LLM_FAIL=1` always returns HTTP 503.

## Simulate the failure

1. Start the API server.
2. Stop the mock LLM server (or set `MOCK_LLM_DELAY=5`).
3. Run the simulation script:

```bash
python scripts\simulate_llm_failure.py --calls 6
```

After a few failures, the circuit breaker opens and the API returns a fast fallback response.

## Demo instructions (before/after)

- Before: run with the breaker disabled to show the API waiting on the slow LLM.

```bash
set BREAKER_ENABLED=0
uvicorn app.main:app --reload --port 8000
```

- After: run with the breaker enabled (default) to show immediate fallbacks.

```bash
set BREAKER_ENABLED=1
uvicorn app.main:app --reload --port 8000
```

## Run tests

```bash
pytest
```

## Configuration

Environment variables supported by the API:
- `STUDENT_ID` (default `BSAI23034`)
- `LLM_URL` (default `http://127.0.0.1:8001/llm`)
- `LLM_TIMEOUT` (default `2.0`)
- `BREAKER_ENABLED` (default `1`)
- `BREAKER_FAILURE_THRESHOLD` (default `3`)
- `BREAKER_RECOVERY_TIMEOUT` (default `10`)
- `BREAKER_SUCCESS_THRESHOLD` (default `1`)
