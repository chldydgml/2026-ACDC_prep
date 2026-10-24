"""모의 적대적 이미지 챌린지 서버 (FastAPI). 블랙박스 분류기, torch 불필요(numpy/PIL).

실행 (저장소 루트 기준):
    cd challenges/mock-adversarial && ../../.venv/bin/python server.py
    # 또는
    .venv/bin/python -m uvicorn --app-dir challenges/mock-adversarial server:app --port 9001

엔드포인트:
    GET  /         → 안내(budget, 임계값, 성공조건)
    GET  /image    → 원본 'cat' 이미지(PNG) 다운로드  = 공격 시작점
    POST /predict  → multipart 'file' 이미지 → {class, confidence}  (피드백용, 제한 없음)
    POST /submit   → multipart 'file' 이미지 → L∞ budget + 성공조건 검사 → 성공 시 flag
"""
from __future__ import annotations

import io

import numpy as np
import uvicorn
from fastapi import FastAPI, File, UploadFile
from fastapi.responses import Response
from PIL import Image

from model import base_image, predict, check_submission, BUDGET, CONF_THRESH, H, W

app = FastAPI(title="ACDC Mock Adversarial Challenge")


def _to_png(arr: np.ndarray) -> bytes:
    buf = io.BytesIO()
    Image.fromarray(arr, mode="RGB").save(buf, format="PNG")
    return buf.getvalue()


def _load(data: bytes) -> np.ndarray:
    img = Image.open(io.BytesIO(data)).convert("RGB")
    return np.asarray(img, dtype=np.uint8)


@app.get("/")
def root() -> dict:
    return {
        "name": "ACDC Mock Adversarial Challenge",
        "task": "원본 'cat' 이미지를 L∞ 섭동 budget 이내로 바꿔 'dog'(confidence>임계값)로 오분류시켜라",
        "image_size": [H, W, 3],
        "budget_linf": BUDGET,
        "conf_thresh": CONF_THRESH,
        "endpoints": {"GET /image": "원본 다운로드", "POST /predict": "피드백", "POST /submit": "채점"},
        "hint": "/predict 로 원본을 찍어보고, 규칙을 추론해 작은 섭동으로 뒤집어 /submit",
    }


@app.get("/image")
def get_image() -> Response:
    return Response(content=_to_png(base_image()), media_type="image/png")


@app.post("/predict")
async def post_predict(file: UploadFile = File(...)) -> dict:
    arr = _load(await file.read())
    cls, conf = predict(arr)
    return {"class": cls, "confidence": round(conf, 4), "shape": list(arr.shape)}


@app.post("/submit")
async def post_submit(file: UploadFile = File(...)) -> dict:
    arr = _load(await file.read())
    return check_submission(arr)


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=9001)
