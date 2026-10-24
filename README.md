# 2026 ACDC 예선 워크스페이스

**AI Cyber Defense Contest 2026 예선**(2026-10-31 온라인, 1인 풀이)을 Claude Code로 푸는 작업 환경.
문제를 빠르게 분석하고, 공격 코드를 짜고, API와 실시간으로 통신하며 `Flag{...}`를 찾기 위한 뼈대·스킬·템플릿을 미리 갖춰둔 저장소다.

> 역할 구분: **사람 = 운전대**(문제 읽기·판단·제출), **Claude = 손발**(코드 작성·실행·결과 판독 반복).

---

## 용도

- ACDC 예선 3영역(**AI for Security / Security for AI / AI Platform Security**) 문제를 공통 뼈대로 접근.
- 보통 Jupyter 노트북 + 제공 API 형태. Claude가 Jupyter에 직접 붙어 셀을 실행하고, 사람은 브라우저로 실시간 관찰.
- 로컬 노트북 · **CPU 전용**(RAM 16GB, GPU 없음) 기준으로 가볍게 설계.

## 빠른 시작

- 처음 설치와 상세 설명 → **`SETUP.md`**
- 핵심 사용법 요약 → **`사용법.md`**
- 대회 당일 켜기/끄기 절차 → **`대회당일_체크리스트.md`**
- 다음에 할 작업·현황 핸드오프 → **`NEXT_SESSION.md`**
- 대회 전략 배경 → **`HANDOFF.md`**

```bash
# 설치(최초 1회)
uv venv .venv --python 3.12
uv pip install --python .venv/bin/python -r requirements.txt

# 켜기 (터미널 2개)
scripts/start_jupyter.sh   # 터미널 A: 실험실 전원, 끄지 말 것
claude                     # 터미널 B: MCP 승인 → /mcp 로 connected 확인
# 브라우저: http://127.0.0.1:8888/lab?token=acdc-local
```

## 구성

```
2026-acdc_prep/
├── CLAUDE.md             # Claude가 켜질 때 자동 로드하는 규칙·문제당 루틴
├── SETUP.md / 사용법.md  # 설치 / 사용법
├── 대회당일_체크리스트.md # 당일 실행 절차 (켜기·브라우저·끄기)
├── NEXT_SESSION.md / HANDOFF.md  # 핸드오프 · 전략 배경
├── .mcp.json             # MCP 서버: jupyter(노트북 실행), context7(라이브러리 문서)
├── .claude/
│   ├── settings.json     # SessionStart 훅 → Jupyter 자동 기동
│   ├── skills/           # 공통 뼈대 1 + 유형별 4 + ECC 참고서 4
│   │   ├── ctf-api-workflow/      # 모든 문제 공통 흐름 — 가장 먼저 연다
│   │   ├── prompt-injection/      # 챗봇에서 Flag 유도
│   │   ├── adversarial-attacks/   # 이미지로 모델 오분류
│   │   ├── ai-platform-security/  # 인프라 침투·JWT·모델 탈취
│   │   ├── ai-for-security/       # 탐지모델 개발
│   │   └── (ecc) pytorch / python / docker / kubernetes-patterns
│   └── agents/security-reviewer.md
├── lib/apiclient.py      # 문제 서버 통신 공통 코드(연결·다운로드·제출·Flag 자동파싱·요청로그)
├── templates/            # 문제마다 복제해 쓰는 뼈대(노트북·FGSM/PGD·탐지·LLM평가·JWT)
├── solutions/            # 문제별 풀이 폴더 + FLAGS.md(Flag 기록장)
├── scripts/              # Jupyter 기동(start/ensure) · ECC 받기(fetch)
└── third_party/ecc/      # 외부에서 가져온 것의 출처·라이선스·목록
```

## 작동 원리 (한눈에)

`start_jupyter.sh`가 내 PC 안에서만 접속되는 **Jupyter Lab 서버**(127.0.0.1:8888, 토큰 `acdc-local`)를 띄운다.
이 서버가 노트북 문서와 커널(실행기)을 쥐고, **Claude(jupyter MCP)와 브라우저가 같은 노트북에 동시에 접속**한다.
Claude가 셀을 실행하면 그 변화가 websocket으로 브라우저에 즉시 전달돼 **실시간으로 보인다**(구글 독스와 같은 공유 문서 방식).

## 이 대회 말고도 쓰는 법 / 계속 활용하기

이 저장소는 ACDC 전용이라기보다 **"Claude + Jupyter로 보안/ML 실험을 반복하는 작업대"**다. 그래서:

- **다른 CTF·보안 과제**: 문제를 `solutions/<이름>/`에 넣고 같은 흐름으로 진행. `lib/apiclient.py`는 어떤 HTTP API에도 재사용.
- **일반 ML/데이터 실험**: Jupyter MCP로 Claude가 셀을 직접 돌리는 구조는 모델 학습·전처리·시각화 반복에 그대로 유용.
- **스킬 추가**: 새 유형을 만나면 `.claude/skills/`에 플레이북을 추가해 다음부터 Claude가 자동 참고하게 한다.
- **본선 대비**: A&D 가드레일·KOTH 등은 예선 후 별도 스킬/템플릿으로 확장(후보는 `third_party/ecc/README.md` 참고).
- **재현성**: 모든 설정이 저장소에 있으므로 새 PC에서 클론 + 설치만으로 동일 환경 복원.

## 출처 / 라이선스

- 일부 스킬·에이전트는 **[affaan-m/ECC](https://github.com/affaan-m/ECC)** (everything-claude-code, MIT License)에서
  필요한 것만 선별 복사했다. 무엇을 왜 가져왔는지와 기준 커밋은 **`third_party/ecc/README.md`** 참고.
- 나머지(규칙·템플릿·클라이언트·문서)는 이 저장소에서 작성.

## 규칙 (요약, 전문은 `CLAUDE.md`)

- 대회 규칙에서 허용이 확인되기 전엔 **대상 API에 자동 대량 질의·자동 제출 봇 금지**. 소량의 수동/반자동 시도만.
- 대회가 제공한 대상 외 시스템은 건드리지 않는다.
- 공격 보조 도구(`jwt_attack.py` 등)는 **허가된 대상(대회/모의)에만** 사용.
