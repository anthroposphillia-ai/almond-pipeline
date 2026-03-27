"""
Almond Pipeline — fetch_animals.py
공공데이터포털 유기동물 보호 공고 API 수집 스크립트

API: https://apis.data.go.kr/1543061/abandonmentPublicSrvc/abandonmentPublic
Manifesto ref: §4 객관성 원칙
Gotchas: GOTCHA-001, GOTCHA-002, GOTCHA-003, GOTCHA-009
"""

import os
import json
import math
import logging
from datetime import datetime, date
from pathlib import Path

import requests

# ──────────────────────────────────────────────
# Config
# ──────────────────────────────────────────────
API_BASE_URL = "https://apis.data.go.kr/1543061/abandonmentPublicSrvc/abandonmentPublic"
OUTPUT_DIR = Path(__file__).parent / "output"
OUTPUT_DIR.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)


# ──────────────────────────────────────────────
# D-day calculation
# ──────────────────────────────────────────────
def calculate_d_day(notice_edt: str) -> int:
    """
    GOTCHA-001: noticeEdt는 'YYYYMMDD' 형식. datetime으로 파싱 후 계산.
    """
    try:
        end_date = datetime.strptime(notice_edt, "%Y%m%d").date()
        return (end_date - date.today()).days
    except ValueError:
        logger.warning(f"날짜 파싱 실패: {notice_edt} — 레코드 스킵")
        return -999  # 파싱 실패 sentinel


def get_status(d_day: int) -> str:
    if d_day == 0:
        return "urgent"
    elif 1 <= d_day <= 3:
        return "critical"
    elif d_day > 3:
        return "normal"
    else:
        return "expired"


# ──────────────────────────────────────────────
# API fetch with pagination
# ──────────────────────────────────────────────
def fetch_page(api_key: str, page_no: int, num_of_rows: int = 100) -> dict:
    params = {
        "serviceKey": api_key,
        "numOfRows": num_of_rows,
        "pageNo": page_no,
        "_type": "json",
        "state": "notice",
    }
    resp = requests.get(API_BASE_URL, params=params, timeout=10)
    resp.raise_for_status()
    return resp.json()


def fetch_all_animals(api_key: str, num_of_rows: int = 100) -> list[dict]:
    """
    GOTCHA-002: totalCount 확인 후 페이지네이션 루프 실행.
    """
    logger.info("1페이지 요청 중...")
    first_response = fetch_page(api_key, page_no=1, num_of_rows=num_of_rows)

    body = first_response.get("response", {}).get("body", {})
    total_count = int(body.get("totalCount", 0))
    items = body.get("items", {}).get("item", [])

    if isinstance(items, dict):  # 단건 응답 시 리스트가 아닌 dict로 반환됨
        items = [items]

    logger.info(f"전체 공고 수: {total_count}")

    total_pages = math.ceil(total_count / num_of_rows)
    for page_no in range(2, total_pages + 1):
        logger.info(f"{page_no}/{total_pages} 페이지 요청 중...")
        response = fetch_page(api_key, page_no=page_no, num_of_rows=num_of_rows)
        page_items = (
            response.get("response", {})
            .get("body", {})
            .get("items", {})
            .get("item", [])
        )
        if isinstance(page_items, dict):
            page_items = [page_items]
        items.extend(page_items)

    return items


