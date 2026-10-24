# 2026 ACDC 예선 워크스페이스

AI Cyber Defense Contest 2026 예선(2026-10-31 09:00~17:00, 온라인) 풀이 환경.

## 전제
- **1인 풀이.** 사용자가 직접 문제를 읽고 판단하고, Claude는 분석·코드·실행을 돕는다.
- **로컬 노트북, CPU 전용**(RAM 16GB, GPU 없음). 무거운 연산은 작은 모델·적은 스텝으로 설계.
- 스택은 Python. 문제는 보통 Jupyter 노트북 + 제공 API 형태이며 `Flag{...}`를 찾는다.
- 2025 문제 형태는 참고일 뿐. 특정 형태에 맞추지 말고 공통 뼈대로 접근.

## 문제당 루틴
1. 문제 설명·제공 파일·API 엔드포인트를 그대로 읽고 **영역 분류**
   (AI for Security / Security for AI / AI Platform Security).
2. `ctf-api-workflow` skill을 먼저 따른다. 그다음 유형별 skill
   (`prompt-injection`, `adversarial-attacks`, `ai-platform-security`, `ai-for-security`).
3. `templates/notebook_starter.ipynb`를 `solutions/<문제명>/`로 복제해서 시작.
   API 통신은 `lib/apiclient.py`를 재사용.
4. 시도와 결과를 노트북에 남기고, Flag를 찾으면 `solutions/FLAGS.md`에 기록.

## 도구
- **Jupyter MCP**(`.mcp.json`의 `jupyter`): `scripts/start_jupyter.sh`로 Jupyter Lab을 먼저 띄운 뒤 사용.
  노트북 셀을 직접 실행하고 출력을 읽어 반복 실험한다.
- **context7 MCP**: torch / torchattacks / onnxruntime / kubernetes 등 라이브러리 최신 문서 조회.
- ECC 원본 전체는 `scripts/fetch_ecc.sh`로 `third_party/ecc/repo/`에 받아 **검색용 레퍼런스**로만 쓴다.
  필요한 skill만 `.claude/skills/`로 복사(통짜 설치 금지).

## 규칙
- 대회 규칙(요강/qna@acdc2026.ai.kr)에서 허용 여부가 확인되기 전에는
  **대상 API에 자동 대량 질의, 자동 제출 봇을 쓰지 않는다.** 소량의 수동/반자동 시도만.
- 대회가 제공한 대상 외의 시스템은 건드리지 않는다.
- 인젝션 페이로드는 문제 상황에 맞게 직접 만든다. skill에는 카테고리와 방법만 있다.
