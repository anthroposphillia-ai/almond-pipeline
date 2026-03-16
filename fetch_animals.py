import os
import json
import requests
from datetime import datetime
from dotenv import load_dotenv

def fetch_abandoned_animals():
    # .env 파일에서 설정값(API 키)을 불러옵니다.
    load_dotenv()
    api_key = os.getenv("ANIMAL_API_KEY")
    
    if not api_key:
        print("에러 (Error): .env 파일에 ANIMAL_API_KEY가 없습니다.")
        return

    # 정상 동작 확인된 V2 엔드포인트
    url = "https://apis.data.go.kr/1543061/abandonmentPublicService_v2/abandonmentPublic_v2"
    
    # 오늘 날짜
    today = datetime.now().date()
    
    # 파라미터 구성
    params = {
        "serviceKey": api_key,
        "numOfRows": "1000",    # 전체 조회를 위해 넉넉히 설정
        "pageNo": "1",
        "_type": "json"
    }

    print("유기동물 데이터를 수집 중입니다...")
    
    try:
        response = requests.get(url, params=params, timeout=15)
        response.raise_for_status()
        data = response.json()
        
        # 데이터 구조 진입
        items_data = data.get("response", {}).get("body", {}).get("items", {})
        if not items_data:
            print("데이터가 없습니다.")
            return
            
        animal_list = items_data.get("item", [])
        if isinstance(animal_list, dict):
            animal_list = [animal_list]

        filtered_animals = []

        for animal in animal_list:
            # 보호종료일 (noticeEdt: YYYYMMDD)
            notice_edt_str = animal.get("noticeEdt")
            if not notice_edt_str:
                continue
                
            try:
                notice_date = datetime.strptime(str(notice_edt_str), "%Y%m%d").date()
                d_day = (notice_date - today).days
                
                # 오늘 기준으로 3일 이내 (D-day 0, 1, 2, 3)
                if 0 <= d_day <= 3:
                    animal_info = {
                        "id": animal.get("desertionNo"),
                        "사진URL": animal.get("popfile1") or animal.get("popfile"),
                        "품종": animal.get("kindFullNm") or animal.get("kindCd"),
                        "나이": animal.get("age"),
                        "성별": animal.get("sexCd"),
                        "보호소위치": animal.get("careAddr"),
                        "보호종료일": str(notice_edt_str),
                        "D-day": d_day
                    }
                    filtered_animals.append(animal_info)
            except ValueError:
                continue

        # 결과 저장
        with open("animals.json", "w", encoding="utf-8") as f:
            json.dump(filtered_animals, f, ensure_ascii=False, indent=4)

        print(f"\n작업 완료! 조건(보호 종료일 3일 이내)에 맞는 동물을 총 {len(filtered_animals)}마리 찾았습니다.")
        print("결과는 'animals.json' 파일에 저장되었습니다.")

    except Exception as e:
        print(f"오류 발생: {e}")

if __name__ == "__main__":
    fetch_abandoned_animals()
