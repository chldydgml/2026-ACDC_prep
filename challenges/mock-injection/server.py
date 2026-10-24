"""모의 프롬프트 인젝션 챗봇 서버 (FastAPI).

실행:
    # 저장소 루트 기준
    uv run --python .venv/bin/python uvicorn --app-dir challenges/mock-injection server:app --port 9000
    # 또는 해당 폴더에서
    cd challenges/mock-injection && ../../.venv/bin/python server.py

로컬(127.0.0.1)에서만 뜬다. 우리가 만든 연습 대상이므로 자유롭게 질의해도 된다
(실제 대회 서버에 대한 자동 대량 질의 금지 규칙과는 무관).

엔드포인트:
    GET  /        → 안내/힌트
    GET  /health  → {"ok": true}
    POST /chat    → {"message": "..."} 를 받아 {"reply": "..."} 반환
"""
from __future__ import annotations

import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel

from guardrail import respond

app = FastAPI(title="ACDC Mock Injection Bot")


class ChatIn(BaseModel):
    message: str = ""


@app.get("/")
def root() -> dict:
    return {
        "name": "ACDC Mock Injection Bot",
        "hint": "POST /chat {\"message\": \"...\"}. 직접 물으면 거부당한다. 비밀을 빼내 보라.",
        "goal": "응답에서 ACDC{...} 를 찾기",
    }


@app.get("/health")
def health() -> dict:
    return {"ok": True}


@app.post("/chat")
def chat(body: ChatIn) -> dict:
    _, reply = respond(body.message)
    return {"reply": reply}


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=9000)
