---
name: generate-content
description: 유기동물 데이터를 기반으로 manifesto 원칙을 준수하는 캡션과 영상 스크립트를 생성
triggers:
  - "캡션 생성"
  - "콘텐츠 생성"
  - "generate caption"
---

# Generate Content Skill

## Purpose
fetch-data 스킬의 출력을 입력으로 받아, manifesto의 저자극성·투명성·존엄성 원칙에 따라
SNS 배포용 캡션과 영상 내 텍스트 오버레이를 생성합니다.

**반드시 먼저 읽기**: `manifesto.txt` §1 저자극성, §2 투명성, `gotchas.md` Category: content

---

## Pre-run Checklist (ACTIVE Gotchas)

- [ ] GOTCHA-004: 생성 후 `validate_against_manifesto()` 실행 — 금지 표현 감지 시 재생성
- [ ] GOTCHA-005: 필수 필드(보호소ID, 공고번호, AI명시, 문의처) 포함 여부 검증

---

## Process

### Step 1 — 입력 데이터 로드
- `fetch-data` 출력 JSON에서 단일 동물 레코드 로드
- `image_status: no_image` 레코드는 이 스킬로 진입 불가 — 에러 반환

### Step 2 — D-day 표현 생성
```
d_day == 0 → "⏰ 오늘이 마지막 날 | D-0"
d_day == 1 → "D-1"
d_day <= 3 → "D-{n} (긴급)"
d_day > 3  → "D-{n}"
```
- "곧 죽습니다", "마지막 기회" 등 감정적 표현 금지 (manifesto §1)

### Step 3 — 동물 특성 텍스트 생성
- `specialMark` 필드를 기반으로 객관적 특성 3줄 이내 요약
- `kindCd`에서 품종 추출 (예: "[개] 말티즈" → "말티즈")
- 나이는 계산: 현재 연도 - 태어난 연도 + "살 추정"
- 성별: M→수컷, F→암컷, Q→미상
- 중성화: Y→중성화 완료, N→미완료, U→미상

### Step 4 — 캡션 생성
`Templates/caption_template.md` 를 기반으로 생성.
모든 변수를 실제 데이터로 치환.

### Step 5 — Manifesto 검증
`Scripts/validate_content.py` 의 `validate_against_manifesto()` 실행:
- 금지 표현 목록 대조 (manifesto §1)
- 필수 필드 포함 여부 확인 (manifesto §2)
- 실패 시: 재생성 요청 (최대 3회)
- 3회 실패 시: `status: human_review` 플래그 후 human review 큐로 이동

### Step 6 — 영상 오버레이 텍스트 생성
`Templates/overlay_template.json` 기반으로 영상에 삽입될 텍스트 레이어 생성:
- 타이틀: 품종 + 나이
- 서브타이틀: D-day
- 하단 정보: 보호소명 + 공고번호
- 워터마크: "AI-generated | 실제 유기동물 정보"

### Step 7 — 결과 저장
`Scripts/output/content_{desertionNo}.json`

---

## Output Schema
```json
{
  "desertionNo": "202600001234",
  "caption": {
    "ko": "...",
    "en": "..."
  },
  "overlay": {
    "title": "말티즈 · 수컷 · 2살 추정",
    "d_day_badge": "D-2 (긴급)",
    "shelter_info": "천안시 유기동물보호소 | 공고 충남-천안-2026-00123",
    "watermark": "AI-generated video | 실제 유기동물 정보 기반",
    "contact": "041-000-0000"
  },
  "validation": {
    "manifesto_pass": true,
    "required_fields_pass": true,
    "attempts": 1
  }
}
```

## Script
`Scripts/generate_caption.py`, `Scripts/validate_content.py`

## Templates
`Templates/caption_template.md`, `Templates/overlay_template.json`
