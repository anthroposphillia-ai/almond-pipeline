import os
import json
import requests
from moviepy import VideoFileClip, TextClip, CompositeVideoClip, ColorClip
from moviepy.video.fx import Resize
import sys
import io

# 윈도우 터미널(CP949)에서도 UTF-8(이모지 등) 출력을 안전하게 하기 위해 설정
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

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

    # animals.json 데이터 로드 (정보 보강용)
    animals_ref = {}
    if os.path.exists("animals.json"):
        try:
            with open("animals.json", "r", encoding="utf-8") as af:
                animals_ref = {a["id"]: a for a in json.load(af)}
        except: pass

    for video in videos_data:
        animal_id = video.get("animal_id")
        video_url = video.get("video_url")
        d_day = video.get("D-day")
        breed = video.get("breed", "유기동물")
        status = video.get("status", "waiting")
        end_date_raw = video.get("end_date", "") or (animals_ref.get(animal_id, {}).get("보호종료일", ""))
        
        # 품종에 따른 용어 정제
        breed_clean = breed.replace("[개] ", "").replace("[고양이] ", "").replace("[기타] ", "")
        if "[개]" in breed:
            subject_name = "이 강아지"
        elif "[고양이]" in breed:
            subject_name = "이 고양이"
        else:
            subject_name = f"이 {breed_clean}"

        # 날짜 포맷팅
        formatted_date = ""
        if end_date_raw and len(end_date_raw) == 8:
            formatted_date = f"{end_date_raw[:4]}-{end_date_raw[4:6]}-{end_date_raw[6:]}"

        line1, line2 = "", ""
        if status == "adopted":
            line1 = f"{subject_name}가 가족을 찾았습니다"
            line2 = formatted_date
        elif status == "euthanized":
            next_animal_id = "다음 동물"
            try:
                waiting_animals = [a for a in animals_ref.values() if a.get("id") != animal_id and a.get("status", "waiting") == "waiting"]
                if waiting_animals:
                    next_animal_id = waiting_animals[0].get("id")[-3:]
            except: pass
            line1 = f"{animal_id[-3:]}호는 오늘 떠났습니다.\n보호기간은 10일이었습니다."
            line2 = f"오늘도 새로운 동물들이 들어왔습니다.\n{next_animal_id}호입니다."
        elif d_day == 3:
            line1 = f"{breed_clean}입니다"
            line2 = "3일이 남았습니다"
        elif d_day == 2:
            line1 = f"{breed_clean}입니다"
            line2 = "내일 모레가 마지막 날입니다"
        elif d_day == 1:
            line1 = f"{breed_clean}입니다"
            line2 = "내일이 마지막 날입니다"
        else:
            line1 = breed_clean
            line2 = "가족을 기다리고 있습니다"

        video["line1"] = line1
        video["line2"] = line2
        video["is_named"] = "이름" in video.get("특징", "") or "이름" in animals_ref.get(animal_id, {}).get("특징", "")

        # 파일 존재 확인 및 건너뛰기
        final_filename = f"final_{animal_id}.mp4"
        final_path = os.path.join(output_dir, final_filename)
        if os.path.exists(final_path):
            video["final_path"] = os.path.abspath(final_path)
            continue

        temp_video = f"temp_{animal_id}.mp4"
        try:
            if video_url.startswith("http"):
                resp = requests.get(video_url)
                with open(temp_video, "wb") as f:
                    f.write(resp.content)
            else:
                temp_video = video_url

            clip = VideoFileClip(temp_video)
            font_path = "Malgun-Gothic"
            if os.name == 'nt':
                possible_font_path = "C:\\Windows\\Fonts\\malgun.ttf"
                if os.path.exists(possible_font_path):
                    font_path = possible_font_path
            
            sub_clip1 = TextClip(
                text=line1,
                font=font_path,
                font_size=60 if "\n" in line1 else 80,
                color='white',
                stroke_color='black',
                stroke_width=1.5,
                duration=clip.duration
            ).with_position(('center', clip.h - 400 if "\n" in line1 else clip.h - 350))

            sub_clip2 = TextClip(
                text=line2,
                font=font_path,
                font_size=70 if "\n" in line2 else 100,
                color='white',
                stroke_color='black',
                stroke_width=2,
                duration=clip.duration
            ).with_position(('center', clip.h - 220))

            final_clip = CompositeVideoClip([clip, sub_clip1, sub_clip2])
            final_clip.write_videofile(final_path, codec="libx264", audio_codec="aac", fps=24, logger=None)
            video["final_path"] = os.path.abspath(final_path)

        except Exception as e:
            print(f"[{animal_id}] 오류 발생: {e}")
        finally:
            if os.path.exists(temp_video) and temp_video.startswith("temp_"):
                try: os.remove(temp_video)
                except: pass

    # 상세 출력
    print("================================")
    print(f"[09:06] add_subtitles.py 실행")
    print("================================")
    for v in videos_data:
        named_tag = "[이름 있음]" if v.get("is_named") else "[이름 없음]"
        print(f"- {v['animal_id']} {named_tag}")
        print(f"  줄1: {v.get('line1', '').replace(chr(10), ' ')}")
        print(f"  줄2: {v.get('line2', '').replace(chr(10), ' ')}")
    print("")

    with open(input_file, "w", encoding="utf-8") as f:
        json.dump(videos_data, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    add_subtitles()
