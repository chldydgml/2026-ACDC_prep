# 새 세션 핸드오프 — 2026 ACDC 예선 워크스페이스

> 이 저장소(`chldydgml/2026-acdc_prep`)를 git으로 물린 새 Claude 세션이 이 문서만 읽고
> 바로 이어서 작업하도록 쓴 자립형 요약. 다음 할 일은 **(선택) 적대적/인프라 유형 리허설**.

---

## 0. 지금 상태 한 줄
예선 풀이 환경(뼈대·스킬·템플릿·MCP·Ubuntu 부트스트랩)은 **구축 완료**, **인젝션 리허설도
end-to-end 성공**(`solutions/FLAGS.md`에 mock-injection 1건). 환경이 통신→공격→Flag파싱→기록까지
도는 것을 VM(Ubuntu)에서 실제로 확인함. 남은 건 **(선택) 다른 유형(적대적 이미지/인프라) 리허설**과
대회 당일 운영뿐. 구조·실대회 흐름은 `구조.md` 참고.

## 1. 대회 팩트 (요약)
- 2026 ACDC(AI Cyber Defense Contest) 예선, **2026-10-31(토) 09:00~17:00 온라인**. 신청 마감 10-26 14:00.
- 혼자 문제를 푼다(팀 로직은 지금 비고려). 문제 3영역: **AI for Security / Security for AI / AI Platform Security**.
- 보통 Jupyter 노트북 + 제공 API로 실시간 통신하며 `Flag{...}`(또는 `ACDC{...}`)를 찾는 형태.
- 로컬 노트북, **CPU 전용**(RAM 16GB, GPU 없음). 무거운 연산은 작은 모델·적은 스텝.
- 2025 형태는 참고일 뿐, 특정 형태에 밀착하지 않는다. 자세한 배경은 `HANDOFF.md`.

## 2. 구축된 환경 (무엇이 왜 있는가)

```
2026-acdc_prep/
├── README.md             # 저장소 소개·구성·원리·활용·출처 (진입점)
├── CLAUDE.md             # 세션 시작 시 자동 로드되는 규칙·문제당 루틴
├── SETUP.md              # 설치(Ubuntu/WSL2/VM, bootstrap 스크립트)
├── 사용법.md             # 한 장짜리 핵심 사용법
├── 구조.md               # 폴더 역할 + 실제 대회 흐름 (challenges vs solutions)
├── 대회당일_체크리스트.md # 당일 켜기·브라우저·끄기 절차
├── HANDOFF.md            # 대회 전략 배경(구버전 핸드오프)
├── NEXT_SESSION.md       # (이 문서)
├── .mcp.json             # MCP 서버: jupyter, context7
├── challenges/           # 내가 만든 연습 문제 보관소(대회 땐 안 씀)
│   └── mock-injection/   # 규칙기반 인젝션 챗봇(server.py+guardrail.py) — 리허설 대상
├── .claude/
│   ├── settings.json     # SessionStart 훅 → Jupyter 자동 기동
│   ├── skills/           # 공통 뼈대 + 유형별 4개 + ECC에서 가져온 4개
│   │   ├── ctf-api-workflow/        # 모든 문제 공통 흐름 — 먼저 연다
│   │   ├── prompt-injection/        # 챗봇에서 Flag 유도
│   │   ├── adversarial-attacks/     # 이미지로 모델 오분류
│   │   ├── ai-platform-security/    # 인프라 침투·JWT·모델 탈취
│   │   ├── ai-for-security/         # 탐지모델 개발
│   │   └── (ecc) pytorch/python/docker/kubernetes-patterns
│   └── agents/security-reviewer.md
├── lib/apiclient.py      # Challenge 클래스: 연결/다운로드/제출/Flag 자동파싱/요청간격/로그
├── templates/            # 문제마다 복제해 쓰는 뼈대
│   ├── notebook_starter.ipynb
│   ├── adversarial_attack.py    # FGSM/PGD (torchattacks+수동 폴백, CPU 자동)
│   ├── detection_baseline.py
│   ├── llm_eval_harness.py
│   ├── prompt_injection_tests.md
│   └── jwt_attack.py            # JWT 디코드/위조 점검(무의존)
├── solutions/            # 문제별 풀이 작업장(고정)
│   ├── FLAGS.md          # Flag 기록장 (mock-injection 1건 기록됨)
│   └── mock-injection/   # 리허설 풀이 노트북(solve.ipynb)
├── requirements.txt / requirements-ml.txt  # 기본 / (적대적·모델 전용, --torch 때)
├── scripts/
│   ├── bootstrap_ubuntu.sh # Ubuntu 선행도구+venv 원스텝(멱등). --torch 로 torch까지
│   ├── start_jupyter.sh  # 터미널에 붙잡아 두고 켜는 포그라운드 방식(root면 --allow-root 자동)
│   ├── ensure_jupyter.sh # 안 떠 있으면 백그라운드 기동(멱등). 훅이 호출
│   └── fetch_ecc.sh      # ECC 원본 전체를 검색용으로 받기(git 제외)
└── third_party/ecc/      # ECC 출처·라이선스(MIT)·가져온 목록
```

