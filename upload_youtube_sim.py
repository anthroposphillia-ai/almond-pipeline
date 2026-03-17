import os
import json

def simulate_upload():
    input_file = "videos.json"
    metadata_file = "metadata.json"
    
    if not os.path.exists(input_file):
        print(f"에러: {input_file}이 없습니다.")
        return

    with open(input_file, "r", encoding="utf-8") as f:
        videos_data = json.load(f)
        
    if not os.path.exists(metadata_file):
        print(f"경고: {metadata_file}이 없어 제목을 생성할 수 없습니다.")
        metadata_data = {}
    else:
        with open(metadata_file, "r", encoding="utf-8") as f:
            metadata_data = json.load(f)

    print("[시뮬레이션] 유튜브 업로드 단계를 시작합니다.")

    upload_count = 0
    for video in videos_data:
        animal_id = video["animal_id"]
        status = video.get("status", "waiting")
        d_day_key = f"D-{video['D-day']}" if video['D-day'] in [1, 2, 3] else "D-3"
        
        if status == "euthanized":
            print(f"[{animal_id}] 업로드 시뮬레이션: SKIPPED (안락사 결말 정책)")
            continue

        # 메타데이터에서 제목 가져오기
        title = metadata_data.get(animal_id, {}).get(d_day_key, {}).get("title", f"[공고] {video['breed']} 가족을 찾습니다")
        
        print(f"[{animal_id}] 업로드 시뮬레이션: SUCCESS")
        print(f" -> 업로드 예정 제목: {title}")
        print(f" -> 자동 작성될 고정 댓글: '입양 문의는 영상 설명란의...'")
        upload_count += 1

    print(f"[시뮬레이션] 총 {upload_count}개의 영상 업로드 시뮬레이션을 마쳤습니다.")
    return upload_count

if __name__ == "__main__":
    simulate_upload()
