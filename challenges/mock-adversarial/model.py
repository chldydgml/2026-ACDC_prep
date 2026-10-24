"""모의 적대적 이미지 챌린지의 '분류기' — 블랙박스. torch 없이 numpy만 사용(CPU에 가벼움).

실제 적대적 문제는 (a) 블랙박스: API가 class/confidence만 돌려주는 피드백 루프,
(b) 화이트박스: 모델 가중치(.pth/.onnx)를 주면 FGSM/PGD. 이 모의는 (a) 유형.

규칙(투명하게 공개된 간단한 결정식):
- 이미지의 평균 R - 평균 B 로 점수 s 를 낸다. s>=0 이면 'cat', s<0 이면 'dog'.
- 성공 조건: 원본('cat')을 L∞ 섭동 budget 이내로만 바꿔서 'dog' 로, confidence>임계값 으로 뒤집기.
- 원본은 결정적으로 생성(서버 재시작해도 동일). 제출 이미지와의 L∞ 거리를 서버가 검사.
해설은 README.md의 SPOILER 참고.
"""
from __future__ import annotations

import numpy as np

H, W = 64, 64
BUDGET = 16          # 허용 L∞ 섭동(0..255 척도)
CONF_THRESH = 0.8    # 성공에 필요한 confidence
FLAG = "ACDC{bl4ckb0x_3v4s10n_r3d_to_blu3}"


def base_image() -> np.ndarray:
    """결정적으로 생성되는 원본 'cat' 이미지 (H,W,3) uint8."""
    rng = np.random.default_rng(20261031)
    img = rng.integers(90, 150, size=(H, W, 3)).astype(np.int16)
    img[..., 0] += 8     # R 약간 ↑
    img[..., 2] -= 4     # B 약간 ↓  → 평균 R > 평균 B (=cat), 단 격차는 작게
    return np.clip(img, 0, 255).astype(np.uint8)


def _score(img: np.ndarray) -> float:
    a = img.astype(np.float64)
    return float(a[..., 0].mean() - a[..., 2].mean())


def predict(img: np.ndarray) -> tuple[str, float]:
    s = _score(img)
    cls = "cat" if s >= 0 else "dog"
    conf = 1.0 / (1.0 + np.exp(-abs(s) / 6.0))   # |s| 클수록 확신↑
    return cls, float(conf)


def linf(a: np.ndarray, b: np.ndarray) -> int:
    return int(np.abs(a.astype(np.int16) - b.astype(np.int16)).max())


def check_submission(img: np.ndarray) -> dict:
    orig = base_image()
    if img.shape != orig.shape:
        return {"success": False, "reason": f"shape {tuple(img.shape)} != {orig.shape}"}
    d = linf(img, orig)
    cls, conf = predict(img)
    ok = (d <= BUDGET) and (cls == "dog") and (conf > CONF_THRESH)
    out = {
        "success": ok,
        "class": cls,
        "confidence": round(conf, 4),
        "l_inf": d,
        "budget": BUDGET,
        "conf_thresh": CONF_THRESH,
    }
    if d > BUDGET:
        out["reason"] = f"perturbation L_inf {d} > budget {BUDGET}"
    elif not ok and cls != "dog":
        out["reason"] = "아직 'cat' 으로 분류됨 — 더 뒤집어야 함"
    elif not ok:
        out["reason"] = f"'dog' 이지만 confidence {round(conf,4)} <= {CONF_THRESH}"
    if ok:
        out["flag"] = FLAG
    return out
