import os
import json
import requests
from moviepy import VideoFileClip, TextClip, CompositeVideoClip, ColorClip
from moviepy.video.fx import Resize

def add_subtitles():
    input_file = "videos.json"
    output_dir = "final_videos"
    os.makedirs(output_dir, exist_ok=True)

    if not os.path.exists(input_file):
        print("videos.json 파일이 없습니다. 영상 생성을 먼저 진행해주세요.")
        return

    with open(input_file, "r", encoding="utf-8") as f:
        videos_data = json.load(f)

    if not videos_data:
        print("합성할 영상 데이터가 없습니다.")
        return

    print(f"총 {len(videos_data)}개의 영상에 자막 합성을 시작합니다...")

    for video in videos_data:
        animal_id = video.get("animal_id")
        video_url = video.get("video_url")
        d_day = video.get("D-day")
        breed = video.get("breed", "유기동물")
        
        # 이미 최종 영상이 있는지 확인 (건너뛰기 로직)
        final_filename = f"final_{animal_id}.mp4"
        final_path = os.path.join(output_dir, final_filename)
        
        if os.path.exists(final_path):
            print(f"[{animal_id}] 이미 처리된 영상입니다. 건너뜁니다.")
            video["final_path"] = os.path.abspath(final_path)
            continue

        temp_video = f"temp_{animal_id}.mp4"
        
        try:
            # 1. 영상 다운로드 (URL인 경우)
            if video_url.startswith("http"):
                print(f"[{animal_id}] 영상 다운로드 중...")
                resp = requests.get(video_url)
                with open(temp_video, "wb") as f:
                    f.write(resp.content)
            else:
                temp_video = video_url # 로컬 경로인 경우

            print(f"[{animal_id}] 자막 합성 작업 중...")
            
            # 2. MoviePy로 영상 로드
            clip = VideoFileClip(temp_video)
            
            # 3. 자막 데이터 구성 (D-day별 두 줄 자막)
            status = video.get("status", "waiting")
            end_date_raw = video.get("end_date", "") # animals.json에서 가져오도록 보완 필요 (현재 videos.json에 없으면 breed 활용)
            
            # 날짜 포맷팅 (YYYYMMDD -> YYYY-MM-DD)
            formatted_date = ""
            if end_date_raw and len(end_date_raw) == 8:
                formatted_date = f"{end_date_raw[:4]}-{end_date_raw[4:6]}-{end_date_raw[6:]}"

            line1, line2 = "", ""
            if status == "adopted":
                line1 = "가족을 찾았습니다"
                line2 = formatted_date
            elif status == "euthanized":
                line1 = breed.replace("[개] ", "").replace("[고양이] ", "")
                line2 = formatted_date
            elif d_day == 3:
                line1 = f"{breed.replace('[개] ', '').replace('[고양이] ', '')}입니다"
                line2 = "3일이 남았습니다"
            elif d_day == 2:
                line1 = f"{breed.replace('[개] ', '').replace('[고양이] ', '')}입니다"
                line2 = "내일 모레가 마지막 날입니다"
            elif d_day == 1:
                line1 = f"{breed.replace('[개] ', '').replace('[고양이] ', '')}입니다"
                line2 = "내일이 마지막 날입니다"
            else:
                line1 = f"{breed.replace('[개] ', '').replace('[고양이] ', '')}"
                line2 = "가족을 기다리고 있습니다"

            # 4. 자막 클립 생성 (첫 3초간 표시)
            font_path = "Malgun-Gothic" 
            
            # 첫 번째 줄
            sub_clip1 = TextClip(
                text=line1,
                font=font_path,
                font_size=80,
                color='white',
                stroke_color='black',
                stroke_width=1.5,
                duration=3
            ).with_position(('center', clip.h - 350))

            # 두 번째 줄 (더 크게 강조)
            sub_clip2 = TextClip(
                text=line2,
                font=font_path,
                font_size=100,
                color='white',
                stroke_color='black',
                stroke_width=2,
                duration=3
            ).with_position(('center', clip.h - 220))

            # 5. 합성
            final_clip = CompositeVideoClip([clip, sub_clip1, sub_clip2])
            
            # 5. 저장
            final_clip.write_videofile(final_path, codec="libx264", audio_codec="aac", fps=24)
            
            video["final_path"] = os.path.abspath(final_path)
            print(f"[{animal_id}] 합성 완료: {final_path}")

        except Exception as e:
            print(f"[{animal_id}] 오류 발생: {e}")
        finally:
            # 임시 파일 삭제
            if os.path.exists(temp_video) and temp_video.startswith("temp_"):
                os.remove(temp_video)

    # 업데이트된 정보 저장
    with open(input_file, "w", encoding="utf-8") as f:
        json.dump(videos_data, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    add_subtitles()
