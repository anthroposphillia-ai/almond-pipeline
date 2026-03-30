"""
YouTube Shorts 업로드 테스트
Mock 영상(202600001002 코리안숏헤어 D-0)으로 실제 업로드 검증
"""
import sys
from pathlib import Path

SKILLS_DIR = Path(__file__).parent / ".claude" / "skills"
sys.path.insert(0, str(SKILLS_DIR / "distribute" / "Scripts"))

from upload_youtube import upload_youtube_shorts

VIDEO_PATH = str(Path(__file__).parent / "final_videos" / "202600001002" / "video_youtube_shorts.mp4")

TITLE = "코리안숏헤어 | 서울 마포구 동물보호센터 | D-0 | 공고 서울-마포-2026-00045"

DESCRIPTION = """[시뮬레이션 테스트 영상] Almond Pipeline 개발 중 업로드 테스트입니다.

이 영상은 실제 유기동물 공공데이터를 기반으로 AI가 제작한 시뮬레이션입니다.
출처: 공공데이터포털 유기동물 보호 공고 API

#유기동물 #입양 #보호소 #AIgenerated #Shorts"""

if __name__ == "__main__":
    print("=== YouTube Shorts 업로드 테스트 ===")
    print(f"영상: {VIDEO_PATH}")
    print(f"제목: {TITLE}")
    print()
    print("브라우저에서 Google 계정 로그인 화면이 열립니다...")
    print()

    result = upload_youtube_shorts(VIDEO_PATH, TITLE, DESCRIPTION)

    print()
    print("=== 결과 ===")
    print(f"상태:   {result['status']}")
    print(f"URL:    {result['url']}")
    print(f"영상ID: {result['video_id']}")
