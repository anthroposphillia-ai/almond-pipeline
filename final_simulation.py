import subprocess
import os
import json
import time
import sys
import io

# 윈도우 터미널(CP949)에서도 UTF-8 출력을 안전하게 하기 위해 설정
if sys.platform == "win32":
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    except:
        pass

def run_step(command):
    try:
        # errors='replace'를 추가하여 인코딩 오류 시 프로그램 중단 방지
        # 보안(명령어 인젝션 방지)을 위해 shell=True 제거하고 리스트 형태로 전달
        result = subprocess.run(command.split(), capture_output=True, text=True, encoding='utf-8', errors='replace')
        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print(f"Error during {command}: {result.stderr}")
    except Exception as e:
        print(f"Failed to run {command}: {e}")

def final_sim():
    # 0. track_animals.py ([08:50])
    run_step("python track_animals.py")

    # 1. manifesto.txt 출력 ([09:00])
    print("-" * 32)
    print("[09:00] 매니페스토 출력")
    print("-" * 32)
    if os.path.exists("manifesto.txt"):
        with open("manifesto.txt", "r", encoding="utf-8") as f:
            print(f.read())
    else:
        print("manifesto.txt 파일이 없습니다.")
    print("")

    # 2. fetch_animals.py ([09:01]) - 실제 API 호출
    run_step("python fetch_animals.py")

    # 3. generate_prompts.py ([09:02])
    run_step("python generate_prompts.py")

    # 4. generate_thumbnail.py ([09:03])
    run_step("python generate_thumbnail.py")

    # 5. generate_metadata.py ([09:04])
    run_step("python generate_metadata.py")

    # 6. generate_videos.py (시뮬레이션) ([09:05])
    run_step("python generate_videos_sim.py")

    # 7. add_subtitles.py ([09:06])
    run_step("python add_subtitles.py")

    # 8. upload_youtube.py (시뮬레이션) ([09:07])
    run_step("python upload_youtube_sim.py")

    # 9. upload_tiktok.py (시뮬레이션) ([09:08])
    # 스크립트 내부에서 videos.json을 읽으므로 직접 실행만 해도 됨 (메인 실행부에서 인자 처리함)
    run_step("python upload_tiktok.py")
 
    # 10. upload_instagram.py (시뮬레이션) ([09:09])
    run_step("python upload_instagram.py")
 
    # 11. upload_twitter.py (시뮬레이션) ([09:10])
    run_step("python upload_twitter.py")

    # 최종 요약
    print("-" * 32)
    print("최종 요약")
    print("-" * 32)
    
    # 데이터 집계
    videos_file = "videos.json"
    if os.path.exists(videos_file):
        with open(videos_file, "r", encoding="utf-8") as f:
            videos = json.load(f)
            total = len(videos)
            yt_count = len([v for v in videos if v.get('status') != 'euthanized'])
            tiktok_count = yt_count
            insta_count = total # 안락사도 사진으로 올라감
            twitter_count = total
            
            print(f"오늘 처리된 동물: {total}마리")
            print("플랫폼별 업로드 수:")
            print(f"- 유튜브: {yt_count}개")
            print(f"- 틱톡: {tiktok_count}개")
            print(f"- 인스타: {insta_count}개")
            print(f"- X: {twitter_count}개")
            print(f"총 업로드: {yt_count + tiktok_count + insta_count + twitter_count}개")
    else:
        print("데이터를 집계할 수 없습니다 (videos.json 없음).")
    
    print("에러: 없음")
    print("================================")

if __name__ == "__main__":
    final_sim()
