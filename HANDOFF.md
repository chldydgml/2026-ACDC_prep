# 2026 ACDC 예선 전략 — 핸드오프 (다른 세션용)

> 목적: 콜드 스타트한 다른 Claude 세션이 이 문서만 읽고 바로 전략 대화를 이어가게 하는 자립형 요약.
> 사용자는 브라우저 화면(1차 출처)을 보면서 이 세션과 전략을 고도화할 예정.

---

## 0. 한 줄 상황
사용자는 **2026 ACDC(AI Cyber Defense Contest) 예선**을 준비 중. **혼자 문제를 푼다**(팀으로 나가지만 문제는 각자, 일부 팀원은 codex 사용 — 교차검증 등 팀 로직은 지금 고려 안 함). 예선용 Claude Code 워크스페이스를 `/home/user/acdc-prep/`에 구축함. 이 사전준비의 핵심은 **"문제 풀이 환경·뼈대 세팅"**이며, 2025 문제는 참고용일 뿐 특정 형태에 밀착하지 않는다.

## 1. 대회 팩트 (✅ = 뉴스로 독립 교차검증됨)
- ✅ 주최 과기정통부 / 주관 KISA·KISIA. **2026이 2회차**(2025=제1회, 세계 최초 AI 해킹방어대회).
- ✅ **예선(온라인)**: 2026-10-31(토) 09:00~17:00. 신청 마감 2026-10-26(월) 14:00.
- ✅ **본선(오프라인)**: 2026-12-01(화) 그랜드 인터컨티넨탈 서울 파르나스. 시상 12-02.
- ✅ 예선 **분야별 상위 20팀(총 40팀)** → 본선.
- ✅ 참가: 대한민국 국적 만 19세↑, 일반부/학생부. 총상금 1억원+@(종합우승 5,000만원).
- ✅ **문제 3영역**: AI for Security · Security for AI · AI Platform Security.
- ✅ **본선 3방식 합산**: Attack&Defense(실시간 프롬프트 공방) + King of the Hill(과제수행 AI 개발·활용) + Secret Mission(비공개).
- 문의: qna@acdc2026.ai.kr

## 2. 예선 문제 형태 (참고용, ⚠️재검증 필요)
출처: 2025 참가자 write-up(velog @jsh1925). **직전 세션은 velog를 직접 못 열어(네트워크 차단) 사용자 요약만 신뢰. 새 세션은 브라우저로 원문 확인.**
※ **중요: 아래는 "이런 식으로 나올 수 있다"는 참고이지 맞춰야 할 스펙이 아님.** 문제는 다르게 나올 수 있으니 공통 단계(뼈대)만 준비한다.
- Jupyter 노트북으로 **제공 API와 실시간 통신** → 단계별 공격 → `Flag{...}`. Python/PyTorch.
- 대표 유형(참고): ① 적대적 공격(이미지 노이즈→안면인식/분류 오분류, .pth/.onnx) ② 프롬프트 인젝션/탈옥(챗봇 API에서 비밀키 Flag) ③ 인프라 융합(Docker/K8s 침투→모델파일 탈취·변조).
- ✅ 참가자들이 AI 도구를 적극 활용해 풀었음(예선에선 정상). ✅ 본선 A&D = 가드레일 프롬프트 방어 + 프롬프트 인젝션 공격.

## 3. 전략 핵심 — 뼈대 + ECC 리소스 풀
- **뼈대만 미리**: 공통 흐름(API 연결→공격→제출→Flag)과 유형별 범용 플레이북·템플릿만 세팅. 특정 문제에 밀착 X.
- **ECC를 자원 풀로 활용**: ECC(affaan-m/everything-claude-code)가 가장 큰 skill/agent 자원. **통짜 설치 안 함**(컨텍스트 낭비·저자 철학 위배, 핵심 기능은 이미 CC 네이티브). 대신 **로컬에 clone해 레퍼런스 라이브러리로 두고**, 문제 유형이 뜨면 거기서 관련 skill을 검색해 **필요한 것만** `.claude/skills/`로 복사.

## 4. 환경 전제
- **로컬 노트북에서 풀이**: RAM 16GB, 디스크 1TB, **GPU 제대로 못 씀 → CPU 기준.**
- 스택 **Python 확정**. 적대적 공격은 CPU 전제(소형 모델·적은 PGD 스텝·전이공격 고려).
- (참고) 이 준비 자체는 클라우드 세션에서 했지만, 실제 대회는 위 노트북에서 진행. acdc-prep 폴더는 그대로 노트북으로 옮겨 사용.

