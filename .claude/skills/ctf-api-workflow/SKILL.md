---
name: ctf-api-workflow
description: Common skeleton for every ACDC challenge — read the problem, classify the area, probe the provided API/notebook, attack in small steps, capture Flag{...}. Use first on any new ACDC/AI-security CTF problem before a type-specific skill.
---

# ACDC 문제 공통 뼈대

## 0. 시작 (5분)
- 문제 설명, 제공 파일, 엔드포인트, 노트북을 **그대로** 읽는다. 추측 금지, 적힌 것부터.
- 영역 분류 → 다음 skill 선택:
  - 챗봇/LLM 응답에서 비밀 빼기 → `prompt-injection`
  - 이미지/모델 오분류, .pth/.onnx 제공 → `adversarial-attacks`
  - Docker/K8s/서버 침투, 모델 파일 탈취·변조 → `ai-platform-security`
  - 탐지 모델 만들기·성능 기준 통과 → `ai-for