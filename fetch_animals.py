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

    # 테스트할 3가지 API 엔드포인트 목록
    endpoints = [
        "https://apis.data.go.kr/1543061/abandonmentPublicService_v2/abandonmentPublic",
        "https://apis.data.go.kr/1543061/abandonmentPublicService_v2",
        "https://openapi.animal.go.kr/openapi/service/rest/abandonedAnimal/getAbandonedAnimal"
    ]
    
    # API 요청에 공통으로 사용할 변수 (인코딩 없이 원본 키 그대로 사용)
    params = {
        "serviceKey": api_key,
        "numOfRows": "3",  
        "pageNo": "1",     
        "_type": "json"    
    }

    print("\n[API 엔드포인트 테스트 시작]")
    
    for i, url in enumerate(endpoints, 1):
        print(f"\n==========================================")
        print(f"테스트 버전 {i}: {url.split('.kr/')[1] if '.kr/' in url else url}")
        
        try:
            # 타임아웃을 주어 무한 대기 방지
            response = requests.get(url, params=params, timeout=10)
            
            print(f"상태 코드 (Status Code): {response.status_code}")
            
            # 응답 앞 200자만 잘라서 출력
            raw_body = response.text
            print(f"응답 본문 (앞 200자): {raw_body[:200]}")
            
        except requests.exceptions.RequestException as e:
            print(f"[네트워크 에러 발생] {e}")

if __name__ == "__main__":
    fetch_abandoned_animals()
