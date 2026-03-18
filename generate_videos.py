import os
import time
import json
import requests
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

def get_headers():
    piapi_key = os.getenv("PIAPI_KEY")
    return {
        "x-api-key": piapi_key,
        "Accept": "application/json",
        "Content-Type": "application/json"
    }

def request_video_generation(prompt):
    """PiAPI Unified API에 영상 생성 요청을 보냅니다."""
    url = "https://api.piapi.ai/api/v1/task"
    payload = {
        "model": "kling",
        "task_type": "video_generation",
        "input": {
            "prompt": prompt,
            "duration": 5,
            "aspect_ratio": "9:16",
            "mode": "std"
        }
    }
    
    response = requests.post(url, headers=get_headers(), json=payload)
    response.raise_for_status()
    res_data = response.json()
    
    # Unified API는 data.task_id 반환
    task_id = res_data.get("data", {}).get("task_id")
    return task_id

def check_video_status(task_id):
    """Unified API 상태를 확인합니다."""
    url = f"https://api.piapi.ai/api/v1/task/{task_id}"
    response = requests.get(url, headers=get_headers())
    response.raise_for_status()
    data = response.json()
    
    status = data.get("data", {}).get("status")
    video_url = None
    
    if status in ["completed", "succeeded", "success", "SUCCESS", "COMPLETED"]:
        # 영상 URL 추출 (Unified API 구조)
        outputs = data.get("data", {}).get("output", {})
        if isinstance(outputs, dict):
            video_url = outputs.get("video_url") or outputs.get("url")
            if not video_url and "videos" in outputs:
                video_url = outputs["videos"][0].get("url")
                
    return status, video_url

def batch_generate_videos(limit=1):
    """
    배치 영상 생성 작업을 수행합니다.
    limit: 이번 실행에서 새로 요청할 영상의 최대 개수
    """
    input_file = "prompts.json"
    output_file = "videos.json"

    if not os.path.exists(input_file):
        print("prompts.json 파일이 없습니다.")
        return

    # 기존 생성 결과 로드
    generated_videos = []
    if os.path.exists(output_file):
        with open(output_file, "r", encoding="utf-8") as f:
            try:
                generated_videos = json.load(f)
            except:
                generated_videos = []

    # 이미 생성된 프롬프트 목록 (중복 생성 방지)
    existing_prompts = {v["prompt"] for v in generated_videos}

    with open(input_file, "r", encoding="utf-8") as f:
        animals_data = json.load(f)

    newly_requested = 0
    
    for animal in animals_data:
        animal_id = animal["animal_id"]
        d_day = animal["D-day"]
        
        for prompt in animal["prompts"]:
            if newly_requested >= limit:
                print(f"\n설정한 생성 제한({limit}개)에 도달했습니다. 작업을 중단합니다.")
                return

            if prompt in existing_prompts:
                # 이미 생성된 영상이면 건너뜁니다.
                continue

            print(f"\n[{animal_id}] 신규 영상 생성 시작...")
            print(f"프롬프트: {prompt}")

            try:
                task_id = request_video_generation(prompt)
                print(f"작업 접수 완료 (ID: {task_id}). 상태를 확인합니다...")
                
                newly_requested += 1
                
                # 폴링 시작 (최대 10분 정도 대기하도록 설정 가능하지만 여기선 단순 루프)
                while True:
                    status, video_url = check_video_status(task_id)
                    print(f"상태: {status}...")
                    
                    if video_url:
                        print(f"성공! URL: {video_url}")
                        # 결과 저장
                        result = {
                            "animal_id": animal_id,
                            "D-day": d_day,
                            "prompt": prompt,
                            "task_id": task_id,
                            "video_url": video_url,
                            "created_at": time.strftime("%Y-%m-%d %H:%M:%S")
                        }
                        generated_videos.append(result)
                        with open(output_file, "w", encoding="utf-8") as out_f:
                            json.dump(generated_videos, out_f, ensure_ascii=False, indent=4)
                        break
                    
                    if status in ["failed", "error", "FAILED", "ERROR"]:
                        print(f"생성 실패 (ID: {task_id})")
                        break
                    
                    time.sleep(15) # 폴링 간격을 조금 늘림 (15초)

            except requests.exceptions.HTTPError as e:
                print(f"API 요청 에러 발생: {e.response.status_code}")
                print(f"상세 에러 내용: {e.response.text}")
                if e.response.status_code == 400:
                    print("파라미터 설정이나 데이터 형식을 다시 확인해야 합니다.")
                return
            except Exception as e:
                print(f"오류 발생: {e}")

def create_longform_videos():
    """입양/기적 케이스 동물의 과거 클립들을 모아 롱폼 영상을 제작합니다."""
    # (내용은 이전과 동일)
    from moviepy import VideoFileClip, concatenate_videoclips
    
    videos_file = "videos.json"
    animals_file = "animals.json"
    output_dir = "longform_videos"
    os.makedirs(output_dir, exist_ok=True)
    
    if not os.path.exists(videos_file) or not os.path.exists(animals_file):
        return

    with open(videos_file, "r", encoding="utf-8") as f:
        videos = json.load(f)
    with open(animals_file, "r", encoding="utf-8") as f:
        animals = json.load(f)

    # 상태가 adopted인 동물 필터링
    adopted_animals = [a for a in animals if a.get("status") == "adopted"]
    
    for animal in adopted_animals:
        animal_id = animal["id"]
        breed = animal.get("품종", "유기동물").replace("[개] ", "").replace("[고양이] ", "").replace("[기타] ", "")
        is_miracle = animal.get("miracle_case", False)
        
        relevant_videos = [v for v in videos if v["animal_id"] == animal_id]
        clips_paths = [v.get("final_path") for v in sorted(relevant_videos, key=lambda x: x.get("D-day", 0), reverse=True) if v.get("final_path")]
        
        if len(clips_paths) < 2:
            continue
            
        print(f"[{animal_id}] 롱폼 영상 제작 시작... (클립 수: {len(clips_paths)})")
        
        try:
            video_clips = [VideoFileClip(p) for p in clips_paths if os.path.exists(p)]
            if not video_clips: continue
                
            final_story = concatenate_videoclips(video_clips)
            filename = f"miracle_{animal_id}.mp4" if is_miracle else f"adopted_{animal_id}.mp4"
            final_story.write_videofile(os.path.join(output_dir, filename), codec="libx264", audio_codec="aac")
            print(f"[{animal_id}] 롱폼 영상 저장 완료: {filename}")
            for c in video_clips: c.close()
        except Exception as e:
            print(f"[{animal_id}] 롱폼 영상 제작 중 오류: {e}")

if __name__ == "__main__":
    batch_generate_videos(limit=1)
    create_longform_videos()
