import json
import itertools
import os

def generate_video_prompts():
    # 저장된 동물의 정보를 불러옵니다.
    input_file = "animals.json"
    output_file = "prompts.json"
    
    if not os.path.exists(input_file):
        print(f"에러 문구 (Error): File '{input_file}' not found.")
        print(f"한국어 설명: '{input_file}' 파일이 없습니다. 먼저 fetch_animals.py를 통해 데이터를 수집해 주세요.")
        return

    with open(input_file, "r", encoding="utf-8") as f:
        animals = json.load(f)

    if not animals:
        print("동물 데이터가 비어 있습니다. 임시로 테스트 데이터를 생성하여 진행합니다.")
        # 테스트용 임시 동물 데이터 1마리를 추가하여 12개 이상 프롬프트를 만드는 것을 확인합니다.
        animals = [{
            "id": "animal_test_001",
            "사진URL": "test_image.jpg",
            "품종": "[개] 믹스견",
            "나이": "2023(년생)",
            "성별": "M",
            "보호소위치": "서울특별시 어딘가",
            "보호종료일": "20260319",
            "D-day": 3
        }]
    
    # 프롬프트 변수 조합 목록 (영어 번역 적용)
    angles = [
        "close-up shot of the eyes",              # 눈 클로즈업
        "full body shot",                         # 전신
        "profile shot from the side",             # 측면
        "wide full body shot showing the shelter environment" # 보호소 환경 포함 전신
    ]
    
    time_lights = [
        "morning natural light",                  # 자연광 아침
        "evening shadows",                        # 저녁 그림자
        "indoor fluorescent lighting"             # 실내 형광등
    ]
    
    movements = [
        "staring silently into the camera",       # 카메라를 조용히 응시
        "slowly turning its head",                # 고개를 천천히 돌림
        "lying down comfortably"                  # 편안하게 누워있음
    ]

    all_prompts_data = []

    for index, animal in enumerate(animals):
        # 만약 고유 ID가 없다면 임의로 동물 번호를 부여합니다.
        animal_id = animal.get("id", f"animal_{index + 1:03d}")
        breed = animal.get("품종", "")
        d_day = animal.get("D-day", "알 수 없음")
        
        # 동물이 개인지 고양이인지 판단하여 스타일 키워드에 적용
        animal_type = "dog" if "개" in breed else ("cat" if "고양이" in breed else "animal")
        
        # 공통으로 들어갈 스타일 키워드
        style_keywords = f"handheld documentary, natural lighting, shelter {animal_type}, emotional, cinematic"
        
        generated_prompts = []
        
        # 앵글(4), 조명(3), 움직임(3) 을 모두 조합하면 총 4x3x3 = 36개의 프롬프트가 나옵니다.
        # 사용자 요청(최소 12개)을 만족하기 위해 모든 조합을 사용하거나, 일부 조합만 만들 수 있습니다.
        # 여기서는 조명 3, 앵글 4 조합(총 12가지)에 각각 움직임을 하나씩 매칭하여 최소 12개를 생성하겠습니다.
        
        for angle in angles:
            for time_light in time_lights:
                # 움직임은 3가지 중 순서대로 하나씩 돌아가면서 선택 (인덱스 활용)
                movement = movements[(len(generated_prompts)) % len(movements)]
                
                # 최종 영어 프롬프트 문장 구성
                prompt_text = f"A {animal_type} {movement}, {angle}, {time_light}, {style_keywords}"
                generated_prompts.append(prompt_text)

        animal_data = {
            "animal_id": animal_id,
            "D-day": d_day,
            "breed": breed,
            "총_생성된_프롬프트_수": len(generated_prompts),
            "prompts": generated_prompts
        }
        all_prompts_data.append(animal_data)

    # 결과를 prompts.json 파일로 저장합니다.
    with open(output_file, "w", encoding="utf-8") as json_file:
        json.dump(all_prompts_data, json_file, ensure_ascii=False, indent=4)

    print(f"\n작업 완료! {len(animals)}마리의 동물에 대해 프롬프트 자동 생성을 완료했습니다.")
    print(f"결과는 '{output_file}' 파일에 저장되었습니다.")

if __name__ == "__main__":
    generate_video_prompts()
