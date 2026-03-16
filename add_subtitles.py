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
            
            # 쇼츠 규격(9:16) 확인 및 조정 (필요시)
            # Kling은 이미 9:16으로 생성하지만 안전을 위해 체크
            
            # 3. 자막 클립 생성 (폰트는 나중에 사용자가 시스템에 맞게 조정 필요)
            # Windows 기본 한글 폰트: 'Malgun-Gothic'
            font_path = "Malgun-Gothic" 
            
            # 상단 제목 서브타이틀
            title_text = "공공보호소 긴급 공고"
            title_clip = TextClip(
                text=title_text,
                font=font_path,
                font_size=60,
                color='white',
                stroke_color='black',
                stroke_width=2,
                duration=clip.duration
            ).with_position(('center', 100))

            # 중앙 품종 정보
            breed_clip = TextClip(
                text=breed,
                font=font_path,
                font_size=80,
                color='yellow',
                stroke_color='black',
                stroke_width=2,
                duration=clip.duration
            ).with_position(('center', 'center'))

            # 하단 D-day (강조)
            dday_text = f"안락사까지 D-{d_day}" if d_day != "알 수 없음" else "가족을 기다려요"
            dday_clip = TextClip(
                text=dday_text,
                font=font_path,
                font_size=100,
                color='red',
                stroke_color='white',
                stroke_width=3,
                duration=clip.duration
            ).with_position(('center', clip.h - 200))

            # 하단 배경 바 (가독성 증대)
            # bg_bar = ColorClip(size=(clip.w, 150), color=(0, 0, 0), duration=clip.duration).with_opacity(0.5).with_position(('center', clip.h - 225))

            # 4. 합성
            final_clip = CompositeVideoClip([clip, title_clip, breed_clip, dday_clip])
            
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
