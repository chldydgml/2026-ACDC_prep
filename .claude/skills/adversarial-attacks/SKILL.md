---
name: adversarial-attacks
description: 적대적 공격/얼굴인식 우회(Security for AI) 문제용 — 제공된 이미지를 조작해 분류·안면인식 모델을 속이고, 성공조건(예 confidence>0.8 AND cosine_distance>0.2)을 만족하는 이미지를 API로 제출해 Flag를 얻는다. 블랙박스 API 피드백 루프 + 이미지 편집(seamless cloning 등)이 주력, 가중치 제공 시 FGSM/PGD. PyTorch/OpenCV. 이미지로 모델 우회하는 문제를 받으면 연다.
---
# 적대적 공격 / 얼굴인식 우회 플레이북
2025 예선(CTF1 Spoof) 교훈: **대부분 블랙박스**(모델 가중치 없음). 서버 API가 주는
`confidence`/`cosine_distance`/`is_adversarial`를 **신호로 삼아 반복**하며, 승리기법은
gradient가 아니라 **이미지 편집(seamless cloning) + 파라미터 스윕**이었다.
## 1. 먼저 파악 (실패 방지)
- **문제 힌트부터 읽기**: 제공 노트북이 기법·라이브러리(seamless cloning, ART/Foolbox, face_alignment, StyleGAN 등)를 직접 알려준다.
- **성공조건 정확히**: 종종 **두 지표 동시**다. 예) 원본과 충분히 닮음(confidence>0.8) **AND** 충분히 변형(cosine_distance>0.2). → "너무 똑같아도, 너무 달라도" 실패.
- **접근**: 블랙박스(API 질의만) / 화이트박스(.pth·.onnx 제공)?
- **입출력 스펙**: 해상도·채널순서(RGB/BGR)·정규화·저장포맷. 서버와 100% 일치.
## 2. 블랙박스 (기본값) — API 피드백 루프 ★
가중치가 없으니 **API 지표를 보고 파라미터를 스윕**한다.
- 이미지 편집 기법: **seamless cloning**(`cv2.seamlessClone`, NORMAL/MIXED), 블렌딩, 모핑, face-swap, 포아송 블렌딩, 액세서리/패턴.
- 루프: 파라미터(shift/강도/영역) 바꿔가며 → 제출 → 지표 읽기 → 조건 만족 시 중단.
  `lib/apiclient.py` 의 `Challenge.sweep(values, make_img, check, endpoint)` 사용.
  ```python
  c.sweep(range(5, 30, 2),
          make_img=lambda s: clone_at(ceo, shift=s),
          check=lambda r: r.get("success"),
          path=CTF_VERIFY)
  ```
- 서버 왕복/레이트리밋 주의 — 스윕 간격을 크게 잡고 좁혀가기(이진탐색).
- OpenCV는 BGR: `cv2.cvtColor(..., COLOR_RGB2BGR)` ↔ 제출 전 다시 RGB/JPEG.
## 3. 화이트박스 (가중치 제공 시)
- `.pth`→PyTorch 로드(아키텍처 필요), `.onnx`→onnxruntime. `templates/adversarial_attack.py`.
- `torchattacks`: FGSM/PGD/CW. targeted면 `set_mode_targeted_by_label()`.
- 손으로: FGSM=`x+eps*sign(grad)`, PGD=반복+eps투영.
## 4. CPU 전제 (로컬 노트북, GPU 약함)
- 소형 모델·입력부터, PGD 스텝 10~30. 큰 모델은 작은 대리모델→전이공격.
- 블랙박스 이미지 편집은 CPU로 충분(무거운 건 API 왕복이지 연산이 아님).
## 5. 제출 전 체크 / 함정
- 성공조건(두 지표)이 **로컬에서 재현**되는가(블랙박스면 지표를 서버에서만 알 수 있으니 스윕).
- **전처리 불일치**가 실패 1위 — 정규화/리사이즈/채널순서.
- **JPEG 재저장 압축**으로 섭동 소실 → 조건 애매하면 PNG 등 무손실 검토(단 서버가 JPEG 요구하면 맞춤).
