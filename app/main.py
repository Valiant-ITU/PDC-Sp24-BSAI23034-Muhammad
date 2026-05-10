import os

import httpx
from fastapi import FastAPI, HTTPException, Request
from fastapi.exception_handlers import http_exception_handler
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from .circuit_breaker import CircuitOpenError
from .llm_client import breaker, call_llm

app = FastAPI(title="StudySync API")

STUDENT_ID = os.getenv("STUDENT_ID", "BSAI23034")


class GenerateRequest(BaseModel):
    prompt: str


class GenerateResponse(BaseModel):
    response: str
    source: str
    breaker_state: str
    degraded: bool


@app.middleware("http")
async def add_student_id_header(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Student-ID"] = STUDENT_ID
    return response


@app.exception_handler(HTTPException)
async def http_exception_handler_with_header(request: Request, exc: HTTPException):
    response = await http_exception_handler(request, exc)
    response.headers["X-Student-ID"] = STUDENT_ID
    return response


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    response = JSONResponse(status_code=500, content={"detail": "Internal Server Error"})
    response.headers["X-Student-ID"] = STUDENT_ID
    return response


@app.get("/health")
async def health_check():
    return {"status": "ok", "breaker_state": breaker.state}


@app.post("/generate", response_model=GenerateResponse)
async def generate_text(payload: GenerateRequest):
    try:
        result = await call_llm(payload.prompt)
        text = result.get("response", "")
        return GenerateResponse(
            response=text,
            source="llm",
            breaker_state=breaker.state,
            degraded=False,
        )
    except CircuitOpenError:
        return GenerateResponse(
            response=_fallback_response(),
            source="fallback",
            breaker_state=breaker.state,
            degraded=True,
        )
    except httpx.HTTPError:
        return GenerateResponse(
            response=_fallback_response(),
            source="fallback",
            breaker_state=breaker.state,
            degraded=True,
        )
    except Exception:
        return GenerateResponse(
            response=_fallback_response(),
            source="fallback",
            breaker_state=breaker.state,
            degraded=True,
        )


def _fallback_response() -> str:
    return "LLM unavailable. Please try again later."
