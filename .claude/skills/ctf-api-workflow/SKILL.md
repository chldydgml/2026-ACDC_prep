---
name: ctf-api-workflow
description: ACDC 예선의 모든 문제에 공통인 뼈대 — 제공된 API 서버에 연결하고, 타깃 데이터를 다운로드하고, 공격을 코드로 구현해 결과를 제출하고, 응답에서 Flag를 받아내는 흐름. Jupyter/Python으로 API와 실시간 통신하는 문제를 시작할 때 가장 먼저 연다.
---
# CTF API 워크플로우 (모든 문제 공통)
2025 예선 패턴: 준비 → 데이터 다운로드 → 공격 구현 → 제출 → `Flag{...}`.
## 재사용 컴포넌트
- `lib/apiclient.py` 의 `Challenge` 클래스: 연결/다운로드/제출/Flag 자동 파싱.
- `templates/notebook_starter.ipynb`: 바로 복제해 문제별 노트북 시작.
## 단계
1. **준비**: 문제 안내에서 base URL·인증토큰·제출 포맷 확보. `.env`에 넣기.
   ```python
   from lib.apiclient import Challenge, find_flag
   c = Challenge(BASE_URL, token=TOKEN)
   ```
2. **탐색(recon)**: 제공 엔드포인트 나열, 샘플 요청으로 응답 구조 파악. (대량 탐색은 서브에이전트)
3. **데이터 다운로드**: `c.download("/target", "data/target.png")` 등. 입력 스펙(크기/정규화) 기록.
4. **공격 구현**: 유형에 맞는 스킬로 이동
   - 이미지/모델 오분류 → `adversarial-attacks`
   - 챗봇 Flag 유도 → `prompt-injection`
   - 인프라 침투/모델 탈취 → `ai-platform-security`
5. **로컬 검증**: 제출 전에 "성공 조건"을 로컬에서 먼저 만족시키기(서버 왕복 아끼기).
6. **제출 & Flag**: `r, flag = c.submit("/submit", files=..., json=...)`.
7. **기록**: `solutions/<문제명>/`에 노트북+산출물 저장, `solutions/FLAGS.md` 갱신.
## 효율 원칙
- **서버 왕복 최소화**: 성공 판정을 로컬에서 재현한 뒤 제출. (레이트리밋·규칙 보호)
- 반복 요청 전 **자동 질의 허용 여부 확인**.
- 공통 유틸은 `lib/`에 쌓아 다음 문제에서 재사용.
- 입력 전처리(정규화/리사이즈) 불일치가 실패 1순위 원인 → 서버 스펙과 정확히 맞출 것.
