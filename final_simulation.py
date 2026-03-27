"""
Almond Pipeline - final_simulation.py
API 키 없이 전체 파이프라인을 시뮬레이션합니다.

실행: python final_simulation.py [--limit N] [--no-video]

출력: final_videos/{desertionNo}/
  +-- caption_ko.txt
  +-- caption_en.txt
  +-- overlay.json
  +-- validation.json
  +-- video_{platform}.mp4  (ffmpeg 설치 시)
  +-- report.json

ffmpeg 없이도 실행 가능합니다 (영상 생성 단계만 스킵됨).
"""

import argparse
import json
import re
import subprocess
import sys
import tempfile
from datetime import date, datetime, timedelta
from pathlib import Path

# ----------------------------------------------
# Paths
# ----------------------------------------------
ROOT = Path(__file__).parent
FINAL_VIDEOS = ROOT / "final_videos"
FINAL_VIDEOS.mkdir(exist_ok=True)

MANIFESTO_PATH = ROOT / "manifesto.txt"
GOTCHAS_PATH = ROOT / "gotchas.md"

# ----------------------------------------------
# ANSI colors
# ----------------------------------------------
class C:
    RESET  = "\033[0m"
    BOLD   = "\033[1m"
    GREEN  = "\033[92m"
    YELLOW = "\033[93m"
    RED    = "\033[91m"
    CYAN   = "\033[96m"
    DIM    = "\033[2m"

def pr(color, label, msg=""):
    print(f"{color}{C.BOLD}[{label}]{C.RESET} {msg}")

# ----------------------------------------------
# Mock data (실제 공공데이터 API 응답 구조 반영)
# ----------------------------------------------
MOCK_ANIMALS = [
    {
        "desertionNo": "202600001001",
        "noticeNo": "충남-천안-2026-00101",
        "happenDt": "20260320",
        "happenPlace": "충남 천안시 서북구",
        "kindCd": "[개] 말티즈",
        "colorCd": "흰색",
        "age": "2022(년생)",
        "weight": "3.5(Kg)",
        "noticeEdt": (date.today() + timedelta(days=2)).strftime("%Y%m%d"),
        "processState": "보호중",
        "sexCd": "M",
        "neuterYn": "Y",
        "specialMark": "온순함, 사람을 잘 따름, 실내생활 적응 완료",
        "careNm": "천안시 유기동물보호소",
        "careTel": "041-521-5690",
        "careAddr": "충청남도 천안시 서북구 쌍용대로 310",
        "orgNm": "충청남도 천안시",
        "chargeNm": "동물보호팀",
        "officetel": "041-521-2121",
        "filename": None,  # 시뮬레이션: 이미지 없음 → 색상 블록으로 대체
    },
    {
        "desertionNo": "202600001002",
        "noticeNo": "서울-마포-2026-00045",
        "happenDt": "20260322",
        "happenPlace": "서울 마포구 합정동",
        "kindCd": "[고양이] 코리안숏헤어",
        "colorCd": "삼색",
        "age": "2023(년생)",
        "weight": "3.2(Kg)",
        "noticeEdt": (date.today() + timedelta(days=0)).strftime("%Y%m%d"),  # D-0 긴급
        "processState": "보호중",
        "sexCd": "F",
        "neuterYn": "N",
        "specialMark": "활발함, 호기심 많음, 타묘와 합사 가능",
        "careNm": "서울 마포구 동물보호소",
        "careTel": "02-3153-9256",
        "careAddr": "서울특별시 마포구 월드컵로 240",
        "orgNm": "서울특별시 마포구",
        "chargeNm": "동물보호팀",
        "officetel": "02-3153-9200",
        "filename": None,
    },
    {
        "desertionNo": "202600001003",
        "noticeNo": "경기-수원-2026-00312",
        "happenDt": "20260318",
        "happenPlace": "경기 수원시 팔달구",
        "kindCd": "[개] 포메라니안",
        "colorCd": "크림색",
        "age": "2021(년생)",
        "weight": "2.8(Kg)",
        "noticeEdt": (date.today() + timedelta(days=5)).strftime("%Y%m%d"),
        "processState": "보호중",
        "sexCd": "F",
        "neuterYn": "Y",
        "specialMark": "애교많음, 산책 좋아함, 어린이와 친화적",
        "careNm": "수원시 유기동물보호소",
        "careTel": "031-228-3456",
        "careAddr": "경기도 수원시 팔달구 효원로 241",
        "orgNm": "경기도 수원시",
        "chargeNm": "동물복지팀",
        "officetel": "031-228-3000",
        "filename": None,
    },
]

