import os
import json
import time

def simulate_video_generation():
    input_file = "prompts.json"
    output_file = "videos.json"
    dummy_dir = "dummy_videos"
    os.makedirs(dummy_dir, exist_ok=True)

    if not os.path.exists(input_file):
        print(f"에러: {input_file}이 없습니다.")
        return

    with open(input_file, "r", encoding="utf-8") as f:
        prompts_data = json.load(f)

    videos_data = []
    
    # 테스트를 위해 상위 몇 개만 진행 (사용자 요청에 따라 조절 가능)
    # 여기서는 수집된 모든 동물에 대해 1개씩만 시뮬레이션
    processed_animals = set()

    print("[시뮬레이션] 영상 생성 단계를 시작합니다.")

    for item in prompts_data:
        animal_id = item["animal_id"]
        if animal_id in processed_animals: continue
        
        print(f"[{animal_id}] AI 영상 생성 시뮬레이션 중...")
        
        # 더미 파일 생성 (실제 파일이 있어야 add_subtitles.py가 작동함)
        # 1초짜리 정적 파일을 복사하거나 만드는 대신, 
        # 간단한 텍스트가 포함된 더미 MP4 파일 경로를 지정
        dummy_path = os.path.join(dummy_dir, f"sim_{animal_id}.mp4")
        
        # MoviePy를 사용하여 아주 짧은 더미 영상 생성 (검증용)
        from moviepy import ColorClip
        clip = ColorClip(size=(720, 1280), color=(0, 0, 0), duration=2)
        clip.write_videofile(dummy_path, fps=24, codec="libx264", logger=None)
        
        video_info = {
            "animal_id": animal_id,
            "video_url": os.path.abspath(dummy_path), # 로컬 경로로 전달
            "D-day": item["D-day"],
            "breed": item["breed"],
            "prompt": item["prompts"][0] if item.get("prompts") else "No prompt available"
        }
        videos_data.append(video_info)
        processed_animals.add(animal_id)
        
        print(f"[{animal_id}] 더미 영상 생성 완료: {dummy_path}")

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(videos_data, f, ensure_ascii=False, indent=4)
        
    print(f"[시뮬레이션] 총 {len(videos_data)}개의 더미 영상 데이터가 videos.json에 저장되었습니다.")

if __name__ == "__main__":
    simulate_video_generation()
