import os
import time

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pydantic import BaseModel

app = FastAPI(title="Mock LLM")


class LLMRequest(BaseModel):
    prompt: str


@app.post("/llm")
def llm_endpoint(payload: LLMRequest):
    delay = float(os.getenv("MOCK_LLM_DELAY", "0"))
    if delay > 0:
        time.sleep(delay)
    if os.getenv("MOCK_LLM_FAIL", "0") == "1":
        return JSONResponse(status_code=503, content={"detail": "LLM down"})
    return {"response": f"Echo: {payload.prompt}"}