# ----------------------------------------------
# Stage 1: Fetch (Simulation)
# ----------------------------------------------
FORBIDDEN_PATTERNS = [
    r"불쌍한?", r"가련한?", r"죽어가는?", r"죽습니다",
    r"제발", r"살려주세요", r"마지막\s*기회",
    r"너무나", r"절박하게?", r"버리지\s*마세요",
    r"도와주세요", r"SOS",
]

def calculate_d_day(notice_edt: str) -> int:
    """GOTCHA-001: %Y%m%d 형식으로 파싱."""
    end_date = datetime.strptime(notice_edt, "%Y%m%d").date()
    return (end_date - date.today()).days

def get_status(d_day: int) -> str:
    if d_day == 0:   return "urgent"
    if d_day <= 3:   return "critical"
    if d_day > 3:    return "normal"
    return "expired"

def sim_fetch(animals: list[dict]) -> list[dict]:
    pr(C.CYAN, "Stage 1", "공공데이터 API 시뮬레이션 (mock data)")
    result = []
    for raw in animals:
        d_day = calculate_d_day(raw["noticeEdt"])
        status = get_status(d_day)
        if status == "expired":
            pr(C.DIM, "SKIP", f"{raw['desertionNo']} - 공고 종료")
            continue
        record = {**raw, "d_day": d_day, "status": status,
                  "image_status": "sim_generated"}  # 시뮬레이션: 이미지 생성
        result.append(record)
        pr(C.GREEN, "FETCH",
           f"{record['desertionNo']} | {record['kindCd']} | D-{d_day} ({status})")
    # GOTCHA-002: totalCount 확인 (시뮬레이션에서는 단순 출력)
    print(f"{C.DIM}  totalCount={len(animals)} / numOfRows=100 → 페이지 1개{C.RESET}")
    return sorted(result, key=lambda x: ({"urgent":0,"critical":1,"normal":2}.get(x["status"],9), x["d_day"]))

# ----------------------------------------------
# Stage 2: Generate Content
# ----------------------------------------------
def extract_breed(kind_cd: str) -> str:
    m = re.search(r"\]\s*(.+)", kind_cd)
    return m.group(1).strip() if m else kind_cd

def extract_species(kind_cd: str) -> str:
    m = re.search(r"\[(.+?)\]", kind_cd)
    return m.group(1).strip() if m else "동물"

def parse_age(age_str: str) -> str:
    m = re.search(r"(\d{4})", age_str)
    if m:
        return f"약 {date.today().year - int(m.group(1))}살"
    return age_str

SEX_MAP    = {"M": "수컷", "F": "암컷", "Q": "성별 미상"}
NEUTER_MAP = {"Y": "중성화 완료", "N": "중성화 미완료", "U": "중성화 미상"}

def format_d_day_badge(d_day: int) -> str:
    if d_day == 0:   return "⏰ 오늘이 보호 마지막 날 | D-0"
    if d_day <= 3:   return f"D-{d_day} (보호 종료 임박)"
    return f"D-{d_day}"

def validate_manifesto(text: str) -> list[str]:
    return [p for p in FORBIDDEN_PATTERNS if re.search(p, text, re.IGNORECASE)]

