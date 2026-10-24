# 모의 문제 — 적대적 이미지 회피 (리허설용)

> 적대적 이미지 유형 환경을 검증하는 **로컬 연습 대상**. 실제 대회 서버가 아니다.
> `adversarial-attacks` 스킬이 말하는 **블랙박스 API 피드백 루프**가 주력인 형태.

## 문제 설명 (이대로 Claude에게 줘도 됨)
> 이미지 분류기(`http://127.0.0.1:9001`)가 고양이/개를 판별한다. 원본 'cat' 이미지를
> `GET /image` 로 받고, **L∞ 섭동 budget(16) 이내**로만 바꿔서 분류기가 'dog'(confidence>0.8)
> 로 **오분류**하게 만들어 `POST /submit` 하면 Flag를 준다. `POST /predict` 로 피드백을 받을 수 있다.

- 영역: **Security for AI** (적대적 예제 / 모델 회피)
- 성공 조건: `class=="dog"` AND `confidence>0.8` AND `L∞(제출, 원본) <= 16`
- 유형: **블랙박스** (모델 가중치 없음, API 피드백만). torch 불필요 — numpy로 충분.

## 실행
설치(`SETUP.md`)가 끝났다고 가정. **torch 없이 기본 설치만으로 동작**한다.
```bash
# 해당 폴더에서 직접
cd challenges/mock-adversarial && ../../.venv/bin/python server.py
# 또는 uvicorn
.venv/bin/python -m uvicorn --app-dir challenges/mock-adversarial server:app --port 9001
```
확인:
```bash
curl -s http://127.0.0.1:9001/            # 안내 JSON (budget/임계값/성공조건)
curl -s -o /tmp/base.png http://127.0.0.1:9001/image && echo "원본 저장됨"
```

## 푸는 쪽(리허설)
1. `solutions/mock-adversarial/solve.ipynb` (BASE_URL 이 `http://127.0.0.1:9001` 로 프리셋).
2. `ctf-api-workflow` → `adversarial-attacks` 스킬 순서로 접근.
3. `c.download('/image', ...)` 로 원본을 받고, `c.post_image_file('/predict', img)` 로 분류를 찍어
   **규칙을 추론**(무엇을 바꾸면 class가 흔들리나), 작은 섭동으로 뒤집어 `c.submit('/submit', ...)`.
4. `ACDC{...}` 가 나오면 `lib/apiclient.py` 가 자동 출력 → `solutions/FLAGS.md` 기록.

## 구성
- `model.py` — 블랙박스 분류기 + budget/성공 판정. 순수 numpy.
- `server.py` — FastAPI 래퍼. `/`, `/image`, `/predict`, `/submit`.

## 참고 — torch 는 언제 필요한가
- 이 문제는 **블랙박스**라 numpy만으로 푼다(기본 설치 OK).
- **화이트박스**(대회가 `.pth`/`.onnx` 가중치를 주는 경우)면 그때 FGSM/PGD로 그래디언트 공격을 하며,
  `scripts/bootstrap_ubuntu.sh --torch` 로 torch 를 설치하고 `templates/adversarial_attack.py` 를 쓴다.

---

<details>
<summary><b>SPOILER — 의도된 풀이 (리허설 전엔 펼치지 마세요)</b></summary>

분류 규칙은 **평균 R - 평균 B**. 양수면 cat, 음수면 dog. 원본은 평균 R 이 평균 B 보다 약간 커서
(score≈+12.7) cat 으로 분류된다. 모든 픽셀에서 **R 을 16 낮추고 B 를 16 올리면**(= L∞ 16, budget 딱)
score 가 약 -32 만큼 이동해 음수가 되고, dog(confidence≈0.96)로 뒤집혀 성공한다.

블랙박스 관점: `/predict` 로 원본이 cat 임을 보고, 채널별로 조금씩 바꿔 confidence 변화를 관찰하면
"R↓/B↑ 가 dog 쪽" 임을 추론할 수 있다. 섭동이 모자라면 `'dog' 이지만 confidence<=0.8` 피드백이 온다.
</details>
