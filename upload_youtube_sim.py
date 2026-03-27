import os
import json
import sys
import io

# 윈도우 터미널(CP949)에서도 UTF-8 출력을 안전하게 하기 위해 설정
if sys.platform == "win32":
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    except:
        pass

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
        
        # 이름 채택 댓글 자동 답글 (추가 단계 10) - 업로드 여부와 상관없이 결말 시 수행
        if status in ["adopted", "euthanized"]:
             # status_log에서 관련 정보 찾기
             if os.path.exists("status_log.json"):
                 with open("status_log.json", "r", encoding="utf-8") as f:
                     logs = json.load(f)
                     my_log = next((l for l in logs if l["animal_id"] == animal_id and l["new_status"] == status), None)
                     
                     if my_log and my_log.get("name") and my_log.get("name_comment_platform") == "youtube":
                         comment_id = my_log["name_comment_id"]
                         name = my_log["name"]
                         
                         # 중복 방지 체크
                         replied = []
                         if os.path.exists("replied_comments.json"):
                             with open("replied_comments.json", "r", encoding="utf-8") as rf:
                                 replied = json.load(rf)
                         
                         if comment_id not in replied:
                             print(f"\n  [자동 답글 실행 - YouTube]")
                             if status == "euthanized":
                                 print(f"  💬 \"{name}는 오늘 떠났습니다. 이름을 지어주셔서 감사합니다. {name}라는 이름은 '기억합니다' 재생목록에 영원히 남습니다. 🕯\"")
                             else:
                                 print(f"  💬 \"{name}이가 가족을 찾았습니다 🐾 이름을 지어주셔서 감사합니다. {name}이의 이름이 빛났습니다.\"")
                             
                             # 이력 저장
                             replied.append(comment_id)
                             with open("replied_comments.json", "w", encoding="utf-8") as wf:
                                 json.dump(replied, wf, ensure_ascii=False, indent=4)
                         else:
                             print(f"  (이미 YouTube 답글을 단 댓글입니다: {comment_id})")

        if status == "euthanized":
            print(f"[{animal_id}] 업로드 시뮬레이션: SKIPPED (안락사 결말 정책)")
            continue

        # 메타데이터에서 제목 및 설명 가져오기
        meta = metadata_data.get(animal_id, {}).get(d_day_key, {})
        title = meta.get("title", f"[공고] {video['breed']} 가족을 찾습니다")
        description = meta.get("description", "설명 없음")
        
        # 재생목록 결정
        playlist = "지금 기다리는 아이들"
        if status == "adopted": playlist = "가족을 찾았습니다 🐾"
        elif status == "euthanized": playlist = "기억합니다"

        print(f"\n[{animal_id}] 업로드 시뮬레이션 상세")
        print(f"- 제목: {title}")
        print(f"- 재생목록: {playlist}")
        print(f"- 고정댓글 내용: '✅ 이 {'강아지' if '[개]' in video['breed'] else '고양이'}는 가족을 찾았습니다...'")
        print("- 설명란 전체 내용:")
        print("--------------------------------")
        print(description)
        print("--------------------------------")
        print(f"- Shorts 여부: {'YES' if status != 'euthanized' else 'NO'}")
        print(f"- 롱폼 여부: {'YES' if status == 'adopted' else 'NO'}")
        
        # 이름 채택 댓글 자동 답글 (추가 단계 10)
        if status in ["adopted", "euthanized"]:
             # status_log에서 관련 정보 찾기
             if os.path.exists("status_log.json"):
                 with open("status_log.json", "r", encoding="utf-8") as f:
                     logs = json.load(f)
                     my_log = next((l for l in logs if l["animal_id"] == animal_id and l["new_status"] == status), None)
                     
                     if my_log and my_log.get("name") and my_log.get("name_comment_platform") == "youtube":
                         comment_id = my_log["name_comment_id"]
                         name = my_log["name"]
                         
                         # 중복 방지 체크
                         replied = []
                         if os.path.exists("replied_comments.json"):
                             with open("replied_comments.json", "r", encoding="utf-8") as rf:
                                 replied = json.load(rf)
                         
                         if comment_id not in replied:
                             print(f"\n  [자동 답글 실행 - YouTube]")
                             if status == "euthanized":
                                 print(f"  💬 \"{name}는 오늘 떠났습니다. 이름을 지어주셔서 감사합니다. {name}라는 이름은 '기억합니다' 재생목록에 영원히 남습니다. 🕯\"")
                             else:
                                 print(f"  💬 \"{name}이가 가족을 찾았습니다 🐾 이름을 지어주셔서 감사합니다. {name}이의 이름이 빛났습니다.\"")
                             
                             # 이력 저장
                             replied.append(comment_id)
                             with open("replied_comments.json", "w", encoding="utf-8") as wf:
                                 json.dump(replied, wf, ensure_ascii=False, indent=4)
                         else:
                             print(f"  (이미 답글을 단 댓글입니다: {comment_id})")

        upload_count += 1
        video["youtube_url"] = f"https://youtu.be/{animal_id}"

    # 유튜브 URL 저장 (Issue 5)
    youtube_urls = {v["animal_id"]: v.get("youtube_url") for v in videos_data if "youtube_url" in v}
    with open("youtube_urls.json", "w", encoding="utf-8") as f:
        json.dump(youtube_urls, f, ensure_ascii=False, indent=4)

    print("-" * 32)
    print(f"[09:07] upload_youtube.py 실행 (시뮬레이션)")
    print("-" * 32)
    print(f"- 총 {upload_count}개의 영상 업로드 예정 목록을 확인했습니다.")
    print("- youtube_urls.json 저장 완료")
    print("")
    return upload_count

if __name__ == "__main__":
    simulate_upload()