def sim_generate(animal: dict) -> dict:
    breed   = extract_breed(animal["kindCd"])
    species = extract_species(animal["kindCd"])
    age     = parse_age(animal["age"])
    sex     = SEX_MAP.get(animal["sexCd"], "미상")
    neuter  = NEUTER_MAP.get(animal["neuterYn"], "미상")
    d_badge = format_d_day_badge(animal["d_day"])

    caption_ko = (
        f"{d_badge}\n\n"
        f"{species} · {breed} · {sex} · {age}\n"
        f"{neuter}\n\n"
        f"특징: {animal['specialMark']}\n\n"
        f"📍 보호소: {animal['careNm']}\n"
        f"📞 문의: {animal['careTel']}\n"
        f"📋 공고번호: {animal['noticeNo']}\n\n"
        f"본 영상은 AI로 제작되었으며, 실제 유기동물 공공데이터를 기반으로 합니다.\n"
        f"출처: 공공데이터포털 유기동물 보호 공고 API\n\n"
        f"#유기동물 #{breed} #입양 #보호소"
    )

    overlay = {
        "title":        f"{breed} · {sex} · {age}",
        "d_day_badge":  d_badge,
        "shelter_info": f"{animal['careNm']} | 공고 {animal['noticeNo']}",
        "watermark":    "AI-generated video | 실제 유기동물 정보 기반",
        "contact":      animal["careTel"],
    }

    # GOTCHA-004: manifesto 검증
    violations = validate_manifesto(caption_ko)
    manifesto_pass = len(violations) == 0

    # GOTCHA-005: 필수 필드 검증
    required_ok = all([
        overlay.get("shelter_info"),
        "AI-generated" in overlay.get("watermark", ""),
        overlay.get("contact"),
    ])

    return {
        "desertionNo": animal["desertionNo"],
        "caption": {"ko": caption_ko, "en": f"[EN] {breed} · {sex} · {age} | D-{animal['d_day']}"},
        "overlay": overlay,
        "validation": {
            "manifesto_pass": manifesto_pass,
            "required_fields_pass": required_ok,
            "violations": violations,
            "attempts": 1,
        },
    }

# ----------------------------------------------
# Stage 3: Create Video (ffmpeg or fallback)
# ----------------------------------------------
PLATFORM_PRESETS = {
    "instagram_reels": {"w": 1080, "h": 1920, "dur": 15},
    "youtube_shorts":  {"w": 1080, "h": 1920, "dur": 30},
    "tiktok":          {"w": 1080, "h": 1920, "dur": 15},
}

# 플랫폼별 배경 색상 (시뮬레이션용)
PLATFORM_COLORS = {
    "instagram_reels": "0x405DE6",
    "youtube_shorts":  "0xFF0000",
    "tiktok":          "0x000000",
}

def check_ffmpeg() -> bool:
    try:
        subprocess.run(["ffmpeg", "-version"], capture_output=True, check=True)
        return True
    except (FileNotFoundError, subprocess.CalledProcessError):
        return False

FONT_PATH = "C\\:/Windows/Fonts/malgun.ttf"


def _esc(text: str) -> str:
    """ffmpeg drawtext 텍스트 이스케이프: 특수문자 제거/치환."""
    return (
        text.replace("\\", "\\\\")
            .replace("'", "")
            .replace("[", "(")
            .replace("]", ")")
            .replace(":", " ")
    )


