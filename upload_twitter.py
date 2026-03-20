import os
import json
import sys
import io

# 윈도우 터미널(CP949)에서도 UTF-8(이모지 등) 출력을 안전하게 하기 위해 설정
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def upload_to_twitter(video_path, title, breed, status, animal_id, d_day):
    """트위터 업로드 시뮬레이션"""
    # 유튜브 URL 로드
    yt_urls = {}
    if os.path.exists("youtube_urls.json"):
        with open("youtube_urls.json", "r", encoding="utf-8") as f:
            yt_urls = json.load(f)
    
    yt_link = yt_urls.get(animal_id, "(유튜브 링크 생성 중)")
    playlist_link = "https://youtube.com/playlist?list=MEMORIAL_LIST"

    print(f"\n- 트윗 텍스트:")
    if status == "euthanized":
        breed_clean = breed.replace("[개] ", "").replace("[고양이] ", "").replace("[기타] ", "")
        print(f"  {breed_clean}\n  보호기간은 10일이었습니다\n  \n  #유기동물\n  → {playlist_link}")
        print("  구분: 사진 (Memorial Photo)")
    elif d_day == 2:
        print(f"  이 강아지에게 2일이 남았습니다\n  이름이 없습니다. 번호만 있습니다.\n  \n  #유기동물 #보호소\n  → {yt_link}")
        print("  구분: 영상 (Short Video)")
    else:
        print(f"  🚨 [D-{d_day}] {breed} 가족을 찾습니다.\n  \n  #유기동물 #입양\n  → {yt_link}")
        print("  구분: 영상 (Short Video)")

    # 이름 채택 댓글 자동 답글 (추가 단계 10)
    if status in ["adopted", "euthanized"]:
         if os.path.exists("status_log.json"):
             with open("status_log.json", "r", encoding="utf-8") as f:
                 logs = json.load(f)
                 my_log = next((l for l in logs if l["animal_id"] == animal_id and l["new_status"] == status), None)
                 
                 if my_log and my_log.get("name") and my_log.get("name_comment_platform") == "twitter":
                     comment_id = my_log["name_comment_id"]
                     name = my_log["name"]
                     
                     replied = []
                     if os.path.exists("replied_comments.json"):
                         with open("replied_comments.json", "r", encoding="utf-8") as rf:
                             replied = json.load(rf)
                     
                     if comment_id not in replied:
                         print(f"  [자동 답글 실행 - Twitter(X)]")
                         if status == "euthanized":
                             print(f"  💬 \"{name}는 오늘 떠났습니다. 이름을 지어주셔서 감사합니다. {name}라는 이름은 '기억합니다' 재생목록에 영원히 남습니다. 🕯\"")
                         else:
                             print(f"  💬 \"{name}이가 가족을 찾았습니다 🐾 이름을 지어주셔서 감사합니다. {name}이의 이름이 빛났습니다.\"")
                         
                         replied.append(comment_id)
                         with open("replied_comments.json", "w", encoding="utf-8") as wf:
                             json.dump(replied, wf, ensure_ascii=False, indent=4)
                     else:
                         print(f"  (이미 답글을 단 멘션입니다: {comment_id})")

    return "TWITTER_SUCCESS"

if __name__ == "__main__":
    print("================================")
    print(f"[09:10] upload_twitter.py 실행 (시뮬레이션)")
    print("================================")
    print("업로드 예정 목록:")
    input_file = "videos.json"
    if os.path.exists(input_file):
        with open(input_file, "r", encoding="utf-8") as f:
            videos = json.load(f)
            for v in videos:
                upload_to_twitter(v.get("final_path", ""), f"[D-{v['D-day']}] {v['breed']}", v['breed'], v.get('status', 'waiting'), v.get('animal_id'), v.get('D-day'))
    print("")
