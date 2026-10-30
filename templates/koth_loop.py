"""KotH(거점 점령) 유지 루프 템플릿.

Jeopardy용 흐름은 그대로 두고, KotH 문제에서만 쓰는 유지 하네스.
문제마다 `solutions/<문제명>/`로 복제해 세 콜백만 채우면 된다.

콜백 (c = lib.apiclient.Challenge):
    check(c)  -> {"held": bool, ...}   # 지금 내가 점유 중인가 (상태/점수 엔드포인트 폴링)
    retake(c) -> dict                  # 점령 시도: 취약점 공격 + 마커 설치 (밀렸을 때만 호출)
    defend(c) -> dict | None           # (선택) 하드닝/방어 1회 (점유 중일 때 호출)

규칙 준수:
    - 대상은 제공된 격리 환경만. DoS·과도한 자동 요청·대량 스캔 금지.
    - `interval`은 채점 틱에 맞춘 얌전한 주기로 둔다(예: 틱 15초면 interval=15).
    - Challenge(min_interval=...) 로 요청 간 최소 간격도 함께 건다.

사용 예 (노트북 또는 스크립트):
    import sys; sys.path.insert(0, "../..")
    from lib.apiclient import Challenge
    from koth_loop import run_koth

    c = Challenge("http://TARGET", min_interval=1.0)
    def check(c):  r = c.get("/status"); return {"held": "MYMARK" in r.text}
    def retake(c): ...; return {"ok": True}
    def defend(c): ...; return {"patched": True}
    run_koth(c, check, retake, defend, interval=15, max_seconds=600)
"""
from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any, Callable, Optional

CheckFn = Callable[[Any], dict]
ActFn = Callable[[Any], Optional[dict]]


def _log(path: Path, event: str, data: dict) -> None:
    rec = {"t": time.strftime("%H:%M:%S"), "event": event, **data}
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(rec, ensure_ascii=False) + "\n")


def run_koth(
    c: Any,
    check: CheckFn,
    retake: ActFn,
    defend: Optional[ActFn] = None,
    *,
    interval: float = 15.0,
    max_ticks: Optional[int] = None,
    max_seconds: Optional[float] = None,
    log_path: str | Path = "koth.events.jsonl",
    verbose: bool = True,
) -> dict:
    """점유 상태를 폴링하며 밀리면 재탈환, 점유 중이면 (선택) 방어하는 얌전한 루프.

    Ctrl-C 또는 max_ticks/max_seconds 도달 시 멈추고 점유 통계를 돌려준다.
    """
    log = Path(log_path)
    start = time.monotonic()
    tick = 0
    held_total = 0.0          # 누적 점유 시간(초)
    held_since: Optional[float] = None
    takeovers = 0             # 재탈환 횟수
    prev_held: Optional[bool] = None

    def _print(*a: object) -> None:
        if verbose:
            print(*a)

    _print(f"[koth] 시작 · interval={interval}s · 대상={getattr(c,'base_url','?')}")
    try:
        while True:
            now = time.monotonic()
            if max_seconds is not None and now - start >= max_seconds:
                break
            if max_ticks is not None and tick >= max_ticks:
                break
            tick += 1

            # 1) 상태 확인
            try:
                st = check(c) or {}
            except Exception as e:  # 네트워크 흔들림 등 — 다음 틱 재시도
                _log(log, "check_error", {"tick": tick, "err": str(e)})
                _print(f"  tick {tick}: check 오류 {e!r}")
                _sleep(interval, start, max_seconds)
                continue
            held = bool(st.get("held"))
            _log(log, "check", {"tick": tick, "held": held, "info": _trim(st)})

            # 점유 상태 전이 추적
            if held and held_since is None:
                held_since = now
                if prev_held is False:
                    takeovers += 1
            if (not held) and held_since is not None:
                held_total += now - held_since
                held_since = None
            prev_held = held

            # 2) 밀렸으면 재탈환, 점유 중이면 (선택) 방어
            if not held:
                _print(f"  tick {tick}: 점유 상실 → 재탈환 시도")
                try:
                    r = retake(c) or {}
                    _log(log, "retake", {"tick": tick, "result": _trim(r)})
                except Exception as e:
                    _log(log, "retake_error", {"tick": tick, "err": str(e)})
                    _print(f"    재탈환 오류 {e!r}")
            else:
                _print(f"  tick {tick}: 점유 유지" + ("  (방어 1회)" if defend else ""))
                if defend is not None:
                    try:
                        d = defend(c)
                        if d:
                            _log(log, "defend", {"tick": tick, "result": _trim(d)})
                    except Exception as e:
                        _log(log, "defend_error", {"tick": tick, "err": str(e)})
                        _print(f"    방어 오류 {e!r}")

            _sleep(interval, start, max_seconds)
    except KeyboardInterrupt:
        _print("\n[koth] 중단(Ctrl-C)")

    # 마지막 점유 구간 반영
    if held_since is not None:
        held_total += time.monotonic() - held_since
    elapsed = time.monotonic() - start
    stats = {
        "ticks": tick,
        "elapsed_s": round(elapsed, 1),
        "held_s": round(held_total, 1),
        "held_ratio": round(held_total / elapsed, 3) if elapsed else 0.0,
        "takeovers": takeovers,
    }
    _log(log, "summary", stats)
    _print(f"[koth] 종료 · 점유 {stats['held_s']}s / {stats['elapsed_s']}s "
           f"(비율 {stats['held_ratio']}) · 재탈환 {takeovers}회")
    return stats


def _sleep(interval: float, start: float, max_seconds: Optional[float]) -> None:
    """interval 만큼 쉬되, max_seconds 를 넘기지 않도록 조정."""
    if max_seconds is not None:
        remain = max_seconds - (time.monotonic() - start)
        interval = max(0.0, min(interval, remain))
    if interval > 0:
        time.sleep(interval)


def _trim(d: Any, limit: int = 300) -> Any:
    """로그에 남길 때 과하게 긴 값은 잘라낸다."""
    s = str(d)
    return d if len(s) <= limit else s[:limit] + "…"
