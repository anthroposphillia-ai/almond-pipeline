---
name: create-video
description: 동물 이미지와 오버레이 텍스트를 합성하여 플랫폼별 AI 영상을 생성
triggers:
  - "영상 생성"
  - "비디오 만들기"
  - "create video"
---

# Create Video Skill

## Purpose
generate-content 스킬의 출력(오버레이 텍스트)과 fetch-data의 이미지 URL을 결합하여,
플랫폼별 규격에 맞는 AI 영상을 생성합니다.

**반드시 먼저 읽기**: `manifesto.txt` §2 투명성(워터마크), `gotchas.md` Category: video

---

## Pre-run Checklist (ACTIVE Gotchas)

- [ ] GOTCHA-006: 대상 플랫폼 명시적 지정. 미지정 시 9:16(1080x1920) 기본값
- [ ] GOTCHA-007: AI 워터마크는 필수 레이어 — 제거 불가

---

## Platform Presets

```python
PLATFORM_PRESETS = {
    "instagram_reels": {"width": 1080, "height": 1920, "fps": 30, "duration": 15},
    "youtube_shorts":  {"width": 1080, "height": 1920, "fps": 30, "duration": 30},
    "tiktok":          {"width": 1080, "height": 1920, "fps": 30, "duration": 15},
    "default":         {"width": 1080, "height": 1920, "fps": 30, "duration": 15},
}
```

---

## Process

### Step 1 — 입력 검증
- `generate-content` 출력의 `validation.manifesto_pass: true` 확인
- `false`이면 이 스킬로 진입 불가 — generate-content로 반환
- 이미지 URL 접근 가능 여부 확인 (HTTP HEAD 요청)

### Step 2 — 이미지 다운로드 및 전처리
- `filename` URL에서 이미지 다운로드
- 이미지 규격 확인 및 플랫폼 프리셋에 맞게 리사이즈/크롭
- 9:16 비율 기준으로 center-crop

### Step 3 — 영상 레이어 구성 (순서 고정)
```
Layer 0 (배경): 동물 이미지 (kenburns 효과 — 부드러운 줌)
Layer 1 (D-day 배지): 좌상단, 반투명 배경
Layer 2 (타이틀): 품종·나이·성별, 중앙 하단 1/3 지점
Layer 3 (보호소 정보): 하단, 공고번호·연락처
Layer 4 (워터마크): 우하단 고정, "AI-generated | 실제 유기동물 정보" (제거 불가 — GOTCHA-007)
```

### Step 4 — 영상 렌더링
- `Scripts/create_video.py` 실행
- ffmpeg 기반 렌더링
- 출력: `Scripts/output/video_{desertionNo}_{platform}.mp4`

### Step 5 — 품질 검증
- 파일 크기 > 0 확인
- 재생 시간이 프리셋과 일치하는지 확인
- 워터마크 레이어 존재 확인 (메타데이터 기록으로 추적)

### Step 6 — 결과 저장
```
Scripts/output/
  video_{desertionNo}_instagram.mp4
  video_{desertionNo}_youtube.mp4
  video_{desertionNo}_tiktok.mp4
  video_{desertionNo}_manifest.json  ← 생성 메타데이터
```

---

## Output Schema
```json
{
  "desertionNo": "202600001234",
  "videos": {
    "instagram_reels": {
      "path": "Scripts/output/video_202600001234_instagram.mp4",
      "size_mb": 8.2,
      "duration_sec": 15,
      "watermark_verified": true
    }
  },
  "render_time_sec": 12.4,
  "status": "success"
}
```

## Script
`Scripts/create_video.py`

## Templates
`Templates/video_config.json` — 렌더링 파라미터 템플릿
