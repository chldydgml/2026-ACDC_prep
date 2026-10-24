---
name: ai-platform-security
description: AI 플랫폼/인프라 보안(AI Platform Security) 문제용 — JWT 등 웹 인증 우회로 권한상승, Docker·Kubernetes 침투로 내부 AI 모델파일(.pth/.onnx) 탈취·변조, 서빙 API·RAG·벡터DB·MCP·공급망 취약점 공략으로 Flag 획득. 전통 웹/인프라 보안과 AI가 결합된 문제를 받으면 연다.
---
# AI 플랫폼 / 인프라 보안 플레이북
2025 예선 유형: 인프라(K8s/Docker) 침투 → 내부 모델파일(.pth/.onnx) 탈취/변조. 전통 appsec 결합.
참고: OWASP ML Top 10, OWASP LLM Top 10(인프라), MITRE ATLAS.
## 1. 공격면 매핑 (recon — 서브에이전트 활용)
- 노출된 엔드포인트/포트/대시보드, 서빙 API, 쿠버네티스/도커 API, 레지스트리, 오브젝트 스토리지.
- 인증·인가 경계, 입력 지점, 파일 업/다운로드 경로.
## 2. 자주 나오는 결정적 취약점
- **역직렬화 RCE**: 신뢰 못 할 `.pth`/pickle `torch.load` → 임의코드 실행(공격). 방어: `safetensors`/허용목록/`weights_only=True`.
- **노출된 K8s/Docker API**: 비인증 kubelet/API, Docker socket 마운트 → 컨테이너 탈출/파드 생성 → 모델파일 접근.
- **경로/SSRF/LFI**: 서빙 API를 통해 내부 파일(.pth/.onnx)·메타데이터 접근.
- **비밀 노출**: env/설정/로그/레지스트리 토큰에서 자격증명.
- **공급망**: 신뢰 못 할 베이스 이미지·모델 체크포인트·의존성.
- **RAG 간접 인젝션**: 인덱스 문서에 지시 심기(→ prompt-injection 스킬 연계).
## 2b. JWT / 웹 인증 우회 ★ 예선 실출제(PAIR Matching)
서빙/벡터DB 서비스가 JWT로 권한을 나눌 때. role=guest→admin만으론 **서명검증에 막힘** → 서명을 위조해야.
`templates/jwt_attack.py` 사용. 먼저 `decode()`로 header/payload 정찰.
- **RS256→HS256 알고리즘 혼동** (최유력): 헤더가 `alg:RS256`이고 **공개키가 노출**(`jku:/public.pem`, `/public.pem`, x5u, JWKS)되면,
  그 **공개키 PEM을 HMAC 비밀키로 써서 HS256 서명** → 서버가 같은 공개키로 검증 시 통과.
  `alg_confusion_variants(payload, "public.pem", extra_header={"jku": "/public.pem"})` 로 바이트변형 모두 시도.
  → **공개키 노출(jku=/public.pem) 자체가 이 공격을 노린 떡밥.**
- **none alg**: `alg:none`, 서명 제거(서버가 허용 시).
- **kid 주입**: `kid` 경로순회(`../../dev/null`로 빈 키)·SQLi로 서명키 제어.
- **jku/x5u 주입**: 공격자 호스팅 JWKS(외부 접속 막히면 동일 오리진/오픈리다이렉트 경유).
- 위조 성공 신호: 새 UI/탭 노출 + "유효 토큰" 통과. role뿐 아니라 **session_id 등 payload 전체**가 서명 안에 유효해야 함.
- 도구: `templates/jwt_attack.py`(무의존), 또는 `jwt_tool`(ticarpi), PyJWT.
## 3. 모델파일 취급
- `.pth`: 아키텍처 필요, 로드 시 역직렬화 위험 인지.
- `.onnx`: onnxruntime로 추론, `onnx` 로 그래프 점검, 변조 시 가중치 수정.
- 탈취 후 제출 요구면 해시/서명 조건 확인.
## 4. 도구
```
trivy image <img> / trivy fs .      # 취약점·비밀 스캔
semgrep --config auto .             # 코드 취약점
kubectl get/describe, docker inspect
pip-audit                           # 의존성
```
## 5. 접근 순서
1. 공격면 매핑 → 2. 가장 임팩트 큰 취약점부터 → 3. 모델파일 접근/변조 →
4. 성공 조건 로컬 확인 → 5. 제출·Flag → 6. `solutions/`·`FLAGS.md` 기록.
