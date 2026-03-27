---
name: fetch-data
description: 공공데이터포털 유기동물 공고 API에서 데이터를 수집하고, D-day 기준으로 정렬하여 파이프라인에 전달
triggers:
  - "유기동물 데이터 수집"
  - "공고 데이터 가져오기"
  - "fetch animal data"
---

# Fetch Data Skill

## Purpose
공공데이터포털 유기동물 보호 공고 API를 호출하여 데이터를 수집하고,
manifesto의 객관성 원칙에 따라 정제한 뒤 파이프라인 다음 단계로 전달합니다.

**반드시 먼저 읽기**: `manifesto.txt` §4 객관성 원칙, `gotchas.md` Category: fetch

---

## Pre-run Checklist (ACTIVE Gotchas)

실행 전 반드시 확인:
- [ ] GOTCHA-001: `noticeEdt` 날짜 파싱은 `%Y%m%d` 형식 사용
- [ ] GOTCHA-002: `totalCount` 확인 후 페이지네이션 루프 실행
- [ ] GOTCHA-003: `filename` null 레코드는 `no_image` 플래그 후 분리
- [ ] GOTCHA-009: `d_day < 0` 레코드는 `expired` 플래그 후 파이프라인 제외

---

## Process

### Step 1 — API 인증 및 요청 준비
- 환경변수 `ANIMAL_API_KEY` 로드 (하드코딩 금지)
- 요청 파라미터:
  - `serviceKey`: API 인증키
  - `numOfRows`: 100 (기본 10 사용 금지 — GOTCHA-002)
  - `pageNo`: 1부터 시작
  - `_type`: json
  - `state`: notice (공고중인 동물만)

### Step 2 — 전체 데이터 수집 (페이지네이션)
- 첫 요청 후 `totalCount` 확인
- `totalCount > numOfRows`이면 `ceil(totalCount / numOfRows)` 페이지 반복 요청
- 모든 레코드를 단일 리스트로 병합

### Step 3 — D-day 계산
- 각 레코드의 `noticeEdt` → `datetime.strptime(date, "%Y%m%d")` (GOTCHA-001)
- `d_day = (notice_end_date - today).days`
- `d_day < 0` → `status: expired` 플래그, 파이프라인 제외 (GOTCHA-009)
- `d_day == 0` → `status: urgent`
- `d_day <= 3` → `status: critical`
- `d_day > 3` → `status: normal`

### Step 4 — 이미지 URL 검증
- `filename` 필드 null 체크 (GOTCHA-003)
- null인 경우: `image_status: no_image` 플래그, 별도 큐로 분리
- 유효한 경우: `image_status: ok`

### Step 5 — 우선순위 정렬
- 1순위: `status: urgent` (D-day = 0)
- 2순위: `status: critical` (D-day 1–3)
- 3순위: `status: normal`
- 동일 우선순위 내: `d_day` 오름차순

### Step 6 — 출력 스키마 검증
각 레코드가 다음 필드를 포함하는지 확인:
```
desertionNo, filename, happenDt, happenPlace, kindCd,
colorCd, age, weight, noticeNo, noticeSdt, noticeEdt,
popfile, processState, sexCd, neuterYn, specialMark,
careNm, careTel, careAddr, orgNm, chargeNm, officetel,
d_day, status, image_status
```

### Step 7 — 결과 저장
- `Scripts/output/animals_YYYYMMDD.json` 에 저장
- `Scripts/output/no_image_YYYYMMDD.json` 에 이미지 없는 레코드 별도 저장

---

## Output Schema
```json
{
  "fetch_date": "YYYY-MM-DD",
  "total_fetched": 150,
  "pipeline_ready": 142,
  "expired_skipped": 5,
  "no_image_queued": 3,
  "animals": [
    {
      "desertionNo": "202600001234",
      "noticeNo": "충남-천안-2026-00123",
      "careNm": "천안시 유기동물보호소",
      "careTel": "041-000-0000",
      "kindCd": "[개] 말티즈",
      "age": "2024(년생)",
      "sexCd": "M",
      "neuterYn": "Y",
      "specialMark": "온순함, 사람을 좋아함",
      "d_day": 2,
      "status": "critical",
      "image_status": "ok",
      "filename": "http://..."
    }
  ]
}
```

---

## Script
`Scripts/fetch_animals.py` 참조

## Templates
`Templates/api_params.json` — API 기본 파라미터 템플릿