### ECC에서 가져온 것 (통짜 설치 안 함)
`affaan-m/ECC`(everything-claude-code, MIT)에서 **스킬 4개 + 에이전트 1개만** 복사.
목록·이유·기준 커밋은 `third_party/ecc/README.md`. 원본 전체가 필요하면 `scripts/fetch_ecc.sh`.

### MCP 서버 (`.mcp.json`)
- **jupyter** (`jupyter-mcp-server==2.2.4`): 노트북 셀을 Claude가 직접 실행/판독. 127.0.0.1:8888, 토큰 `acdc-local`.
- **context7** (`@upstash/context7-mcp@4.4.4`): torch/torchattacks/onnxruntime/kubernetes 등 라이브러리 최신 문서 조회.
- 새 세션 첫 실행 때 "이 MCP 서버 쓸까요?"를 승인해야 붙는다. `/mcp`로 `connected` 확인.

## 3. Jupyter 자동 기동 — 동작 방식 (중요)
- `.claude/settings.json`에 **SessionStart 훅**이 있어, 세션이 시작될 때 `scripts/ensure_jupyter.sh`를 실행한다.
- 이 스크립트는 **멱등**이다: 이미 떠 있으면 건너뛰고, 꺼져 있으면 백그라운드로 띄운다(로그 `/tmp/acdc-jupyter.log`).
  컨테이너(root)에서는 `--allow-root`를 자동으로 붙인다.
- **단, `.venv`가 없으면(=아직 설치 전) 조용히 건너뛴다.** 그래서 순서가 중요하다(아래 4번).
- 프로젝트 훅은 새 환경에서 **승인/신뢰 확인**을 한 번 요구할 수 있다. 승인하면 이후 자동 동작.

## 4. 설치·리허설 현황 (이미 완료) + 다음 할 일

### 완료된 것
- **설치**: Ubuntu VM에서 `scripts/bootstrap_ubuntu.sh`로 선행도구+`.venv` 구축, `/mcp`에서
  jupyter·context7 `connected` 확인. (콜드 환경이면 이 스크립트 한 방이면 됨.)
- **인젝션 리허설**: `challenges/mock-injection` 서버(`:9000`)를 대상으로
  `solutions/mock-injection/solve.ipynb`에서 end-to-end 성공 → `FLAGS.md` 기록.
  흐름·구조는 `구조.md`에 정리.

### 다음 세션에서 할 수 있는 일 (선택)
1. **다른 유형 리허설** — 같은 틀로 `challenges/` 아래에 추가:
   - 적대적 이미지: 작은 분류모델 + 이미지 제출 API(성공조건 체크). `adversarial-attacks` 스킬.
     (이땐 `scripts/bootstrap_ubuntu.sh --torch`로 torch 설치 필요.)
   - 인프라/JWT: 토큰 위조·모델파일 탈취 미니 시나리오. `ai-platform-security` 스킬.
2. **인젝션 심화** — 모의 서버를 난이도 (b)로: Flag를 2개 필드로 쪼개 간접 조합만 되게 `guardrail.py` 확장.
3. **대회 운영 준비** — 예선 규칙(자동질의/레이트리밋 허용) 재확인, 신청 상태 점검(§6).

### 대회 당일 실제 문제 푸는 법 (요약 — 상세는 `구조.md`)
- `solutions/<문제명>/`에 받은 파일을 넣고, `notebook_starter.ipynb`를 복제해 `BASE_URL`만 대회 URL로 바꾼다.
- VM Claude에게 "영역 분류하고 계획부터" → Claude가 자동 분류·스킬 선택, 사람은 방향만 잡는다.
- `challenges/`는 **연습 전용**이라 대회 땐 쓰지 않는다(대상은 대회 서버에 있음).

## 5. 규칙 / 주의
- **대회 규칙 확인 전**: 실제 대회 대상 API에 자동 대량 질의·자동 제출 봇 금지. (모의 로컬 서버는 예외)
- 대회가 제공한 대상 외 시스템은 건드리지 않는다.
- `jwt_attack.py` 등 공격 보조는 **허가된 대상(대회/모의)에만**.
- 커밋 메시지 형식: 이모지 + 키워드 + 설명. 예) `✨ feat : 모의 인젝션 서버 추가`, `🐛 fix : ...`, `📝 docs : ...`.
- **Git 워크플로**: `main`에 직접 푸시하지 않는다. 작업은 `claude/busy-wozniak-cprq2s`
  브랜치에 쌓고 **PR로 주기적으로 merge**한다. 커밋 author는 저장소 주인(chldydgml)으로
  맞춘다(실제 push 주체는 Claude GitHub App일 수 있음 — 바꿀 수 없는 부분). PR이 merge된
  뒤의 후속 작업은 최신 `main`에서 같은 브랜치를 다시 시작한다.

## 6. 아직 확정 안 됨 (여유 될 때)
- 예선 규칙 원문에서 자동 질의/레이트리밋 허용 여부 재확인(qna@acdc2026.ai.kr, 요강).
- 2025 write-up 원문 재검증(`HANDOFF.md` §8 링크).
- 본선(A&D 가드레일, KOTH) 준비는 예선 후 별도.
