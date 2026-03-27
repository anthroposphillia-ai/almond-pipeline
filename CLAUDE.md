# Almond Pipeline — CLAUDE.md

공공데이터 유기동물 공고를 AI 영상으로 변환하여 입양률을 높이는 자동화 파이프라인.

**모든 작업 전 필수 참조**: `manifesto.txt`, `gotchas.md`

---

## 파이프라인 흐름

```
[공공데이터 API]
      ↓
① fetch-data       → animals_YYYYMMDD.json
      ↓
② generate-content → content_{id}.json (manifesto 검증 포함)
      ↓
③ create-video     → video_{id}_{platform}.mp4
      ↓
④ distribute       → SNS 배포 (human approval gate 필수)
```

---

## 스킬 디렉토리

| 스킬 | 경로 | 역할 |
|------|------|------|
| fetch-data | `.claude/skills/fetch-data/` | API 수집, D-day 계산, 정렬 |
| generate-content | `.claude/skills/generate-content/` | 캡션 + 오버레이 생성, manifesto 검증 |
| create-video | `.claude/skills/create-video/` | 이미지 → 플랫폼별 영상 렌더링 |
| distribute | `.claude/skills/distribute/` | SNS 업로드, 중복방지, 승인 게이트 |

---

## 핵심 파일

| 파일 | 역할 |
|------|------|
| `manifesto.txt` | 생명 존중 철학 — 모든 스킬이 참조 |
| `gotchas.md` | 반복 실수 기록 & 개선 루프 — 실행 전 반드시 확인 |
| `pipeline.py` | 전체 파이프라인 진입점 |

---

## 환경변수 (필수)

```bash
ANIMAL_API_KEY=...          # 공공데이터포털 API 인증키
INSTAGRAM_ACCESS_TOKEN=...  # Instagram Graph API
INSTAGRAM_USER_ID=...
YOUTUBE_API_KEY=...         # YouTube Data API v3
TIKTOK_ACCESS_TOKEN=...     # TikTok Content Posting API
```

**모든 키는 환경변수로 관리. 코드에 하드코딩 금지.**

---

## Manifesto 5대 원칙 요약

1. **저자극성**: 불쌍함을 팔지 않는다. D-day는 사실로 전달.
2. **투명성**: AI 제작 명시. 보호소·공고번호 항상 포함.
3. **존엄성**: 동물마다 개별 콘텐츠. 결함 강조/은폐 없음.
4. **객관성**: API 데이터만 사용. null = "정보 없음".
5. **자동화 윤리**: 최종 배포는 human approval gate 통과 필수.

---

## 새 Gotcha 발견 시

1. `gotchas.md`에 GOTCHA-[N] 항목 추가
2. 해당 스킬의 `SKILL.md` Pre-run Checklist에 추가
3. 수정 완료 후 `Status: RESOLVED`로 변경
