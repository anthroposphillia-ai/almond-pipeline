import os
import json
import requests
from datetime import datetime
from dotenv import load_dotenv

def fetch_abandoned_animals():
    # .env 파일에서 설정값(API 키)을 불러옵니다.
    load_dotenv()
    api_key = os.getenv("ANIMAL_API_KEY")
    
    if not api_key or api_key.startswith("여기에_"):
        print("에러 문구 (Error): API key is missing or not configured in .env file.")
        print("한국어 설명: .env 파일에 공공API 인증키(ANIMAL_API_KEY)가 입력되지 않았습니다. 올바른 키를 넣어주세요.")
        return

    # 사용자께서 요청하신 공공데이터 API 주소입니다.
    url = "https://openapi.animal.go.kr/openapi/service/rest/abandonedAnimal/getAbandonedAnimal"
    
    # 오늘 날짜를 구합니다. (예: 2026-03-16)
    today = datetime.now().date()
    
    # API 요청에 필요한 변수들을 설정합니다.
    params = {
        "ServiceKey": api_key,
        "pageNo": "1",          # 첫 번째 페이지
        "numOfRows": "1000",    # 한 번에 가져올 데이터 개수 (넉넉하게 설정)
        "_type": "json"         # 결과값을 JSON 형태로 받기
    }

    print("데이터를 가져오는 중입니다. 잠시만 기다려주세요...")
    
    try:
        # 서버에 데이터를 요청합니다.
        response = requests.get(url, params=params)
        response.raise_for_status() # 요청에 실패하면 에러를 발생시킵니다.
        data = response.json()
    except requests.exceptions.RequestException as e:
        print(f"에러 문구 (Error): Network request failed - {e}")
        print("한국어 설명: 인터넷 연결에 문제가 있거나, 공공데이터 서버에 접속할 수 없습니다. 또는 API 키가 유효하지 않을 수 있습니다.")
        return
    except json.JSONDecodeError as e:
        print(f"에러 문구 (Error): Failed to parse JSON response - {e}")
        print("한국어 설명: 서버에서 받은 데이터를 읽을 수 없습니다. API 키가 잘못되어 에러 메시지가 일반 텍스트로 왔을 수 있습니다.")
        return

    # 응답받은 데이터에서 동물 목록을 추출합니다. (공공데이터 포털 표준 구조를 따름)
    try:
        items = data.get("response", {}).get("body", {}).get("items", {})
        if not items:
            animal_list = []
        else:
            animal_list = items.get("item", [])
            # 결과가 한 마리만 있을 때는 리스트가 아니라 딕셔너리로 오므로, 리스트로 감싸줍니다.
            if isinstance(animal_list, dict):
                animal_list = [animal_list]
    except AttributeError:
        animal_list = []

    filtered_animals = []

    # 전체 동물을 하나씩 확인하면서 조건에 맞는 동물만 골라냅니다.
    for animal in animal_list:
        # 공고종료일(보호종료일)을 가져옵니다. (ex: "20260319")
        notice_edt_str = animal.get("noticeEdt")
        if not notice_edt_str:
            continue
            
        try:
            # 문자열로 된 날짜를 계산 가능한 날짜 객체로 바꿉니다.
            notice_date = datetime.strptime(str(notice_edt_str), "%Y%m%d").date()
            
            # 보호종료일과 오늘 날짜의 차이(D-day)를 계산합니다.
            d_day = (notice_date - today).days
            
            # D-day가 0일에서 3일 사이(오늘부터 3일 이내)인지 확인합니다.
            if 0 <= d_day <= 3:
                # 필요한 정보만 새 사전에 담습니다.
                animal_info = {
                    "사진URL": animal.get("popfile", "사진 없음"),
                    "품종": animal.get("kindCd", "품종 모름"),
                    "나이": animal.get("age", "나이 모름"),
                    "성별": animal.get("sexCd", "성별 모름"), # M:수컷, F:암컷, Q:미상
                    "보호소위치": animal.get("careAddr", "주소 없음"),
                    "보호종료일": str(notice_edt_str),
                    "D-day": d_day
                }
                filtered_animals.append(animal_info)
        except ValueError:
            # 날짜 형식이 잘못된 경우 무시하고 넘어갑니다.
            continue

    # 완성된 동물 목록을 animals.json 파일로 저장합니다.
    with open("animals.json", "w", encoding="utf-8") as json_file:
        # ensure_ascii=False로 설정하여 한글이 깨지지 않게 합니다.
        json.dump(filtered_animals, json_file, ensure_ascii=False, indent=4)

    # 최종적으로 찾은 동물 마리 수를 화면에 보여줍니다.
    print(f"\n작업 완료! 조건(보호 종료일 3일 이내)에 맞는 동물을 총 {len(filtered_animals)}마리 찾았습니다.")
    print("결과는 'animals.json' 파일에 저장되었습니다.")

if __name__ == "__main__":
    fetch_abandoned_animals()
