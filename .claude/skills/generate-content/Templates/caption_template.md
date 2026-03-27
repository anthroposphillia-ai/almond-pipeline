# Caption Template — Almond Pipeline

**Manifesto 준수**: §1 저자극성, §2 투명성, §3 존엄성
**금지 표현**: 불쌍한, 가련한, 죽어가는, 제발, 살려주세요, 마지막 기회

---

## 한국어 캡션 템플릿

```
{D_DAY_BADGE}

{SPECIES} · {BREED} · {SEX} · {AGE}
{NEUTER_STATUS}

특징: {SPECIAL_MARK}

📍 보호소: {CARE_NM}
📞 문의: {CARE_TEL}
📋 공고번호: {NOTICE_NO}

본 영상은 AI로 제작되었으며, 실제 유기동물 공공데이터를 기반으로 합니다.
출처: 공공데이터포털 유기동물 보호 공고 API

#유기동물 #{BREED} #입양 #보호소
```

---

## 영어 캡션 템플릿

```
{D_DAY_BADGE}

{SPECIES} · {BREED} · {SEX} · {AGE}
{NEUTER_STATUS}

Note: {SPECIAL_MARK}

📍 Shelter: {CARE_NM}
📞 Contact: {CARE_TEL}
📋 Notice No.: {NOTICE_NO}

This video is AI-generated, based on real abandoned animal public data.
Source: Korea Public Data Portal — Abandoned Animal API

#abandoned #rescue #adopt #{BREED_SLUG}
```

---

## D-day 배지 규칙 (Manifesto §1)

| d_day | 표현 |
|-------|------|
| 0 | `⏰ 오늘이 보호 마지막 날 \| D-0` |
| 1–3 | `D-{n} (보호 종료 임박)` |
| 4+ | `D-{n}` |

**사용 금지**: "곧 죽습니다", "마지막 기회", "제발 입양해주세요"

---

## 필수 포함 필드 (GOTCHA-005)

모든 캡션에 반드시 포함:
- [ ] 보호소명 (`careNm`)
- [ ] 공고번호 (`noticeNo`)
- [ ] 문의 연락처 (`careTel`)
- [ ] AI 제작 명시 문구
- [ ] 데이터 출처 명시

---

## 변수 매핑

| 변수 | API 필드 | 변환 규칙 |
|------|---------|---------|
| `{BREED}` | `kindCd` | `[개] 말티즈` → `말티즈` |
| `{SPECIES}` | `kindCd` | `[개]` → `개` |
| `{AGE}` | `age` | `2022(년생)` → `약 4살` |
| `{SEX}` | `sexCd` | M→수컷, F→암컷, Q→미상 |
| `{NEUTER_STATUS}` | `neuterYn` | Y→중성화완료, N→미완료, U→미상 |
| `{SPECIAL_MARK}` | `specialMark` | 원문 그대로 (null이면 `정보 없음`) |