def create_sim_video(out_path: Path, overlay: dict, preset: dict, platform: str) -> bool:
    """
    ffmpeg로 텍스트 오버레이가 포함된 시뮬레이션 영상 생성.
    GOTCHA-006: 플랫폼별 프리셋 사용.
    GOTCHA-007: 워터마크 필수.
    """
    w, h, dur = preset["w"], preset["h"], preset["dur"]
    color = PLATFORM_COLORS.get(platform, "0x333333")

    title     = _esc(overlay["title"][:40])
    d_badge   = _esc(overlay["d_day_badge"][:30])
    shelter   = _esc(overlay["shelter_info"][:50])
    watermark = _esc(overlay["watermark"])  # 항상 포함 - GOTCHA-007

    ff = f"fontfile='{FONT_PATH}'"
    drawtext = (
        f"drawtext={ff}:text='{d_badge}':fontsize=40:fontcolor=white"
        f":x=40:y=60:box=1:boxcolor=red@0.8:boxborderw=10,"
        f"drawtext={ff}:text='{title}':fontsize=36:fontcolor=white"
        f":x=(w-text_w)/2:y=h*0.65,"
        f"drawtext={ff}:text='{shelter}':fontsize=22:fontcolor=white"
        f":x=(w-text_w)/2:y=h-100:box=1:boxcolor=black@0.6:boxborderw=8,"
        f"drawtext={ff}:text='{watermark}':fontsize=16:fontcolor=white@0.7"
        f":x=w-text_w-10:y=h-30"
    )

    cmd = [
        "ffmpeg", "-y",
        "-f", "lavfi",
        "-i", f"color=c={color}:size={w}x{h}:duration={dur}:rate=30",
        "-vf", drawtext,
        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-preset", "ultrafast",
        str(out_path),
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.returncode == 0

# ----------------------------------------------
# Stage 4: Distribute (Simulation)
# ----------------------------------------------
DIST_LOG = ROOT / "final_videos" / "distributed_log.json"

def load_dist_log() -> dict:
    return json.loads(DIST_LOG.read_text(encoding="utf-8")) if DIST_LOG.exists() else {}

def save_dist_log(log: dict):
    DIST_LOG.write_text(json.dumps(log, ensure_ascii=False, indent=2), encoding="utf-8")

def sim_distribute(animal: dict, content: dict, video_paths: dict, auto_approve: bool) -> dict:
    desertion_no = animal["desertionNo"]

    # GOTCHA-008: 중복 배포 방지
    log = load_dist_log()
    if desertion_no in log:
        pr(C.DIM, "SKIP", f"{desertion_no} - 이미 배포됨")
        return {"status": "already_distributed"}

    # Manifesto §5: 승인 게이트
    if not auto_approve:
        caption_preview = content["caption"]["ko"][:120].replace("\n", " ")
        print(f"\n{C.YELLOW}{'-'*56}{C.RESET}")
        print(f"{C.BOLD}⚠️  HUMAN APPROVAL REQUIRED{C.RESET}")
        print(f"{'-'*56}")
        print(f"  공고번호: {animal['noticeNo']}")
        print(f"  보호소:   {animal['careNm']}")
        print(f"  D-day:    D-{animal['d_day']}")
        print(f"  영상:     {list(video_paths.keys())}")
        print(f"  캡션:     {caption_preview}...")
        print(f"{'-'*56}")
        resp = input(f"  approve {desertion_no} / reject {desertion_no}: ").strip()
        if not resp.startswith(f"approve {desertion_no}"):
            pr(C.RED, "REJECT", desertion_no)
            return {"status": "rejected"}
    else:
        pr(C.DIM, "AUTO-APPROVE", f"{desertion_no} (시뮬레이션 모드)")

    # 배포 시뮬레이션
    platforms_result = {
        p: {"status": "sim_success", "url": f"https://{p}.com/sim/{desertion_no}"}
        for p in video_paths
    }

    log[desertion_no] = {
        "noticeNo": animal["noticeNo"],
        "distributed_at": datetime.now().isoformat(),
        "platforms": list(platforms_result.keys()),
        "approved_by": "auto_sim" if auto_approve else "human",
        "status": "sim_success",
    }
    save_dist_log(log)
    return {"status": "sim_success", "platforms": platforms_result}

# ----------------------------------------------
# Main
# ----------------------------------------------
def run_simulation(limit: int | None, no_video: bool, auto_approve: bool):
    print(f"\n{C.BOLD}{'='*60}{C.RESET}")
    print(f"{C.BOLD}  🐾 Almond Pipeline - Simulation Mode{C.RESET}")
    print(f"{C.BOLD}{'='*60}{C.RESET}")
    print(f"  manifesto.txt : {'✅' if MANIFESTO_PATH.exists() else '❌ 없음'}")
    print(f"  gotchas.md    : {'✅' if GOTCHAS_PATH.exists() else '❌ 없음'}")
    print(f"  final_videos/ : {FINAL_VIDEOS}")
    has_ffmpeg = check_ffmpeg()
    print(f"  ffmpeg        : {'✅ 설치됨' if has_ffmpeg else '⚠️ 없음 (영상 생성 스킵)'}")
    print(f"  auto_approve  : {'예 (승인 게이트 자동 통과)' if auto_approve else '아니오 (직접 승인 필요)'}")
    print(f"{'='*60}\n")

    animals = MOCK_ANIMALS[:limit] if limit else MOCK_ANIMALS

    # -- Stage 1 --
    print(f"\n{C.CYAN}{C.BOLD}--- Stage 1: Fetch Data ---{C.RESET}")
    fetched = sim_fetch(animals)
    print(f"  → {len(fetched)}마리 파이프라인 진입\n")

    summary = []

    for i, animal in enumerate(fetched, 1):
        did = animal["desertionNo"]
        out_dir = FINAL_VIDEOS / did
        out_dir.mkdir(exist_ok=True)

        print(f"{C.BOLD}[{i}/{len(fetched)}] {did} | {animal['kindCd']} | D-{animal['d_day']}{C.RESET}")

        # -- Stage 2 --
        print(f"  {C.CYAN}→ Stage 2: Generate Content{C.RESET}")
        content = sim_generate(animal)

        val = content["validation"]
        if val["manifesto_pass"] and val["required_fields_pass"]:
            pr(C.GREEN, "PASS", "manifesto ✓  required_fields ✓")
        else:
            pr(C.RED, "FAIL", f"violations={val['violations']}")

        # 파일 저장
        (out_dir / "caption_ko.txt").write_text(content["caption"]["ko"], encoding="utf-8")
        (out_dir / "caption_en.txt").write_text(content["caption"]["en"], encoding="utf-8")
        (out_dir / "overlay.json").write_text(
            json.dumps(content["overlay"], ensure_ascii=False, indent=2), encoding="utf-8")
        (out_dir / "validation.json").write_text(
            json.dumps(val, ensure_ascii=False, indent=2), encoding="utf-8")

        # -- Stage 3 --
        video_paths = {}
        print(f"  {C.CYAN}→ Stage 3: Create Video{C.RESET}")
        if no_video or not has_ffmpeg:
            reason = "--no-video 플래그" if no_video else "ffmpeg 미설치"
            pr(C.YELLOW, "SKIP", f"영상 생성 스킵 ({reason})")
            (out_dir / "video_skipped.txt").write_text(reason, encoding="utf-8")
        else:
            for platform, preset in PLATFORM_PRESETS.items():
                mp4_path = out_dir / f"video_{platform}.mp4"
                ok = create_sim_video(mp4_path, content["overlay"], preset, platform)
                if ok:
                    size_mb = round(mp4_path.stat().st_size / 1024 / 1024, 2)
                    pr(C.GREEN, platform, f"{mp4_path.name} ({size_mb} MB)")
                    video_paths[platform] = str(mp4_path)
                else:
                    pr(C.RED, platform, "렌더링 실패")

        # -- Stage 4 --
        print(f"  {C.CYAN}→ Stage 4: Distribute{C.RESET}")
        dist_result = sim_distribute(animal, content, video_paths, auto_approve)

        # 리포트 저장
        report = {
            "desertionNo": did,
            "animal": {
                "kindCd": animal["kindCd"],
                "d_day": animal["d_day"],
                "status": animal["status"],
                "careNm": animal["careNm"],
                "noticeNo": animal["noticeNo"],
            },
            "content_validation": val,
            "videos_generated": list(video_paths.keys()),
            "distribution": dist_result,
            "run_at": datetime.now().isoformat(),
        }
        (out_dir / "report.json").write_text(
            json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

        summary.append(report)
        print()

    # -- Final Summary --
    print(f"\n{C.BOLD}{'='*60}{C.RESET}")
    print(f"{C.BOLD}  🏁 Simulation 완료{C.RESET}")
    print(f"{'='*60}")
    print(f"  처리된 동물: {len(summary)}마리")

    ok  = sum(1 for r in summary if r["distribution"]["status"] in ("sim_success", "already_distributed"))
    rej = sum(1 for r in summary if r["distribution"]["status"] == "rejected")
    vid = sum(1 for r in summary if r["videos_generated"])
    print(f"  배포 성공:   {ok}건")
    print(f"  배포 거절:   {rej}건")
    print(f"  영상 생성:   {vid}건")
    print(f"\n  출력 폴더:   {FINAL_VIDEOS}")

    # final_videos/ 내 mp4 파일 확인
    mp4_files = list(FINAL_VIDEOS.rglob("*.mp4"))
    if mp4_files:
        print(f"\n  {C.GREEN}✅ final_videos/ 내 MP4 파일 ({len(mp4_files)}개):{C.RESET}")
        for f in mp4_files:
            size_mb = round(f.stat().st_size / 1024 / 1024, 2)
            print(f"    {f.relative_to(FINAL_VIDEOS)} - {size_mb} MB")
    else:
        print(f"\n  {C.YELLOW}⚠️  final_videos/ 내 MP4 파일 없음{C.RESET}")
        print(f"     ffmpeg 설치 후 재실행하거나 --no-video 플래그를 제거하세요.")

    print(f"{'='*60}\n")
    return summary


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Almond Pipeline 시뮬레이션 (API 키 불필요)"
    )
    parser.add_argument("--limit", type=int, default=None,
                        help="처리할 동물 수 제한 (기본: 전체)")
    parser.add_argument("--no-video", action="store_true",
                        help="영상 생성 스킵 (콘텐츠 생성/검증만 확인)")
    parser.add_argument("--auto-approve", action="store_true",
                        help="배포 승인 게이트 자동 통과 (시뮬레이션 전용)")
    args = parser.parse_args()

    run_simulation(
        limit=args.limit,
        no_video=args.no_video,
        auto_approve=args.auto_approve,
    )
