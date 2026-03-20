import os
import json
import sys
import io

# 윈도우 터미널(CP949)에서도 UTF-8(이모지 등) 출력을 안전하게 하기 위해 설정
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def upload_to_tiktok(video_path, title, breed, status, d_day, animal_id):
    """틱톡 업로드 시뮬레이션"""
    if status == "euthanized":
        print(f"[{title}] 업로드 안 함: 안락사 결말 정책에 따라 틱톡 업로드를 생략합니다.")
        return

    breed_tag = breed.replace("[개] ", "").replace("[고양이] ", "").replace("[기타] ", "")
    
    caption = ""
    if status == "adopted":
        caption = "가족을 찾았습니다 🐾\n기다려줘서 고마워요.\n.\n.\n#유기동물 #입양완료 #adoption #adoptdontshop #rescuedog"
    elif d_day == 1:
        caption = f"내일입니다.\n이 강아지의 마지막 날입니다.\n.\n.\n#유기동물 #보호소 #입양 #유기견 #동물보호 #사지말고입양하세요 #straydog #adoption #animalrescue"
    elif d_day == 2:
        caption = f"이 강아지에게 2일이 남았습니다.\n이름도 없습니다. 번호만 있습니다.\n이름을 달아주세요 💬\n.\n.\n#유기동물 #보호소 #입양 #유기견 #동물보호 #사지말고입양하세요 #straydog #adoption #animalrescue #rescuedog #adoptdontshop"
    else:
        caption = f"{title} #유기동물 #사지말고입양하세요"

    print(f"- {title}")
    print(f"  캡션 전체:\n{caption}")

    # 이름 채택 댓글 자동 답글 (추가 단계 10)
    if status == "adopted": # 틱톡은 입양 시에만 업로드됨
         if os.path.exists("status_log.json"):
             with open("status_log.json", "r", encoding="utf-8") as f:
                 logs = json.load(f)
                 my_log = next((l for l in logs if l["animal_id"] == animal_id and l["new_status"] == status), None)
                 
                 if my_log and my_log.get("name") and my_log.get("name_comment_platform") == "tiktok":
                     comment_id = my_log["name_comment_id"]
                     name = my_log["name"]
                     
                     replied = []
                     if os.path.exists("replied_comments.json"):
                         with open("replied_comments.json", "r", encoding="utf-8") as rf:
                             replied = json.load(rf)
                     
                     if comment_id not in replied:
                         print(f"  [자동 답글 실행 - TikTok]")
                         print(f"  💬 \"{name}이가 가족을 찾았습니다 🐾 이름을 지어주셔서 감사합니다. {name}이의 이름이 빛났습니다.\"")
                         
                         replied.append(comment_id)
                         with open("replied_comments.json", "w", encoding="utf-8") as wf:
                             json.dump(replied, wf, ensure_ascii=False, indent=4)
                     else:
                         print(f"  (이미 답글을 단 댓글입니다: {comment_id})")

    return "TIKTOK_SUCCESS"

if __name__ == "__main__":
    print("================================")
    print(f"[09:08] upload_tiktok.py 실행 (시뮬레이션)")
    print("================================")
    print("업로드 예정 목록:")
    input_file = "videos.json"
    if os.path.exists(input_file):
        with open(input_file, "r", encoding="utf-8") as f:
            videos = json.load(f)
            for v in videos:
                upload_to_tiktok(v.get("final_path", ""), f"[D-{v['D-day']}] {v['breed']}", v['breed'], v.get('status', 'waiting'), v.get('D-day'), v.get('animal_id'))
    print("")
