import os
import json
import sys
import io

# 윈도우 터미널(CP949)에서도 UTF-8(이모지 등) 출력을 안전하게 하기 위해 설정
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def upload_to_instagram(video_path, title, breed, status, animal_id):
    """인스타그램 업로드 시뮬레이션"""
    print(f"\n- Reels 목록")
    print(f"  제목/캡션: {title} | 인스타그램 전용 캡션")
    print(f"  해시태그 전체: #instagram #reels #animal #volunteer #{animal_id[-6:]}")
    
    # 이름 채택 댓글 자동 답글 (추가 단계 10)
    if status in ["adopted", "euthanized"]:
         if os.path.exists("status_log.json"):
             with open("status_log.json", "r", encoding="utf-8") as f:
                 logs = json.load(f)
                 my_log = next((l for l in logs if l["animal_id"] == animal_id and l["new_status"] == status), None)
                 
                 if my_log and my_log.get("name") and my_log.get("name_comment_platform") == "instagram":
                     comment_id = my_log["name_comment_id"]
                     name = my_log["name"]
                     
                     replied = []
                     if os.path.exists("replied_comments.json"):
                         with open("replied_comments.json", "r", encoding="utf-8") as rf:
                             replied = json.load(rf)
                     
                     if comment_id not in replied:
                         print(f"  [자동 답글 실행 - Instagram]")
                         if status == "euthanized":
                             print(f"  💬 \"{name}는 오늘 떠났습니다. 이름을 지어주셔서 감사합니다. {name}라는 이름은 '기억합니다' 재생목록에 영원히 남습니다. 🕯\"")
                         else:
                             print(f"  💬 \"{name}이가 가족을 찾았습니다 🐾 이름을 지어주셔서 감사합니다. {name}이의 이름이 빛났습니다.\"")
                         
                         replied.append(comment_id)
                         with open("replied_comments.json", "w", encoding="utf-8") as wf:
                             json.dump(replied, wf, ensure_ascii=False, indent=4)
                     else:
                         print(f"  (이미 답글을 단 댓글입니다: {comment_id})")

    return "INSTA_SUCCESS"

if __name__ == "__main__":
    print("================================")
    print(f"[09:09] upload_instagram.py 실행 (시뮬레이션)")
    print("================================")
    print("업로드 예정 목록:")
    input_file = "videos.json"
    if os.path.exists(input_file):
        with open(input_file, "r", encoding="utf-8") as f:
            videos = json.load(f)
            for v in videos:
                upload_to_instagram(v.get("final_path", ""), f"[D-{v['D-day']}] {v['breed']}", v['breed'], v.get('status', 'waiting'), v.get('animal_id'))
    print("")
