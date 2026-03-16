import os
import time
import json
import requests
from dotenv import load_dotenv

def generate_video():
    load_dotenv()
    piapi_key = os.getenv("PIAPI_KEY")
    
    if not piapi_key:
        print("에러 문구 (Error): PIAPI_KEY is missing in .env file.")
        print("한국어 설명: .env 파일에 PiAPI 키(PIAPI_KEY)가 없습니다. 키를 추가해주세요.")
        return

    input_file = "prompts.json"
    output_file = "videos.json"

    if not os.path.exists(input_file):
        print(f"에러 문구 (Error): File '{input_file}' not found.")
        print("한국어 설명: prompts.json 파일이 없습니다. 프롬프트를 먼저 생성해 주세요.")
        return

    with open(input_file, "r", encoding="utf-8") as f:
        prompts_data = json.load(f)

    if not prompts_data or not prompts_data[0].get("prompts"):
        print("에러 문구: 프롬프트 데이터가 비어 있습니다.")
        return

    # 첫 번째 동물의 첫 번째 프롬프트 1개만 테스트로 가져옵니다.
    test_animal = prompts_data[0]
    animal_id = test_animal.get("animal_id", "알 수 없음")
    d_day = test_animal.get("D-day", "알 수 없음")
    test_prompt = test_animal["prompts"][0]

    print(f"\n[{animal_id}] 동물의 영상 생성을 시작합니다.")
    print(f"프롬프트: {test_prompt}")

    # PiAPI Kling API 엔드포인트 및 헤더
    url = "https://api.piapi.ai/api/v1/task"
    headers = {
        "x-api-key": piapi_key,
        "Accept": "application/json",
        "Content-Type": "application/json"
    }
    
    # 요청 페이로드 설정 (Unified API 방식)
    payload = {
        "model": "kling",
        "task_type": "video_generation",
        "input": {
            "prompt": test_prompt,
            "duration": 5,
            "aspect_ratio": "9:16"
        }
    }

    try:
        print("\n1. PiAPI 서버(Kling)에 영상 생성 작업을 발송합니다...")
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        res_data = response.json()
        
        # PiAPI 응답 구조에 맞게 작업 ID(task_id) 추출
        task_id = res_data.get("data", {}).get("task_id")
        if not task_id:
            # 다른 구조일 수 있으므로 추가 탐색
            task_id = res_data.get("data", {}).get("id") or res_data.get("id") or res_data.get("task_id")
             
        if not task_id:
             print("에러 (Error): 응답에서 작업 ID를 찾을 수 없습니다. 응답 원문:", res_data)
             return
             
        print(f"작업이 성공적으로 접수되었습니다! (Task ID: {task_id})")
        
        # 2. 영상 생성이 완료될 때까지 10초마다 상태 확인(Polling)
        status_url = f"{url}/{task_id}"
        print("\n2. 영상 생성이 완료될 때까지 조회합니다. (10초 간격으로 확인, 영상 길이에 따라 보통 2~5분 소요)")
        
        video_url = None
        
        while True:
            # 상태 조회 API 요청 (보통 같은 엔드포인트 뒤에 /작업ID 를 붙여서 GET 요청함)
            status_response = requests.get(status_url, headers=headers)
            status_response.raise_for_status()
            status_data = status_response.json()
            
            # 진행 상태(status) 추출
            # PiAPI의 경우 구조가 data.status 이거나 직속 status 일 수 있음
            status = status_data.get("data", {}).get("status") or status_data.get("status")
            
            print(f"현재 상태 (Status): {status} ... (10초 후 다시 확인)")
            
            # 완료(completed)를 의미하는 단어들
            if status in ["completed", "succeeded", "success", "SUCCESS", "COMPLETED"]:
                # 영상 URL 결과물 추출 (반환 구조가 여러 가지인 상황 대비)
                video_url = status_data.get("data", {}).get("video", {}).get("url")
                if not video_url:
                    video_url = status_data.get("data", {}).get("video_url")
                
                # 만약 출력 리스트가 따로 배열로 나오는 구조라면
                if not video_url:
                     outputs = status_data.get("data", {}).get("output", {}).get("videos", [])
                     if outputs and len(outputs) > 0:
                         video_url = outputs[0].get("url")
                
                # 영상 링크를 성공적으로 찾은 경우 종료
                if video_url:
                    break
                else:
                    print("\n에러 (Error): 상태는 완료되었으나 결과 URL 파일 링크를 찾지 못했습니다.", status_data)
                    return
            # 실패(failed)를 의미하는 단어들
            elif status in ["failed", "error", "FAILED", "ERROR"]:
                print(f"\n영상 생성 실패: {status_data}")
                return
                
            # 완료도 실패도 아니라면 (보통 pending, processing, in-progress 등) 10초 대기
            time.sleep(10)

        # 3. 완료된 영상을 videos.json에 추가 저장
        if video_url:
            print(f"\n영상 생성이 완료되었습니다!")
            print(f"다운로드/확인 링크 (URL): {video_url}")
            
            videos_list = []
            if os.path.exists(output_file):
                with open(output_file, "r", encoding="utf-8") as f:
                    try:
                        videos_list = json.load(f)
                    except json.JSONDecodeError:
                        videos_list = []
            
            # 저장할 데이터 구조
            result_entry = {
                "animal_id": animal_id,
                "D-day": d_day,
                "prompt": test_prompt,
                "task_id": task_id,
                "video_url": video_url
            }
            videos_list.append(result_entry)
            
            # 파일 덮어쓰기
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(videos_list, f, ensure_ascii=False, indent=4)
                
            print(f"\n결과가 '{output_file}' 파일에 무사히 저장되었습니다!")

    except requests.exceptions.HTTPError as e:
        status_code = e.response.status_code
        error_msg = e.response.text
        print(f"\nHTTP 통신 에러 문구 (Error {status_code}): {error_msg}")
        print("한국어 설명: PiAPI 요청 중 권한이 없거나, 잔액이 부족하거나, 요청 형식이 잘못되었습니다. PiAPI 사이트에서 잔고나 설정을 확인해 주세요.")
    except requests.exceptions.RequestException as e:
        print(f"\n네트워크 에러 (Error): {e}")
        print("한국어 설명: 인터넷 연결이 끊겼거나 PiAPI 서버가 응답하지 않습니다.")

if __name__ == "__main__":
    generate_video()
