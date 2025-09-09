from __future__ import annotations

import os
import time
from fastapi import FastAPI, HTTPException, Request, Depends, Header
from pydantic import BaseModel

from .services.db import add_idea, init_db
from .services.llm_interface import gerar_resposta


app = FastAPI()

# --- Auth -----------------------------------------------------------------

def verify_token(x_token: str = Header(...)) -> None:
    expected = os.getenv("HERMES_TOKEN")
    if not expected or x_token != expected:
        raise HTTPException(status_code=401, detail="Invalid token")


# --- Rate limiting --------------------------------------------------------

REQUEST_LIMIT = 60  # requests per minute
_window = 60
_requests: dict[str, tuple[int, float]] = {}


@app.middleware("http")
async def rate_limiter(request: Request, call_next):
    key = request.client.host or "global"
    now = time.time()
    count, start = _requests.get(key, (0, now))
    if now - start > _window:
        count, start = 0, now
    if count >= REQUEST_LIMIT:
        raise HTTPException(status_code=429, detail="Rate limit exceeded")
    _requests[key] = (count + 1, start)
    return await call_next(request)


# --- Models ----------------------------------------------------------------

class Idea(BaseModel):
    user: int
    title: str
    body: str


class Prompt(BaseModel):
    prompt: str


# --- Startup ---------------------------------------------------------------

@app.on_event("startup")
def _startup() -> None:
    init_db()


# --- Endpoints -------------------------------------------------------------

@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/ideas")
def create_idea(
    idea: Idea,
    request: Request,
    _: None = Depends(verify_token),
) -> dict[str, int | str]:
    device_id = request.headers.get("X-Device-Id", "")
    source = f"caduceu_{device_id}" if device_id else "caduceu_"
    idea_id = add_idea(idea.user, idea.title, idea.body, source=source)
    return {"id": idea_id, "source": source}


@app.post("/ask")
def ask(prompt: Prompt, _: None = Depends(verify_token)) -> dict[str, str]:
    result = gerar_resposta(prompt.prompt)
    if not result.get("ok"):
        raise HTTPException(status_code=502, detail=result.get("message", "error"))
    return {"response": result["response"]}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", "8000")))
