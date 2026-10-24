"""LLM 공격셋 성공률 측정 하네스.

프롬프트 인젝션 문제에서 여러 시도(payload)를 한 번에 돌려
어떤 것이 성공했는지 표로 보기 위함. 자동 '대량' 질의가 아니라,
직접 만든 소수의 가설 payload를 정리해 비교하는 용도.
대량 자동질의 허용 여부는 규칙에서 먼저 확인할 것.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable

from lib.apiclient import Challenge, find_flag


@dataclass
class Attempt:
    name: str          # 이 시도의 가설 한 줄
    payload: dict      # API에 보낼 바디 (예: {"message": "..."})
    success: bool = False
    flag: str | None = None
    response: str = ""


def run(c: Challenge, path: str, attempts: list[Attempt],
        check: Callable[[dict | str], bool] | None = None) -> list[Attempt]:
    """attempts를 순서대로 제출하고 결과를 채워서 돌려준다."""
    for a in attempts:
        r = c.post(path, json=a.payload)
        a.response = r.text[:500]
        a.flag = find_flag(r.text)
        try:
            body = r.json()
        except ValueError:
            body = r.text
        a.success = bool(a.flag) or (check(body) if check else False)
        mark = "O" if a.success else "."
        print(f"[{mark}] {a.name}  flag={a.flag}")
    ok = sum(a.success for a in attempts)
    print(f"\n성공 {ok}/{len(attempts)}")
    return attempts
