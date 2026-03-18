import json
import os
import sys
from datetime import datetime

# 윈도우 터미널(CP949)에서도 UTF-8(이모지 등) 출력을 안전하게 하기 위해 설정
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def post_monthly_summary():
    status_log_file = "status_log.json"
    
    if not os.path.exists(status_log_file):
        print(f"에러: {status_log_file} 파일이 없습니다. 통계를 집계할 수 없습니다.")
        return

    with open(status_log_file, "r", encoding="utf-8") as f:
        logs = json.load(f)

    # 지난달 데이터 필터링 (현재 날짜 기준 이전 달)
    today = datetime.now()
    # 시뮬레이션을 위해 현재 달의 통계를 뽑는 것으로 우선 구현
    current_month = today.month
    current_year = today.year

    adopted_count = 0
    euthanized_count = 0

    for entry in logs:
        log_date = datetime.strptime(entry["date"], "%Y-%m-%d %H:%M:%S")
        if log_date.year == current_year and log_date.month == current_month:
            if entry["new_status"] == "adopted":
                adopted_count += 1
            elif entry["new_status"] == "euthanized":
                euthanized_count += 1

    # 게시글 내용 구성 (Step 1046 반영)
    content = f"""지난달 함께한 동물들
   
입양: {adopted_count}마리 🐾
떠남: {euthanized_count}마리
   
우리가 바꿔야 할 숫자입니다.
   
이번달도 함께해주세요."""

    print("====================================")
    print("커뮤니티 게시글 생성 (시뮬레이션)")
    print("====================================")
    print(content)
    print("====================================")
    
    # 실제 구현 시 YouTube Community API가 없으므로 로그로 기록
    with open("monthly_summary_log.txt", "a", encoding="utf-8") as f:
        f.write(f"\n[{datetime.now().strftime('%Y-%m-%d')}] 게시 예정 내용:\n")
        f.write(content + "\n")
        f.write("-" * 30 + "\n")

if __name__ == "__main__":
    post_monthly_summary()
