"""
Almond Pipeline — generate_caption.py
유기동물 데이터 기반 캡션 및 영상 오버레이 텍스트 생성

Manifesto ref: §1 저자극성, §2 투명성, §3 존엄성
Gotchas: GOTCHA-004, GOTCHA-005
"""

import json
import re
from datetime import date
from pathlib import Path

MANIFESTO_PATH = Path(__file__).parents[5] / "manifesto.txt"
TEMPLATES_DIR = Path(__file__).parent.parent / "Templates"
OUTPUT_DIR = Path(__file__).parent / "output"
OUTPUT_DIR.mkdir(exist_ok=True)

# ──────────────────────────────────────────────
# Manifesto §1: 금지 표현 목록
# ──────────────────────────────────────────────
FORBIDDEN_PATTERNS = [
    r"불쌍한?",
    r"가련한?",
    r"죽어가는?",
    r"죽습니다",
    r"제발",
    r"살려주세요",
    r"마지막\s*기회",
    r"너무나",
    r"절박하게?",
    r"버리지\s*마세요",
    r"도와주세요",
    r"긴급\s*구조",
    r"SOS",
]

# ──────────────────────────────────────────────
# Data transformation helpers
# ──────────────────────────────────────────────
def extract_breed(kind_cd: str) -> str:
    """'[개] 말티즈' → '말티즈'"""
    match = re.search(r"\]\s*(.+)", kind_cd)
    return match.group(1).strip() if match else kind_cd


def extract_species(kind_cd: str) -> str:
    """'[개] 말티즈' → '개'"""
    match = re.search(r"\[(.+?)\]", kind_cd)
    return match.group(1).strip() if match else "동물"


def parse_age(age_str: str) -> str:
    """'2022(년생)' → '약 4살', '2024(년생)' → '약 2살'"""
    match = re.search(r"(\d{4})", age_str)
    if match:
        birth_year = int(match.group(1))
        age = date.today().year - birth_year
        return f"약 {age}살"
    return age_str


def format_sex(sex_cd: str) -> str:
    return {"M": "수컷", "F": "암컷", "Q": "성별 미상"}.get(sex_cd, "성별 미상")


def format_neuter(neuter_yn: str) -> str:
    return {"Y": "중성화 완료", "N": "중성화 미완료", "U": "중성화 미상"}.get(neuter_yn, "중성화 미상")


def format_d_day_badge(d_day: int) -> str:
    """Manifesto §1: 사실 기반 D-day 표현"""
    if d_day == 0:
        return "⏰ 오늘이 보호 마지막 날 | D-0"
    elif d_day <= 3:
        return f"D-{d_day} (보호 종료 임박)"
    else:
        return f"D-{d_day}"


# ──────────────────────────────────────────────
# Manifesto validation (GOTCHA-004)
# ──────────────────────────────────────────────
def validate_against_manifesto(text: str) -> list[str]:
    """
    금지 표현 감지. 위반 항목 리스트 반환. 빈 리스트 = 통과.
    """
    violations = []
    for pattern in FORBIDDEN_PATTERNS:
        if re.search(pattern, text, re.IGNORECASE):
            violations.append(pattern)
    return violations


def validate_required_fields(caption: str, overlay: dict) -> list[str]:
    """
    GOTCHA-005: 필수 필드 포함 여부 확인.
    """
    missing = []
    if not overlay.get("shelter_info"):
        missing.append("shelter_info (보호소ID/공고번호)")
    if "AI-generated" not in overlay.get("watermark", ""):
        missing.append("AI-generated watermark")
    if not overlay.get("contact"):
        missing.append("contact (문의처)")
    return missing


