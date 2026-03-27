"""
Almond Pipeline — validate_content.py
Manifesto 준수 검증 모듈

Manifesto ref: §1 저자극성, §2 투명성, §5 자동화 윤리
Gotchas: GOTCHA-004, GOTCHA-005
"""

import re


FORBIDDEN_PATTERNS = [
    (r"불쌍한?", "불쌍함 표현 (§1 위반)"),
    (r"가련한?", "불쌍함 표현 (§1 위반)"),
    (r"죽어가는?", "죽음 강조 표현 (§1 위반)"),
    (r"죽습니다", "죽음 강조 표현 (§1 위반)"),
    (r"제발", "감정 호소 (§1 위반)"),
    (r"살려주세요", "감정 호소 (§1 위반)"),
    (r"마지막\s*기회", "감정 호소 (§1 위반)"),
    (r"너무나", "과장 부사 (§1 위반)"),
    (r"절박하게?", "감정 표현 (§1 위반)"),
    (r"버리지\s*마세요", "의인화 호소 (§1 위반)"),
    (r"도와주세요", "감정 호소 (§1 위반)"),
    (r"SOS", "과장 표현 (§1 위반)"),
]

REQUIRED_OVERLAY_FIELDS = [
    "shelter_info",
    "watermark",
    "contact",
    "d_day_badge",
    "title",
]


def validate_against_manifesto(text: str) -> list[dict]:
    """
    금지 표현 감지. 위반 항목 리스트 반환. 빈 리스트 = 통과.
    GOTCHA-004: 캡션 생성 후 반드시 실행.
    """
    violations = []
    for pattern, reason in FORBIDDEN_PATTERNS:
        matches = re.findall(pattern, text, re.IGNORECASE)
        if matches:
            violations.append({
                "pattern": pattern,
                "reason": reason,
                "found": matches,
            })
    return violations


def validate_required_fields(overlay: dict) -> list[str]:
    """
    GOTCHA-005: 필수 필드 포함 여부 확인.
    """
    missing = []
    for field in REQUIRED_OVERLAY_FIELDS:
        if not overlay.get(field):
            missing.append(field)

    # 워터마크 내용 검증 (Manifesto §2)
    watermark = overlay.get("watermark", "")
    if "AI-generated" not in watermark:
        missing.append("watermark must contain 'AI-generated'")

    return missing


def validate_content(caption_ko: str, overlay: dict) -> dict:
    """
    통합 검증. 결과 반환.
    """
    manifesto_violations = validate_against_manifesto(caption_ko)
    missing_fields = validate_required_fields(overlay)

    return {
        "manifesto_pass": len(manifesto_violations) == 0,
        "required_fields_pass": len(missing_fields) == 0,
        "manifesto_violations": manifesto_violations,
        "missing_fields": missing_fields,
    }
