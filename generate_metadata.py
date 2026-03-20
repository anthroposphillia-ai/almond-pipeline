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
    used_titles = {} # 중복 제목 추적을 위한 딕셔너리

    for animal in animals:
        animal_id = animal.get("id")
        breed = animal.get("품종", "유기동물")
        location_full = animal.get("보호소주소", "알 수 없음")
        region = location_full.split()[0] if location_full != "알 수 없음" else "전국"
        care_nm = animal.get("보호소명", region)
        care_tel = animal.get("보호소전화번호", "")
        age = animal.get("나이", "알 수 없음")
        sex = "암컷" if animal.get("성별") == "F" else "수컷" if animal.get("성별") == "M" else "미상"
        end_date = animal.get("보호종료일", "알 수 없음")
        d_day = animal.get("D-day")
        special_mark = animal.get("특징", "")
        
        # 품종명 정제
        breed_clean = breed.replace("[개] ", "").replace("[고양이] ", "").replace("[기타] ", "")
        
        # 용어 정제
        if "[개]" in breed:
            subject_name = "이 강아지"
        elif "[고양이]" in breed:
            subject_name = "이 고양이"
        else:
            subject_name = f"이 {breed_clean}"

        # 제목 보조 정보 (특징 또는 보호소-Issue 1)
        sub_info = ""
        if special_mark:
            # 첫 번째 단어 추출 (공백이나 쉼표 기준)
            import re
            words = re.split(r'[ ,]', special_mark)
            sub_info = words[0] if words[0] else ""
        
        # 태그
        base_tags = ["유기견", "유기묘", "입양", "보호소", "동물보호", "stray dog", "animal rescue", "adoption", "D-day", "보호기간"]
        tags = list(set(base_tags + [breed_clean, region, care_nm]))
        tags_str = ", ".join(tags)

        animal_metadata = {}
        
        # 시나리오 정의
        scenarios = {
            "D-3": {"title_base": f"[{breed_clean}] {subject_name}에게 3일이 남았습니다"},
            "D-2": {"title_base": f"내일 모레가 마지막입니다 | {breed_clean} {region}"},
            "D-1": {"title_base": f"내일입니다 | {breed_clean}"},
            "입양결말": {"title_base": f"가족을 찾았습니다 🐾 | {breed_clean}"},
            "안락사결말": {"title_base": f"{breed_clean} | {end_date}"}
        }

        for key, val in scenarios.items():
            # 중복 방지 제목 생성
            final_title = val["title_base"]
            if sub_info:
                # 특징 추가 (방법 2)
                if "|" in final_title:
                    parts = final_title.split("|")
                    final_title = f"{parts[0]}| {sub_info} {parts[1].strip()}"
                else:
                    final_title = f"{final_title} ({sub_info})"
            
            # 보호소 및 중복 순번 체크 (방법 1)
            base_key = f"{key}_{final_title}"
            if base_key in used_titles:
                used_titles[base_key] += 1
                final_title = f"{final_title} | {care_nm} #{used_titles[base_key]}"
            else:
                used_titles[base_key] = 1

            elapsed_days = 10 - d_day if isinstance(d_day, int) else "알 수 없음"
            
            # 문의처 정보 (Issue 3)
            contact_info = f"{care_nm} {care_tel}".strip() or location_full

            description = f"""본 콘텐츠는 국가동물보호정보시스템 공공데이터를 기반으로 제작됩니다.

{subject_name}는 {region} 보호소에 있습니다.
보호기간은 10일입니다. 오늘은 {elapsed_days}일째입니다.

품종: {breed}
나이: {age}
성별: {sex}
보호소: {location_full}
보호 종료일: {end_date}

이 영상은 국가동물보호정보시스템 실제 데이터를 기반으로 AI가 제작했습니다.
{subject_name}는 진짜입니다.

D-3 영상부터 보시려면 → (재생목록 링크 준비중)
입양 문의 → {contact_info} (문의 시 공고번호 {animal_id}를 말씀해주세요)

매일 새로운 강아지와 고양이들이 보호소에 들어옵니다.
보호기간은 10일입니다.
그래서 매일 올립니다.
우리가 빠른 게 아닙니다. 시간이 없는 겁니다.

---
{tags_str}

#유기동물 #사지말고입양하세요 #공공보호소 #입양공고 #shorts"""

            animal_metadata[key] = {
                "title": final_title,
                "description": description,
                "tags": tags
            }

        metadata_result[animal_id] = animal_metadata

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(metadata_result, f, ensure_ascii=False, indent=4)

    print("================================")
    print(f"[09:04] generate_metadata.py 실행")
    print("================================")
    if metadata_result:
        print("- 각 동물별 제목:")
        for aid, meta in metadata_result.items():
            d_key = "D-1" if "D-1" in meta else ("D-2" if "D-2" in meta else "D-3")
            print(f"  * {aid}: {meta.get(d_key, {}).get('title', 'N/A')}")
        
        first_aid = list(metadata_result.keys())[0]
        first_dkey = list(metadata_result[first_aid].keys())[0]
        print(f"\n- 설명란 예시 (ID: {first_aid}):")
        print("--------------------------------")
        print(metadata_result[first_aid][first_dkey]["description"])
        print("--------------------------------")
    print("")

if __name__ == "__main__":
    generate_metadata()
