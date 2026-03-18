import os
import json
import requests
from datetime import datetime
from dotenv import load_dotenv

def track_animal_status():
    load_dotenv()
    api_key = os.getenv("ANIMAL_API_KEY")
    if not api_key:
        print("에러: ANIMAL_API_KEY가 없습니다.")
        return

    # 설정 파일 경로
    animals_file = "animals.json"
    status_log_file = "status_log.json"
    ended_animals_file = "ended_animals.json"
    
    if not os.path.exists(animals_file):
        print("animals.json 파일이 없습니다. 추적할 동물이 없습니다.")
        return

    # 데이터 로드
    with open(animals_file, "r", encoding="utf-8") as f:
        stored_animals = json.load(f)
    
    if os.path.exists(ended_animals_file):
        with open(ended_animals_file, "r", encoding="utf-8") as f:
            ended_animals = json.load(f)
    else:
        ended_animals = []

    if os.path.exists(status_log_file):
        with open(status_log_file, "r", encoding="utf-8") as f:
            status_logs = json.load(f)
    else:
        status_logs = []

    # 최신 API 데이터 가져오기 (비교용)
    url = "https://apis.data.go.kr/1543061/abandonmentPublicService_v2/abandonmentPublic_v2"
    params = {
        "serviceKey": api_key,
        "numOfRows": "2000", # 상태 변화 확인을 위해 넉넉히 조회
        "pageNo": "1",
        "_type": "json"
    }

    try:
        print("최신 상태를 확인하기 위해 API 데이터를 조회합니다...")
        response = requests.get(url, params=params, timeout=15)
        response.raise_for_status()
        api_data = response.json()
        
        items = api_data.get("response", {}).get("body", {}).get("items", {}).get("item", [])
        if isinstance(items, dict):
            items = [items]
            
        # 최신 상태 매핑 (ID -> 상태)
        current_api_status = {item["desertionNo"]: item.get("processState", "보호중") for item in items}
        
    except Exception as e:
        print(f"API 조회 중 오류 발생: {e}. 로컬 데이터로 D-day만 업데이트합니다.")
        current_api_status = {}

    today = datetime.now().date()
    updated_stored_animals = []
    today_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    summary = {
        "waiting": 0,
        "adopted": 0,
        "euthanized": 0,
        "urgent_d1": 0
    }

    for animal in stored_animals:
        animal_id = animal["id"]
        old_status = animal.get("status", "waiting")
        
        # 1. D-day 업데이트
        old_d_day = animal.get("D-day", 99)
        notice_date = datetime.strptime(animal["보호종료일"], "%Y%m%d").date()
        new_d_day = (notice_date - today).days
        animal["D-day"] = new_d_day
        
        # 2. 상태 결정
        api_status_text = current_api_status.get(animal_id)
        new_status = old_status
        
        if api_status_text:
            if "입양" in api_status_text:
                new_status = "adopted"
            elif any(x in api_status_text for x in ["안락사", "자연사"]):
                new_status = "euthanized"
            elif "보호중" in api_status_text:
                new_status = "waiting"
            else:
                new_status = "waiting" # 기타 상태도 일단 대기
        else:
            # API 목록에 없는데 공고일이 지났다면 종료된 것으로 간주
            if new_d_day < 0:
                new_status = "euthanized" # 데이터가 사라졌으면 대게 종료
            else:
                new_status = "unknown"

        # 3. 상태 변화 기록
        if old_status != new_status:
            log_entry = {
                "animal_id": animal_id,
                "old_status": old_status,
                "new_status": new_status,
                "date": today_str
            }
            # 기적의 케이스 감지 (D-1 이하에서 입양)
            if old_status == "waiting" and new_status == "adopted" and old_d_day <= 1:
                animal["miracle_case"] = True
                print(f"[{animal_id}] ✨ 기적의 케이스 감지! (D-{old_d_day}에 입양)")
            
            status_logs.append(log_entry)
            animal["status"] = new_status
            print(f"[{animal_id}] 상태 변경: {old_status} -> {new_status}")

        # 4. 분류 및 결과 처리
        if new_status in ["adopted", "euthanized"]:
            animal["ended_at"] = today_str
            ended_animals.append(animal)
            if new_status == "adopted": summary["adopted"] += 1
            if new_status == "euthanized": summary["euthanized"] += 1
        else:
            updated_stored_animals.append(animal)
            summary["waiting"] += 1
            if new_d_day == 1:
                summary["urgent_d1"] += 1

    # 파일 저장
    with open(animals_file, "w", encoding="utf-8") as f:
        json.dump(updated_stored_animals, f, ensure_ascii=False, indent=4)
    
    with open(ended_animals_file, "w", encoding="utf-8") as f:
        json.dump(ended_animals, f, ensure_ascii=False, indent=4)
        
    with open(status_log_file, "w", encoding="utf-8") as f:
        json.dump(status_logs, f, ensure_ascii=False, indent=4)

    # 요약 출력
    print("\n--- 오늘 동물 상태 추적 요약 ---")
    print(f"현재 대기중: {summary['waiting']}마리")
    print(f"오늘 입양 완료: {summary['adopted']}마리")
    print(f"오늘 보호종료(만료): {summary['euthanized']}마리")
    if summary['urgent_d1'] > 0:
        print(f"⚠️ 긴급: 안락사 D-1인 동물이 {summary['urgent_d1']}마리 있습니다!")
    print("--------------------------------\n")

if __name__ == "__main__":
    track_animal_status()
