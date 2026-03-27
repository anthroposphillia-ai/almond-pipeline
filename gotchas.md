# gotchas.md — Almond Pipeline Learning & Evolution Log

에이전트의 반복적 실수를 기록하고 개선하는 루프.
모든 스킬 실행 전, 이 파일을 읽고 해당 카테고리의 GOTCHA를 확인하세요.

**Before every skill run: read the ACTIVE gotchas in your category.**

---

## 형식 | Format

```
### GOTCHA-[NNN]
- **Date**: YYYY-MM-DD
- **Category**: fetch / content / video / distribute / pipeline
- **Skill**: 어떤 스킬에서 발생했는가
- **Mistake**: 무엇이 잘못되었는가
- **Root Cause**: 왜 발생했는가
- **Fix Applied**: 어떻게 수정했는가
- **Prevention Rule**: 다음에 어떻게 방지하는가
- **Status**: ACTIVE | RESOLVED | WONT-FIX
```

---

## Category: fetch-data

### GOTCHA-001
- **Date**: 2026-03-27
- **Category**: fetch
- **Skill**: fetch-data
- **Mistake**: API 응답의 `noticeEdt`(공고 종료일) 필드가 "20260330" 형식인데 datetime 파싱 없이 문자열 비교로 D-day 계산함
- **Root Cause**: 날짜 형식 가정 (YYYY-MM-DD) vs 실제 형식 (YYYYMMDD)
- **Fix Applied**: `datetime.strptime(notice_edt, "%Y%m%d")` 로 파싱 후 계산
- **Prevention Rule**: 날짜 필드는 반드시 `%Y%m%d` 형식으로 파싱. 다른 형식이면 로그에 기록하고 해당 레코드 스킵
- **Status**: ACTIVE

### GOTCHA-002
- **Date**: 2026-03-27
- **Category**: fetch
- **Skill**: fetch-data
- **Mistake**: API 페이지네이션 미처리 — `numOfRows=10` 기본값으로 첫 10건만 가져옴
- **Root Cause**: API 문서 미확인, 기본 파라미터 사용
- **Fix Applied**: `numOfRows=100`, `pageNo` 루프로 전체 데이터 수집
- **Prevention Rule**: 첫 요청 후 `totalCount` 필드 확인. `totalCount > numOfRows`이면 페이지네이션 루프 실행
- **Status**: ACTIVE

### GOTCHA-003
- **Date**: 2026-03-27
- **Category**: fetch
- **Skill**: fetch-data
- **Mistake**: 이미지 URL(`filename` 필드)이 null인 레코드를 파이프라인에 그대로 통과시킴 → 이후 영상 생성 단계에서 에러
- **Root Cause**: null 체크 없음
- **Fix Applied**: `filename` null 레코드는 `no_image` 플래그 설정 후 별도 큐로 분리
- **Prevention Rule**: fetch 단계 출력 시 `filename` null 레코드는 반드시 분리. 영상 생성 단계로 보내지 않음
- **Status**: ACTIVE

---

## Category: generate-content

### GOTCHA-004
- **Date**: 2026-03-27
- **Category**: content
- **Skill**: generate-content
- **Mistake**: 생성된 캡션에 "불쌍한" 표현 포함 — manifesto §1 위반
- **Root Cause**: 금지 표현 검증 로직 미적용
- **Fix Applied**: `validate_against_manifesto()` 함수 추가 — 금지 표현 감지 시 자동 재생성 요청
- **Prevention Rule**: 캡션 생성 후 반드시 `validate_against_manifesto()` 실행. 3회 재시도 후에도 실패하면 human review 큐로 이동
- **Status**: ACTIVE

### GOTCHA-005
- **Date**: 2026-03-27
- **Category**: content
- **Skill**: generate-content
- **Mistake**: 보호소 번호, 공고 번호 누락된 캡션 배포됨
- **Root Cause**: 템플릿에서 필수 필드 검증 없음
- **Fix Applied**: `validate_required_fields()` 함수로 배포 전 필수 필드 확인
- **Prevention Rule**: 캡션 출력물에는 반드시: 보호소ID, 공고번호, AI제작명시, 문의처 포함 여부 체크
- **Status**: ACTIVE

---

## Category: create-video

### GOTCHA-006
- **Date**: 2026-03-27
- **Category**: video
- **Skill**: create-video
- **Mistake**: 영상 해상도가 플랫폼별 요구사항과 불일치 (Instagram Reels: 9:16, YouTube Shorts: 9:16)
- **Root Cause**: 단일 해상도(1080x1080)로 모든 플랫폼 출력
- **Fix Applied**: 플랫폼별 프리셋 추가: `PLATFORM_PRESETS` dict
- **Prevention Rule**: 영상 생성 시 대상 플랫폼을 명시적으로 지정. 미지정 시 9:16(1080x1920) 기본값 사용
- **Status**: ACTIVE

### GOTCHA-007
- **Date**: 2026-03-27
- **Category**: video
- **Skill**: create-video
- **Mistake**: AI 제작 워터마크 누락
- **Root Cause**: 워터마크 레이어가 조건부로만 추가됨
- **Fix Applied**: 워터마크를 선택사항이 아닌 필수 레이어로 변경 — manifesto §2 준수
- **Prevention Rule**: 워터마크 레이어는 파이프라인에서 제거 불가한 필수 요소로 고정
- **Status**: ACTIVE

---

## Category: distribute

### GOTCHA-008
- **Date**: 2026-03-27
- **Category**: distribute
- **Skill**: distribute
- **Mistake**: 동일 공고번호 영상이 중복 배포됨
- **Root Cause**: 배포 완료 상태 추적 없음
- **Fix Applied**: `distributed_log.json`에 공고번호 기록, 중복 배포 방지 체크 추가
- **Prevention Rule**: 배포 전 `distributed_log.json` 조회. 공고번호 이미 존재하면 스킵
- **Status**: ACTIVE

---

## Category: pipeline

### GOTCHA-009
- **Date**: 2026-03-27
- **Category**: pipeline
- **Skill**: 전체 파이프라인
- **Mistake**: D-day가 지난 레코드(이미 보호 종료)가 파이프라인에 진입
- **Root Cause**: fetch 단계에서 D-day < 0 필터링 없음
- **Fix Applied**: fetch 단계 출력 시 `d_day >= 0` 조건 필터 추가
- **Prevention Rule**: fetch 단계에서 `d_day < 0` 레코드는 `expired` 플래그 후 파이프라인 제외
- **Status**: ACTIVE

---

## 추가 방법 | How to Add a New Gotcha

파이프라인 실행 중 새로운 실수가 발견되면:

1. 이 파일에 새 GOTCHA 항목 추가 (번호 순차 증가)
2. Status = ACTIVE로 설정
3. 해당 스킬의 `SKILL.md` Guidelines 섹션에 "See GOTCHA-[NNN] in gotchas.md" 추가
4. 수정 후 검증이 완료되면 Status = RESOLVED로 변경

**ACTIVE gotcha는 해당 스킬의 Pre-run Checklist에 반드시 포함되어야 합니다.**
