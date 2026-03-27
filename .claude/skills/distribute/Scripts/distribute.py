"""
Almond Pipeline — distribute.py
플랫폼별 영상 배포 + 중복 방지 + 최종 승인 게이트

Manifesto ref: §2 투명성, §5 자동화 윤리(승인 게이트)
Gotchas: GOTCHA-008
"""

import json
import os
from datetime import datetime
from pathlib import Path

LOG_PATH = Path(__file__).parent / "distributed_log.json"
OUTPUT_DIR = Path(__file__).parent / "output"
OUTPUT_DIR.mkdir(exist_ok=True)


# ──────────────────────────────────────────────
# Distributed log (GOTCHA-008: 중복 방지)
# ──────────────────────────────────────────────
def load_log() -> dict:
    if LOG_PATH.exists():
        return json.loads(LOG_PATH.read_text(encoding="utf-8"))
    return {}


def save_log(log: dict):
    LOG_PATH.write_text(json.dumps(log, ensure_ascii=False, indent=2), encoding="utf-8")


def is_already_distributed(desertion_no: str) -> bool:
    """GOTCHA-008: 공고번호 중복 배포 방지."""
    log = load_log()
    return desertion_no in log


# ──────────────────────────────────────────────
# Human approval gate (Manifesto §5)
# ──────────────────────────────────────────────
def request_human_approval(animal: dict, content: dict, video_manifest: dict) -> bool:
    """
    Manifesto §5: 사람의 최종 승인 없이는 배포 불가.
    """
    caption_preview = content.get("caption", {}).get("ko", "")[:200]
    video_paths = [v["path"] for v in video_manifest.get("videos", {}).values()]

    print("\n" + "─" * 60)
    print("⚠️  HUMAN APPROVAL REQUIRED — Almond Pipeline")
    print("─" * 60)
    print(f"공고번호:   {animal.get('noticeNo', 'N/A')}")
    print(f"보호소:     {animal.get('careNm', 'N/A')}")
    print(f"D-day:      D-{animal.get('d_day', '?')}")
    print(f"영상 파일:")
    for path in video_paths:
        print(f"            {path}")
    print(f"\n캡션 미리보기:\n{caption_preview}...")
    print("─" * 60)
    print(f"승인: 'approve {animal['desertionNo']}'")
    print(f"거절: 'reject  {animal['desertionNo']} [사유]'")
    print("─" * 60)

    response = input("> ").strip()

    desertion_no = animal["desertionNo"]
    if response.startswith(f"approve {desertion_no}"):
        print("✅ 승인됨. 배포를 시작합니다.")
        return True
    elif response.startswith(f"reject {desertion_no}"):
        reason = response.replace(f"reject {desertion_no}", "").strip()
        print(f"❌ 거절됨. 사유: {reason or '(없음)'}")
        return False
    else:
        print("❌ 잘못된 입력. 거절로 처리됩니다.")
        return False


# ──────────────────────────────────────────────
# Platform uploaders (stub — 실제 API 키 필요)
# ──────────────────────────────────────────────
def upload_instagram(video_path: str, caption: str) -> dict:
    """Instagram Graph API 업로드 (stub)."""
    access_token = os.environ.get("INSTAGRAM_ACCESS_TOKEN")
    ig_user_id = os.environ.get("INSTAGRAM_USER_ID")
    if not access_token or not ig_user_id:
        raise EnvironmentError("INSTAGRAM_ACCESS_TOKEN, INSTAGRAM_USER_ID 환경변수 필요")
    # 실제 구현: Reels 업로드 API 호출
    print(f"[Instagram] 업로드 시뮬레이션: {video_path}")
    return {"status": "success", "platform": "instagram", "post_id": "STUB_ID", "url": "https://instagram.com/p/STUB"}


def upload_youtube(video_path: str, title: str, description: str) -> dict:
    """YouTube Data API v3 업로드 (stub)."""
    api_key = os.environ.get("YOUTUBE_API_KEY")
    if not api_key:
        raise EnvironmentError("YOUTUBE_API_KEY 환경변수 필요")
    print(f"[YouTube] 업로드 시뮬레이션: {video_path}")
    return {"status": "success", "platform": "youtube", "video_id": "STUB_ID", "url": "https://youtube.com/shorts/STUB"}


def upload_tiktok(video_path: str, description: str) -> dict:
    """TikTok Content Posting API 업로드 (stub)."""
    access_token = os.environ.get("TIKTOK_ACCESS_TOKEN")
    if not access_token:
        raise EnvironmentError("TIKTOK_ACCESS_TOKEN 환경변수 필요")
    print(f"[TikTok] 업로드 시뮬레이션: {video_path}")
    return {"status": "success", "platform": "tiktok", "video_id": "STUB_ID", "url": "https://tiktok.com/@stub"}


# ──────────────────────────────────────────────
# Main distribute function
# ──────────────────────────────────────────────
def distribute(
    animal_path: str,
    content_path: str,
    video_manifest_path: str,
    platforms: list[str] | None = None,
) -> dict:
    animal = json.loads(Path(animal_path).read_text(encoding="utf-8"))
    content = json.loads(Path(content_path).read_text(encoding="utf-8"))
    video_manifest = json.loads(Path(video_manifest_path).read_text(encoding="utf-8"))

    desertion_no = animal["desertionNo"]
    notice_no = animal.get("noticeNo", "정보 없음")

    # GOTCHA-008: 중복 배포 방지
    if is_already_distributed(desertion_no):
        print(f"[스킵] {desertion_no}은 이미 배포됨.")
        return {"status": "already_distributed", "desertionNo": desertion_no}

    # Manifesto §5: 최종 승인 게이트
    approved = request_human_approval(animal, content, video_manifest)
    if not approved:
        return {"status": "rejected", "desertionNo": desertion_no}

    if platforms is None:
        platforms = ["instagram", "youtube", "tiktok"]

    caption_ko = content["caption"]["ko"]
    caption_en = content["caption"]["en"]
    videos = video_manifest["videos"]

    results = {}

    if "instagram" in platforms and "instagram_reels" in videos:
        results["instagram"] = upload_instagram(
            videos["instagram_reels"]["path"], caption_ko
        )

    if "youtube" in platforms and "youtube_shorts" in videos:
        breed = animal.get("kindCd", "유기동물").split("]")[-1].strip()
        title = f"{breed} | {animal.get('careNm', '')} | D-{animal['d_day']} | {notice_no}"
        results["youtube"] = upload_youtube(
            videos["youtube_shorts"]["path"], title, caption_ko + "\n\n" + caption_en
        )

    if "tiktok" in platforms and "tiktok" in videos:
        short_caption = caption_ko[:150]
        results["tiktok"] = upload_tiktok(videos["tiktok"]["path"], short_caption)

    # 배포 로그 기록
    log = load_log()
    log[desertion_no] = {
        "noticeNo": notice_no,
        "distributed_at": datetime.now().isoformat(),
        "platforms": list(results.keys()),
        "approved_by": "human",
        "status": "success",
    }
    save_log(log)

    return {
        "desertionNo": desertion_no,
        "approved": True,
        "platforms": results,
        "distributed_at": datetime.now().isoformat(),
    }


if __name__ == "__main__":
    import sys
    result = distribute(sys.argv[1], sys.argv[2], sys.argv[3])
    print(json.dumps(result, ensure_ascii=False, indent=2))
