# 2026 ACDC 예선 워크스페이스

AI Cyber Defense Contest 2026 예선(2026-10-31 09:00~17:00, 온라인) 풀이 환경.

## 전제
- **이 환경 사용자 2인**(+별도 환경의 팀원 2인, 총 4인 팀). 사용자가 문제를 읽고 판단하고,
  Claude는 분석·코드·실행을 돕는다. 팀 내 협업은 허용, 타 팀과 공유는 금지.
- **로컬 노트북, CPU 전용**(RAM 16GB, GPU 없음). 무거운 연산은 작은 모델·적은 스텝으로 설계.
- 스택은 Python. 예선은 **① 문제풀이(Jeopardy) + ② KotH(거점 점령) 2트랙**이며 최종 순위는 둘 합산.
  Jeopardy는 보통 Jupyter 노트북 + 제공 API로 `Flag{...}`/`ACDC{...}`를 찾고,
  KotH는 제공된 시스템을 점령·방어하며 **점유 시간**으로 득점한다.
- 2025 문제 형태는 참고일 뿐(2025 예선은 Jeopardy 단독, KotH는 2026 신규). 특정 형태에 맞추지 말고 공통 뼈대로 접근.

## 문제당 루틴
1. 문제 설명·제공 파일·API 엔드포인트를 그대로 읽고 **영역 분류**
   (AI for Security / Security for AI / AI Platform Security).
2. `ctf-api-workflow` skill을 먼저 따른다. 그다음 유형별 skill
   (`prompt-injection`, `adversarial-attacks`, `ai-platform-security`, `ai-for-security`).
   **거점 점령형이면 `koth` skill**(유지 루프는 `templates/koth_loop.py`).
3. `templates/notebook_starter.ipynb`를 `solutions/<문제명>/`로 복제해서 시작.
   API 통신은 `lib/apiclient.py`를 재사용.
4. 시도와 결과를 노트북에 남기고, Flag를 찾으면 `solutions/FLAGS.md`에 기록.
   (KotH는 Flag가 아니라 점유 유지가 목표 — `koth` skill 참고, 점유 로그는 `koth.events.jsonl`.)

## 도구
- **Jupyter MCP**(`.mcp.json`의 `jupyter`): `scripts/start_jupyter.sh`로 Jupyter Lab을 먼저 띄운 뒤 사용.
  노트북 셀을 직접 실행하고 출력을 읽어 반복 실험한다.
- **context7 MCP**: torch / torchattacks / onnxruntime / kubernetes 등 라이브러리 최신 문서 조회.
- ECC 원본 전체는 `scripts/fetch_ecc.sh`로 `third_party/ecc/repo/`에 받아 **검색용 레퍼런스**로만 쓴다.
  필요한 skill만 `.claude/skills/`로 복사(통짜 설치 금지).

## 규칙
- **자동화**: DoS/DDoS·과도한 자동 요청·대량 스캔/퍼징은 **항상 금지**(요강 명시).
  Jeopardy는 소량의 수동/반자동 시도만. KotH는 **채점 틱에 맞춘 얌전한 주기 루프는 허용**
  (과도하지 않게, 밀렸을 때만 재탈환 — `templates/koth_loop.py`).
- 공격 대상 = **대회가 제공한 격리 환경만**. 운영서버·점수판·관리자 기능·타 팀 기기/계정·외부 시스템 금지.
- 시각 기준 KST, 종료 시각 이전에 대회 서버에 접수된 것만 인정. 플랫폼 결함은 악용 말고 운영진 신고.
- 인젝션 페이로드는 문제 상황에 맞게 직접 만든다. skill에는 카테고리와 방법만 있다.
- 문의/소통: 공식 Discord 및 qna@acdc2026.ai.kr. (플랫폼 접속테스트 10/30 13:00~)