## 5. 구축된 워크스페이스 — `/home/user/acdc-prep/`
```
acdc-prep/
├── CLAUDE.md            # 앵커: 1인 풀이·CPU·뼈대·ECC활용·문제당 루틴
├── SETUP.md            # 설치(CPU torch)·ECC clone·규칙확인·유형별 연습
├── HANDOFF.md          # (이 문서)
├── lib/apiclient.py    # 공통: 연결/다운로드/제출/Flag 자동파싱 재사용
├── solutions/FLAGS.md  # 개인 진행/Flag 기록장
├── templates/
│   ├── notebook_starter.ipynb   # 문제마다 복제해 시작
│   ├── adversarial_attack.py    # FGSM/PGD(torchattacks+수동폴백)+검증+무손실저장 (CPU 자동)
│   ├── detection_baseline.py    # 탐지/분류 베이스라인
│   ├── llm_eval_harness.py      # 공격셋 성공률 측정
│   └── prompt_injection_tests.md# 인젝션 카테고리 체크리스트
└── .claude/skills/     # 유형별 범용 플레이북(지연로딩)
    ├── ctf-api-workflow/        # 모든 문제 공통 뼈대 — 먼저 열림
    ├── adversarial-attacks/     # 이미지/모델 오분류(+CPU 가이드)
    ├── prompt-injection/        # 챗봇 Flag 유도
    ├── ai-platform-security/    # Docker/K8s→모델파일 탈취
    └── ai-for-security/         # 탐지모델 개발(보조)
```
> 공격 스킬은 카테고리/방법 체크리스트 수준(실제 페이로드는 직접 창작). 자동 대량 질의·자동 제출봇은 규칙 확인 전까지 금지로 명시.

## 6. 아직 확정 안 됨 — 새 세션이 확인/결정할 것
- [ ] **규칙**: 대상 API 자동 대량 질의 허용? 레이트리밋? (요강/qna)
- [ ] **본선** AI·인터넷 허용 여부(예선과 다를 수 있음, 폐쇄망 가능성).
- [ ] **velog write-up 원문 재검증**(§8 링크, 브라우저로).
- [ ] ECC에서 실제로 가져올 만한 skill/agent 추려두기(문제 전 미리 후보만).
- [ ] `lib/apiclient.py`를 실제 API 패턴(이미지 멀티파트 제출 등)에 맞출지(문제 보고 판단).

## 7. 새 세션 추천 다음 스텝
1. **브라우저로 §8 링크 열어 예선 문제 형태 1차출처 확인**(직전 세션이 차단돼 못 봄).
2. ECC clone 훑어 유형별로 가져올 skill 후보 선별(통짜 설치는 금지).
3. 유형별 범용 연습: 적대적(torchattacks, CPU) / 인젝션(Gray Swan Proving Ground) / 인프라(pickle RCE·K8s).
4. 본선 전략은 예선 후 별도(A&D 가드레일, KOTH eval harness).

## 8. 확인해야 할 링크 (직전 세션은 네트워크 차단으로 못 열었음 → 브라우저로 열람)
- 2025 예선 참가자 write-up: https://velog.io/@jsh1925/2025-ACDC-해킹방어대회-Write-Up
- 2025 본선 A&D 후기: https://blog.realsung.kr/2025/12/04/2025-ACDC-Final/
- KISA 2025 보도자료: https://www.kisa.or.kr/402/form?postSeq=2538 , https://kisa.or.kr/402/form?postSeq=2558
- 2026 ACDC 공고(원본): https://www.kisa.or.kr/401/form?postSeq=3780
- ECC 저장소: https://github.com/affaan-m/everything-claude-code
- roboco ECC 해설: https://roboco.io/en/posts/everything-claude-code-distilled/

## 9. 환경 주의 (중요)
직전 세션은 **클라우드 컨테이너**라 roboco/grayswan/kisa/velog/realsung 등 외부 도메인 대부분이 **프록시 allowlist에 막혀 직접 접속 불가**였음. 그래서 상당수 사실은 **사용자 붙여넣기 + 웹검색 스니펫** 기반이고, ✅ 표시만 뉴스로 독립 교차검증된 것. 새 세션/브라우저는 직접 열람 가능하니 **1차 출처 재확인을 우선**할 것.
