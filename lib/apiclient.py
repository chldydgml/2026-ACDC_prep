"""문제 API 공통 클라이언트.

스킬/노트북에서:
    import sys; sys.path.insert(0, "../..")   # 저장소 루트
    from lib.apiclient import Challenge, find_flag
    c = Challenge(BASE_URL, token=TOKEN)
    r = c.post("/chat", json={"message": "hi"})
    c.flags            # 지금까지 응답에서 자동으로 찾은 Flag 목록

모든 요청/응답은 log_path(JSONL)에 남는다 — 어떤 시도가 먹혔는지 되짚기 위함.
자동 대량 질의 방지를 위해 min_interval(초) 간격을 강제한다.
"""
from __future__ import annotations

import base64
import io
import json
import re
import time
from pathlib import Path
from typing import Any, Callable, Iterable

import requests

FLAG_RE = re.compile(r"(?:Flag|FLAG|flag|ACDC|acdc)\{[^}\s]{1,200}\}")


def find_flags(text: str) -> list[str]:
    """문자열에서 Flag 패턴을 모두 찾는다."""
    return FLAG_RE.findall(text or "")


def find_flag(text: str) -> str | None:
    """첫 번째 Flag 하나(없으면 None)."""
    hits = find_flags(text)
    return hits[0] if hits else None


class Challenge:
    """한 문제의 API 세션. 연결/다운로드/제출/Flag 자동 파싱을 담당."""

    def __init__(
        self,
        base_url: str,
        token: str | None = None,
        headers: dict[str, str] | None = None,
        timeout: float = 30.0,
        min_interval: float = 1.0,
        log_path: str | Path = "requests.log.jsonl",
    ):
        self.base_url = base_url.rstrip("/")
        self.s = requests.Session()
        if token:
            self.s.headers["Authorization"] = f"Bearer {token}"
        self.s.headers.update(headers or {})
        self.timeout = timeout
        self.min_interval = min_interval
        self.log_path = Path(log_path)
        self.flags: list[str] = []
        self._last = 0.0

    def _url(self, path: str) -> str:
        return path if path.startswith("http") else f"{self.base_url}/{path.lstrip('/')}"

    def request(self, method: str, path: str, **kw: Any) -> requests.Response:
        wait = self.min_interval - (time.monotonic() - self._last)
        if wait > 0:
            time.sleep(wait)
        kw.setdefault("timeout", self.timeout)
        r = self.s.request(method, self._url(path), **kw)
        self._last = time.monotonic()
        self._record(method, path, kw, r)
        return r

    def get(self, path: str, **kw: Any) -> requests.Response:
        return self.request("GET", path, **kw)

    def post(self, path: str, **kw: Any) -> requests.Response:
        return self.request("POST", path, **kw)

    def _record(self, method: str, path: str, kw: dict, r: requests.Response) -> None:
        body = r.text
        new = [f for f in find_flags(body) if f not in self.flags]
        if new:
            self.flags.extend(new)
            print(f"[!] FLAG 발견: {new}")
        sent = kw.get("json") if "json" in kw else kw.get("data")
        entry = {
            "t": time.strftime("%H:%M:%S"),
            "method": method,
            "path": path,
            "sent": sent if isinstance(sent, (dict, list, str, type(None))) else str(sent),
            "status": r.status_code,
            "resp": body[:4000],
        }
        with self.log_path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")

    # --- 자주 쓰는 형태 ---
    def json(self, method: str, path: str, **kw: Any) -> Any:
        r = self.request(method, path, **kw)
        r.raise_for_status()
        return r.json()

    def download(self, path: str, dest: str | Path) -> Path:
        """타깃 데이터(이미지/모델 등)를 내려받아 dest에 저장."""
        r = self.get(path, stream=True)
        r.raise_for_status()
        dest = Path(dest)
        dest.parent.mkdir(parents=True, exist_ok=True)
        with dest.open("wb") as f:
            for chunk in r.iter_content(1 << 16):
                f.write(chunk)
        return dest

    def submit(self, path: str, **kw: Any) -> tuple[requests.Response, str | None]:
        """결과 제출. (응답, 찾은 Flag) 튜플을 돌려준다."""
        r = self.post(path, **kw)
        return r, find_flag(r.text)

    def sweep(
        self,
        values: Iterable[Any],
        make_img,
        check: Callable[[Any], bool],
        path: str,
        field: str = "file",
        fmt: str = "PNG",
    ) -> tuple[Any, Any] | None:
        """파라미터를 하나씩 바꿔가며 이미지를 만들어 제출하고, check가 True면 멈춘다.

        make_img(value) -> PIL 이미지,  check(resp_json) -> bool.
        성공 시 (value, 응답 json)을 반환, 전부 실패면 None.
        """
        for v in values:
            img = make_img(v)
            r = self.post_image_file(path, img, field=field, fmt=fmt)
            try:
                data = r.json()
            except ValueError:
                data = {"text": r.text}
            print(f"  sweep {v!r}: status={r.status_code} {str(data)[:160]}")
            if check(data):
                print(f"[+] 성공: value={v!r}")
                return v, data
        print("[-] 스윕 전부 실패")
        return None

    def post_image_file(self, path: str, img, field: str = "file", fmt: str = "PNG", **kw: Any):
        """PIL 이미지를 multipart로 업로드 (PNG는 무손실)."""
        buf = io.BytesIO()
        img.save(buf, format=fmt)
        buf.seek(0)
        files = {field: (f"image.{fmt.lower()}", buf, f"image/{fmt.lower()}")}
        return self.post(path, files=files, **kw)

    def post_image_b64(self, path: str, img, key: str = "image", fmt: str = "PNG", extra: dict | None = None):
        """PIL 이미지를 base64 JSON으로 업로드."""
        buf = io.BytesIO()
        img.save(buf, format=fmt)
        payload = {key: base64.b64encode(buf.getvalue()).decode(), **(extra or {})}
        return self.post(path, json=payload)


# 이전 이름 호환
Client = Challenge
