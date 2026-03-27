---
name: distribute
description: 생성된 영상을 플랫폼별로 배포하고, 중복 배포 방지 및 최종 승인 게이트를 운영
triggers:
  - "영상 배포"
  - "SNS 업로드"
  - "distribute video"
---

# Distribute Skill

## Purpose
create-video 스킬의 출력 영상을 Instagram Reels, YouTube Shorts, TikTok에 배포합니다.
manifesto §5의 자동화 윤리 원칙에 따라 최종 승인 게이트를 반드시 거칩니다.

**반드시 먼저 읽기**: `manifesto.txt` §2 투명성, §5 자동화 윤리, `gotchas.md` Category: distribute

---

## Pre-run Checklist (ACTIVE Gotchas)

- [ ] GOTCHA-008: `distributed_log.json` 조회 — 공고번호 이미 존재하면 스킵

---

## Process

### Step 1 — 중복 배포 방지 체크
- `Scripts/distributed_log.json` 에서 `desertionNo` 조회 (GOTCHA-008)
- 이미 존재하면: `status: already_distributed` 반환, 스킵
- 존재하지 않으면: 계속 진행

### Step 2 — 최종 승인 게이트 (Human Review)
```
⚠️  HUMAN APPROVAL REQUIRED
───────────────────────────────────────────
동물명(임시): {name}
공고번호: {noticeNo}
보호소: {careNm}
D-day: D-{d_day}
영상 파일: {video_paths}
캡션 미리보기:
{caption_preview}
───────────────────────────────────────────
승인하려면 'approve {desertionNo}' 입력
거절하려면 'reject {desertionNo} [사유]' 입력
```
- 승인 없이는 배포 불가 (manifesto §5)
- 거절 시: `status: rejected`, 사유 기록 후 종료

### Step 3 — 플랫폼별 업로드
승인 후 순서대로 업로드:

**Instagram Reels**
- 영상: `video_{id}_instagram.mp4`
- 캡션: `content.caption.ko` (최대 2,200자)
- 해시태그: `Templates/hashtags_ko.txt` 참조
- API: Instagram Graph API

**YouTube Shorts**
- 영상: `video_{id}_youtube.mp4`
- 제목: `{품종} | {보호소명} | D-{n} | 공고 {noticeNo}`
- 설명: `content.caption.ko` + 영문 요약
- 태그: `Templates/hashtags_ko.txt` 참조

**TikTok**
- 영상: `video_{id}_tiktok.mp4`
- 설명: 캡션 축약본 (최대 150자)

### Step 4 — 배포 결과 기록
성공 시 `Scripts/distributed_log.json` 업데이트:
```json
{
  "desertionNo": "202600001234",
  "noticeNo": "충남-천안-2026-00123",
  "distributed_at": "2026-03-27T14:30:00",
  "platforms": ["instagram", "youtube", "tiktok"],
  "approved_by": "human",
  "status": "success"
}
```

### Step 5 — 모니터링 데이터 수집 (선택)
배포 24시간 후 각 플랫폼 API에서:
- 조회수, 좋아요, 저장수, 공유수 수집
- `Scripts/output/analytics_{desertionNo}.json` 저장

---

## Output Schema
```json
{
  "desertionNo": "202600001234",
  "approved": true,
  "platforms": {
    "instagram": {"status": "success", "post_id": "...", "url": "..."},
    "youtube": {"status": "success", "video_id": "...", "url": "..."},
    "tiktok": {"status": "success", "video_id": "...", "url": "..."}
  },
  "distributed_at": "2026-03-27T14:30:00"
}
```

## Script
`Scripts/distribute.py`, `Scripts/distributed_log.json`

## Templates
`Templates/hashtags_ko.txt`, `Templates/post_template.md`
