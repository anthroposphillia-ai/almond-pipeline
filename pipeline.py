"""
Almond Pipeline — pipeline.py
전체 파이프라인 진입점

실행: python pipeline.py [--limit N] [--platforms instagram youtube tiktok]
"""

import argparse
import json
import sys
from datetime import date
from pathlib import Path

# .env 파일 자동 로드 (python-dotenv)
try:
    from dotenv import load_dotenv
    load_dotenv(Path(__file__).parent / ".env")
except ImportError:
    pass  # dotenv 미설치 시 환경변수를 직접 설정

SKILLS_DIR = Path(__file__).parent / ".claude" / "skills"
sys.path.insert(0, str(SKILLS_DIR / "fetch-data" / "Scripts"))
sys.path.insert(0, str(SKILLS_DIR / "generate-content" / "Scripts"))
sys.path.insert(0, str(SKILLS_DIR / "create-video" / "Scripts"))
sys.path.insert(0, str(SKILLS_DIR / "distribute" / "Scripts"))

from fetch_animals import main as fetch_main
from generate_caption import process_animal
from create_video import create_video
from distribute import distribute


def run_pipeline(limit: int | None = None, platforms: list[str] | None = None):
    today = date.today().strftime("%Y%m%d")
    fetch_output_path = SKILLS_DIR / "fetch-data" / "Scripts" / "output" / f"animals_{today}.json"

    # ── Stage 1: Fetch ──────────────────────────────
    print("\n═══ Stage 1: Fetch Data ═══")
    fetch_result = fetch_main()
    animals = fetch_result["animals"]

    if limit:
        animals = animals[:limit]
        print(f"[limit] {limit}개 동물만 처리")

    print(f"파이프라인 대상: {len(animals)}마리")

    # ── Stage 2–4: Per animal ───────────────────────
    for i, animal in enumerate(animals, 1):
        desertion_no = animal["desertionNo"]
        print(f"\n[{i}/{len(animals)}] {desertion_no} | D-{animal['d_day']} | {animal.get('kindCd', '')}")

        animal_path = fetch_output_path.parent / f"animal_{desertion_no}.json"
        animal_path.write_text(json.dumps(animal, ensure_ascii=False, indent=2), encoding="utf-8")

        # Stage 2: Generate Content
        print("  → Stage 2: Generate Content")
        content = process_animal(animal)
        content_path = SKILLS_DIR / "generate-content" / "Scripts" / "output" / f"content_{desertion_no}.json"

        if content.get("validation", {}).get("status") == "human_review":
            print(f"  ⚠️  {desertion_no}: human_review 큐로 이동 — 스킵")
            continue

        # Stage 3: Create Video
        print("  → Stage 3: Create Video")
        try:
            video_manifest = create_video(str(content_path), animal["filename"], platforms)
        except Exception as e:
            print(f"  ❌ 영상 생성 실패: {e} — 스킵")
            continue

        manifest_path = SKILLS_DIR / "create-video" / "Scripts" / "output" / f"video_{desertion_no}_manifest.json"

        # Stage 4: Distribute (human approval gate)
        print("  → Stage 4: Distribute")
        result = distribute(str(animal_path), str(content_path), str(manifest_path), platforms)

        if result["status"] == "already_distributed":
            print(f"  ↩️  이미 배포됨 — 스킵")
        elif result["status"] == "rejected":
            print(f"  ❌ 거절됨")
        else:
            print(f"  ✅ 배포 완료: {list(result.get('platforms', {}).keys())}")

    print("\n═══ Pipeline 완료 ═══")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Almond Pipeline")
    parser.add_argument("--limit", type=int, help="처리할 동물 수 제한 (테스트용)")
    parser.add_argument(
        "--platforms",
        nargs="+",
        default=["instagram", "youtube", "tiktok"],
        help="배포 플랫폼 지정",
    )
    args = parser.parse_args()
    run_pipeline(limit=args.limit, platforms=args.platforms)