# ──────────────────────────────────────────────
# Caption generation
# ──────────────────────────────────────────────
def generate_caption(animal: dict) -> dict:
    """
    Manifesto §1, §2, §3 준수 캡션 생성.
    """
    breed = extract_breed(animal.get("kindCd", "정보 없음"))
    species = extract_species(animal.get("kindCd", "정보 없음"))
    age = parse_age(animal.get("age", "정보 없음"))
    sex = format_sex(animal.get("sexCd", "Q"))
    neuter = format_neuter(animal.get("neuterYn", "U"))
    special = animal.get("specialMark", "정보 없음")
    care_nm = animal.get("careNm", "정보 없음")
    care_tel = animal.get("careTel", "정보 없음")
    notice_no = animal.get("noticeNo", "정보 없음")
    d_day = animal.get("d_day", 0)
    d_day_badge = format_d_day_badge(d_day)

    caption_ko = f"""{d_day_badge}

{species} · {breed} · {sex} · {age}
{neuter}

특징: {special}

📍 보호소: {care_nm}
📞 문의: {care_tel}
📋 공고번호: {notice_no}

본 영상은 AI로 제작되었으며, 실제 유기동물 공공데이터를 기반으로 합니다.
출처: 공공데이터포털 유기동물 보호 공고 API

#유기동물 #{breed} #입양 #보호소 #유기견 #유기묘"""

    caption_en = f"""{d_day_badge}

{species} · {breed} · {sex} · {age}
{neuter}

Note: {special}

📍 Shelter: {care_nm}
📞 Contact: {care_tel}
📋 Notice No.: {notice_no}

This video is AI-generated, based on real abandoned animal public data.
Source: Korea Public Data Portal — Abandoned Animal API

#abandoned #rescue #adopt #{breed.lower().replace(' ', '')}"""

    return {"ko": caption_ko, "en": caption_en}


def generate_overlay(animal: dict) -> dict:
    """
    영상 오버레이 텍스트 생성.
    GOTCHA-007: 워터마크는 필수.
    """
    breed = extract_breed(animal.get("kindCd", "정보 없음"))
    age = parse_age(animal.get("age", "정보 없음"))
    sex = format_sex(animal.get("sexCd", "Q"))
    d_day = animal.get("d_day", 0)

    return {
        "title": f"{breed} · {sex} · {age}",
        "d_day_badge": format_d_day_badge(d_day),
        "shelter_info": f"{animal.get('careNm', '정보 없음')} | 공고 {animal.get('noticeNo', '정보 없음')}",
        "watermark": "AI-generated video | 실제 유기동물 정보 기반",  # 필수 — 제거 불가
        "contact": animal.get("careTel", "정보 없음"),
    }


# ──────────────────────────────────────────────
# Main
# ──────────────────────────────────────────────
def process_animal(animal: dict, max_retries: int = 3) -> dict:
    desertion_no = animal.get("desertionNo", "unknown")

    for attempt in range(1, max_retries + 1):
        caption = generate_caption(animal)
        overlay = generate_overlay(animal)

        # GOTCHA-004: manifesto 검증
        manifesto_violations = validate_against_manifesto(caption["ko"])
        # GOTCHA-005: 필수 필드 검증
        missing_fields = validate_required_fields(caption["ko"], overlay)

        manifesto_pass = len(manifesto_violations) == 0
        fields_pass = len(missing_fields) == 0

        if manifesto_pass and fields_pass:
            return {
                "desertionNo": desertion_no,
                "caption": caption,
                "overlay": overlay,
                "validation": {
                    "manifesto_pass": True,
                    "required_fields_pass": True,
                    "attempts": attempt,
                },
            }
        else:
            print(f"[attempt {attempt}] 검증 실패 — violations: {manifesto_violations}, missing: {missing_fields}")

    # 3회 실패 → human review 큐
    return {
        "desertionNo": desertion_no,
        "caption": caption,
        "overlay": overlay,
        "validation": {
            "manifesto_pass": False,
            "required_fields_pass": False,
            "attempts": max_retries,
            "status": "human_review",
        },
    }


def main(input_path: str):
    data = json.loads(Path(input_path).read_text(encoding="utf-8"))
    animals = data.get("animals", [])

    results, human_review = [], []

    for animal in animals:
        result = process_animal(animal)
        if result["validation"].get("status") == "human_review":
            human_review.append(result)
        else:
            results.append(result)
        # 결과 저장
        out_path = OUTPUT_DIR / f"content_{animal['desertionNo']}.json"
        out_path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"완료 — 성공: {len(results)} | human_review: {len(human_review)}")
    return results, human_review


if __name__ == "__main__":
    import sys
    main(sys.argv[1])
