import json
import os
from datetime import datetime

def generate_metadata():
    input_file = "animals.json"
    output_file = "metadata.json"

    if not os.path.exists(input_file):
        print(f"에러: '{input_file}' 파일이 없습니다.")
        return

    with open(input_file, "r", encoding="utf-8") as f:
        animals = json.load(f)

    metadata_result = {}

    for animal in animals:
        animal_id = animal.get("id")
        breed = animal.get("품종", "유기동물")
        location_full = animal.get("보호소위치", "알 수 없음")
        # 지역명 추출 (첫 번째 단어, 주로 도/시 단위)
        region = location_full.split()[0] if location_full != "알 수 없음" else "전국"
        age = animal.get("나이", "알 수 없음")
        sex = "암컷" if animal.get("성별") == "F" else "수컷" if animal.get("성별") == "M" else "미상"
        end_date = animal.get("보호종료일", "알 수 없음")
        
        # 품종명 정제 ( [개] 믹스견 -> 믹스견 )
        breed_clean = breed.replace("[개] ", "").replace("[고양이] ", "").replace("[기타] ", "")
        
        # 태그 리스트 생성
        base_tags = ["유기견", "유기묘", "입양", "보호소", "동물보호", "stray dog", "animal rescue", "adoption", "D-day", "보호기간"]
        tags = base_tags + [breed_clean, region]
        tags_str = ", ".join(list(set(tags))) # 중복 제거 및 콤마 구분

        # 시나리오별 메타데이터 세트
        scenarios = {
            "D-3": {
                "title": f"[{breed_clean}] {breed_clean}에게 3일이 남았습니다",
                "description_header": "🚨 공공보호소 긴급 공고: 안락사까지 3일 남았습니다."
            },
            "D-2": {
                "title": f"내일 모레가 마지막입니다 | {breed_clean} {region}",
                "description_header": "⚠️ 내일 모레면 이 아이를 다시 볼 수 없을지도 모릅니다."
            },
            "D-1": {
                "title": f"내일입니다 | {breed_clean}",
                "description_header": "⏳ 마지막 24시간. 기적이 필요합니다."
            },
            "입양결말": {
                "title": f"가족을 찾았습니다 🐾 | {breed_clean}",
                "description_header": "🎉 행복한 소식! 드디어 평생 가족을 만났습니다."
            },
            "안락사결말": {
                "title": f"{breed_clean} | {end_date}",
                "description_header": f"🕯️ {breed_clean} 아이가 하늘의 별이 되었습니다. 기억해주세요."
            }
        }

        animal_metadata = {}
        
        for key, value in scenarios.items():
            # 설명 구성
            description = f"""{value['description_header']}

🐾 동물 정보
- 품종: {breed}
- 나이: {age}
- 성별: {sex}
- 지역: {region}
- 보호소: {location_full}
- 보호 종료일: {end_date}

이 아이의 이야기는 국가동물보호정보시스템 실제 데이터를 기반으로 합니다.
입양 문의는 해당 보호소로 직접 부탁드립니다. 

{tags_str}

#유기동물 #사지말고입양하세요 #공공보호소 #입양공고 #shorts"""

            animal_metadata[key] = {
                "title": value["title"],
                "description": description,
                "tags": tags
            }

        metadata_result[animal_id] = animal_metadata

    # 결과 저장
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(metadata_result, f, ensure_ascii=False, indent=4)

    print(f"성공: {len(animals)}마리의 동물에 대한 메타데이터가 '{output_file}'에 저장되었습니다.")

if __name__ == "__main__":
    generate_metadata()
