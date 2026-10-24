---
name: ai-for-security
description: AI/ML을 활용해 보안 작업을 수행(AI for Security)하는 문제용 플레이북 — 로그·트래픽 이상탐지, 악성코드·피싱 분류, 코드 취약점 탐지, 자동 트리아지 등을 빠르게 개발. ACDC 예선에서 "AI를 활용한 보안" 영역 문제를 받았을 때 연다.
---
# AI for Security 플레이북
핵심: "AI로 보안 문제를 **푸는 산출물**(모델/파이프라인/스크립트)"을 만든다. 정확도·시간이 점수.
## 1. 문제 분류 먼저
- 입력 데이터 유형: 로그/패킷 / 바이너리·악성코드 / 소스코드 / 텍스트(피싱·이메일)?
- 산출물: 분류/탐지 모델? 탐지 룰? 리포트?
- 평가지표: accuracy/F1 / 탐지율 / 처리속도?
## 2. 빠른 베이스라인 → 개선 (시간 분배)
1. **데이터 즉시 파악**: 라벨 분포, 결측, 피처 종류. (`pandas`, 서브에이전트로 EDA 위임)
2. **싸고 강한 베이스라인 먼저**:
   - 표/피처형 → GradientBoosting(`xgboost`/`lightgbm`) 또는 RandomForest.
   - 텍스트 → TF-IDF + 선형모델, 또는 소형 임베딩 + 로지스틱.
   - 로그/시퀀스 이상탐지 → IsolationForest / 통계적 임계값부터.
3. **그 다음** 딥러닝/LLM은 시간 남을 때만. 과제가 LLM 활용을 요구하면 few-shot 프롬프트 분류부터.
4. 베이스라인 스캐폴드: `templates/detection_baseline.py`
## 3. LLM을 "보안 도구"로 쓰는 패턴
- 코드 취약점 탐지: 함수 단위로 쪼개 LLM에 점검 → 룰/정적분석(`bandit`,`semgrep`)과 교차검증.
- 로그 트리아지: 정상/이상 few-shot 분류 + 근거 추출.
- 반드시 **결정적 검증기와 결합**(LLM 단독 판단 신뢰 금지).
## 4. 자주 쓰는 설치
```
pip install pandas scikit-learn lightgbm xgboost numpy
# 텍스트: sentence-transformers  / 정적분석: bandit semgrep
```
## 5. 함정
- 리더보드 과적합: 검증셋 분리, 랜덤시드 고정, 재현성 확보.
- 전처리에서 라벨 누수 주의. 시간 대비 효과 낮은 튜닝에 매몰되지 말 것 — 베이스라인 제출부터.
