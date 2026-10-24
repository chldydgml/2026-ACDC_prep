# 설치와 사용법

## 1. 노트북에 처음 한 번 설치 (Ubuntu / WSL2 / VM)

갓 만든 Ubuntu(또는 WSL2 Ubuntu, VMware·VirtualBox 게스트 포함)에서 아래만 하면 된다.
선행 도구(uv·Node·Claude Code)와 가상환경까지 `bootstrap_ubuntu.sh`가 한 번에 깐다.

```bash
# git·curl 만 먼저 (없을 때). 그 뒤 클론.
sudo apt update && sudo apt install -y git curl
git clone https://github.com/chldydgml/2026-acdc_prep.git
cd 2026-acdc_prep

# 선행 도구 + 가상환경(.venv)을 한 번에. 멱등(다시 돌려도 안전).
scripts/bootstrap_ubuntu.sh
# 적대적 이미지(torch) 문제까지 대비하려면:
scripts/bootstrap_ubuntu.sh --torch

# (선택) ECC 원본 전체를 검색용으로 받기
scripts/fetch_ecc.sh
```

`bootstrap_ubuntu.sh`가 하는 일: apt로 `curl git gnupg` → [uv](https://docs.astral.sh/uv/)(파이썬 3.12 포함)
→ Node.js 22 LTS(context7 MCP용) → Claude Code(네이티브 설치) → `.venv` 생성 + `requirements.txt` 설치.
이미 설치된 건 건너뛴다.

> 설치 후 `uv`·`claude` 가 `command not found` 면 **새 터미널**을 열거나 `source $HOME/.local/bin/env`.
> 수동으로 하고 싶으면 스크립트 내용을 그대로 한 줄씩 실행해도 된다.

## 2. 매번 풀이 시작할 때

터미널 두 개를 쓴다.

**터미널 A — Jupyter 켜기 (끄지 말고 둔다)**
```bash
scripts/start_jupyter.sh
# 브라우저로 직접 보고 싶으면: http://127.0.0.1:8888/lab?token=acdc-local
```

**터미널 B — Claude Code 켜기**
```bash
claude
```
- 처음 켜면 이 폴더의 `.mcp.json`에 있는 MCP 서버(jupyter, context7)를 쓸지 물어본다 → 승인.
- `/mcp` 를 입력하면 두 서버가 `connected`인지 확인할 수 있다.
- jupyter가 `failed`면 대부분 터미널 A의 Jupyter가 꺼져 있는 경우다.

## 3. 문제 하나 푸는 흐름

1. 대회 페이지에서 문제 설명·파일·노트북을 받아 `solutions/<문제명>/`에 넣는다.
2. Claude에게 문제 설명을 붙여 넣고 시작한다. 예:
   > "solutions/q3 에 문제 파일 넣었어. 설명은 아래와 같아. 영역 분류하고 접근 계획부터 세워줘."
3. Claude가 `CLAUDE.md`의 루틴과 `.claude/skills/`의 해당 skill을 읽고 계획을 제안한다.
4. 노트북 작업은 Jupyter MCP로 Claude가 직접 셀을 추가·실행하고 결과를 읽는다.
   사용자는 브라우저(터미널 A의 주소)로 같은 노트북을 실시간으로 보면서 방향을 잡는다.
5. API 통신은 `lib/apiclient.py`의 `Client`를 쓴다. 모든 요청/응답이 `requests.log.jsonl`에 남고,
   응답에 `Flag{...}`가 보이면 자동으로 출력된다.
6. Flag를 찾으면 `solutions/FLAGS.md`에 기록하고 제출은 사용자가 직접 한다.

## 4. 구성 요소가 각각 하는 일

| 파일/폴더 | 하는 일 |
|---|---|
| `CLAUDE.md` | Claude가 켜질 때 자동으로 읽는 규칙·루틴 |
| `.claude/skills/` | 상황별 참고서. 필요할 때만 Claude가 열어 본다 |
| `.claude/agents/security-reviewer.md` | 소스/설정 보안 리뷰를 맡길 수 있는 보조 에이전트 |
| `.mcp.json` | Claude에 연결할 외부 도구 목록 (jupyter, context7) |
| `lib/apiclient.py` | 문제 서버 통신 공통 코드 |
| `scripts/start_jupyter.sh` | Jupyter를 내 컴퓨터 안에서만 접속되게 켬 (토큰 `acdc-local`) |
| `scripts/fetch_ecc.sh` | ECC 원본 전체를 검색용으로 받음 (git에는 안 올라감) |
| `third_party/ecc/` | ECC에서 무엇을 왜 가져왔는지 + 라이선스 |