# ──────────────────────────────────────────────
# Record processing
# ──────────────────────────────────────────────
def process_record(raw: dict) -> dict | None:
    """
    단일 레코드 정제.
    GOTCHA-001: 날짜 파싱
    GOTCHA-003: 이미지 URL null 체크
    GOTCHA-009: d_day < 0 필터링
    Manifesto §4: null 필드는 "정보 없음" 표기
    """
    notice_edt = raw.get("noticeEdt", "")
    if not notice_edt:
        logger.warning(f"noticeEdt 없음: {raw.get('desertionNo')} — 스킵")
        return None

    d_day = calculate_d_day(notice_edt)
    if d_day == -999:
        return None  # 날짜 파싱 실패

    status = get_status(d_day)

    # GOTCHA-009: 이미 종료된 공고 제외
    if status == "expired":
        return {**raw, "d_day": d_day, "status": "expired", "image_status": "expired"}

    # GOTCHA-003: 이미지 URL 검증
    filename = raw.get("filename") or raw.get("popfile")
    image_status = "ok" if filename else "no_image"

    return {
        "desertionNo": raw.get("desertionNo", "정보 없음"),
        "noticeNo": raw.get("noticeNo", "정보 없음"),
        "happenDt": raw.get("happenDt", "정보 없음"),
        "happenPlace": raw.get("happenPlace", "정보 없음"),
        "kindCd": raw.get("kindCd", "정보 없음"),
        "colorCd": raw.get("colorCd", "정보 없음"),
        "age": raw.get("age", "정보 없음"),
        "weight": raw.get("weight", "정보 없음"),
        "noticeSdt": raw.get("noticeSdt", "정보 없음"),
        "noticeEdt": notice_edt,
        "processState": raw.get("processState", "정보 없음"),
        "sexCd": raw.get("sexCd", "정보 없음"),
        "neuterYn": raw.get("neuterYn", "정보 없음"),
        "specialMark": raw.get("specialMark", "정보 없음"),
        "careNm": raw.get("careNm", "정보 없음"),
        "careTel": raw.get("careTel", "정보 없음"),
        "careAddr": raw.get("careAddr", "정보 없음"),
        "orgNm": raw.get("orgNm", "정보 없음"),
        "chargeNm": raw.get("chargeNm", "정보 없음"),
        "officetel": raw.get("officetel", "정보 없음"),
        "filename": filename or None,
        "d_day": d_day,
        "status": status,
        "image_status": image_status,
    }


# ──────────────────────────────────────────────
# Priority sort
# ──────────────────────────────────────────────
PRIORITY_ORDER = {"urgent": 0, "critical": 1, "normal": 2}

def sort_by_priority(animals: list[dict]) -> list[dict]:
    return sorted(
        animals,
        key=lambda x: (PRIORITY_ORDER.get(x["status"], 99), x["d_day"]),
    )


# ──────────────────────────────────────────────
# Main
# ──────────────────────────────────────────────
def main():
    api_key = os.environ.get("ANIMAL_API_KEY")
    if not api_key:
        raise EnvironmentError("환경변수 ANIMAL_API_KEY가 설정되지 않았습니다.")

    raw_animals = fetch_all_animals(api_key)
    logger.info(f"원본 레코드 수: {len(raw_animals)}")

    processed, expired, no_image = [], [], []

    for raw in raw_animals:
        record = process_record(raw)
        if record is None:
            continue
        if record["status"] == "expired":
            expired.append(record)
        elif record["image_status"] == "no_image":
            no_image.append(record)
        else:
            processed.append(record)

    pipeline_ready = sort_by_priority(processed)

    today_str = date.today().strftime("%Y%m%d")

    # 파이프라인 진행 데이터
    output = {
        "fetch_date": date.today().isoformat(),
        "total_fetched": len(raw_animals),
        "pipeline_ready": len(pipeline_ready),
        "expired_skipped": len(expired),
        "no_image_queued": len(no_image),
        "animals": pipeline_ready,
    }
    out_path = OUTPUT_DIR / f"animals_{today_str}.json"
    out_path.write_text(json.dumps(output, ensure_ascii=False, indent=2), encoding="utf-8")
    logger.info(f"파이프라인 준비 완료: {out_path}")

    # 이미지 없는 레코드 별도 저장
    no_img_path = OUTPUT_DIR / f"no_image_{today_str}.json"
    no_img_path.write_text(json.dumps(no_image, ensure_ascii=False, indent=2), encoding="utf-8")
    logger.info(f"이미지 없는 레코드: {no_img_path}")

    logger.info(
        f"완료 — 전체: {len(raw_animals)} | "
        f"파이프라인: {len(pipeline_ready)} | "
        f"종료: {len(expired)} | "
        f"이미지없음: {len(no_image)}"
    )
    return output


if __name__ == "__main__":
    main()
