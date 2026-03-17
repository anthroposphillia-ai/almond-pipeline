import json
import os

def generate_video_prompts():
    # 저장된 동물의 정보를 불러옵니다.
    input_file = "animals.json"
    output_file = "prompts.json"
    
    if not os.path.exists(input_file):
        print(f"에러: '{input_file}' 파일이 없습니다. 먼저 fetch_animals.py를 통해 데이터를 수집해 주세요.")
        return

    with open(input_file, "r", encoding="utf-8") as f:
        animals = json.load(f)

    if not animals:
        print("동물 데이터가 비어 있습니다.")
        return

    # 김옥영 다큐멘터리 원칙 기반 프롬프트 엔진
    # 1. 현실 원칙: unscripted, authentic, no artificial poses
    # 2. 관찰자 원칙: observational documentary style, camera as silent witness
    # 3. 설득 원칙: visual storytelling without narration, emotion through observation not manipulation
    base_style = "unscripted, authentic, no artificial poses, observational documentary style, camera as silent witness, visual storytelling without narration, emotion through observation not manipulation"

    all_prompts_data = []

    for animal in animals:
        animal_id = animal.get("id")
        breed = animal.get("품종", "animal")
        d_day = animal.get("D-day")
        status = animal.get("status", "waiting")
        
        animal_type = "dog" if "개" in breed else ("cat" if "고양이" in breed else "animal")
        breed_clean = breed.replace("[개] ", "").replace("[고양이] ", "").replace("[기타] ", "")

        # 3. 진행형 구조 원칙: D-day별 다른 무드 적용
        # 2. 시각 원칙: 차가운 데이터 vs 살아있는 존재의 대비
        mood_prompts = []
        
        if status == "adopted":
            # 입양 결말 (가족을 찾은 기쁨)
            mood_header = "🎉 Ending: Found a forever home."
            mood_keywords = f"warm golden hour light, soft focus, {animal_type} wagging tail happily, cinematic resolution, hope, joy"
            mood_prompts = [
                f"A {animal_type} walking towards a bright light, {mood_keywords}, {base_style}",
                f"Close-up of {animal_type}'s happy eyes reflecting the sunset, {mood_keywords}, {base_style}"
            ]
        elif status == "euthanized":
            # 기간 종료 (기억과 추모)
            mood_header = "🕯️ Ending: Memorial."
            mood_keywords = f"slow motion, black and white, subtle grain, {animal_type} fading into white background, peaceful, eternal silence"
            mood_prompts = [
                f"A {animal_type} sitting still as the screen slowly fades to white, {mood_keywords}, {base_style}",
                f"Empty cage floor where the {animal_type} used to be, emotional stillness, {mood_keywords}, {base_style}"
            ]
        elif d_day == 3:
            # D-3: 처음 만남의 낯섦 (시각 원칙: 데이터 vs 생명)
            mood_header = "D-3: The Strange First Encounter."
            visual_contrast = "contrast between cold metal cage bars and the warmth of a living breathing creature, handheld shaky cam"
            mood_prompts = [
                f"A {animal_type} nervously sniffing the air in a cold shelter, {visual_contrast}, {base_style}",
                f"Extreme close-up of a {animal_type}'s eye reflecting a blue digital record screen, {visual_contrast}, {base_style}",
                f"A {animal_type} huddling in the corner of a dimly lit cage, raw documentary footage, {base_style}"
            ]
        elif d_day == 2:
            # D-2: 관계가 생긴 하루 (유대감)
            mood_header = "D-2: A Day of Connection."
            connection_style = "shallow depth of field, focus on the animal's interaction with the camera person, natural morning light"
            mood_prompts = [
                f"A {animal_type} slowly approaching the camera, hesitant but curious, {connection_style}, {base_style}",
                f"A {animal_type} blinking slowly while looking into the lens, establishing eye contact, {connection_style}, {base_style}",
                f"Close-up of a {animal_type} resting its chin on the cold floor, looking sadly but trustingly, {base_style}"
            ]
        elif d_day == 1:
            # D-1: 시간이 멈추는 느낌 (긴박함과 정적)
            mood_header = "D-1: The Moment Time Stops."
            urgency_style = "high contrast lighting, long shadow, silence, extreme close-up of breath, frozen in time"
            mood_prompts = [
                f"A shot of a {animal_type} sitting under a single shaft of light, motionless as if time stopped, {urgency_style}, {base_style}",
                f"The ticking clock sound visualization through the {animal_type}'s heavy breathing, extreme close-up, {urgency_style}, {base_style}",
                f"A {animal_type} staring into infinity beyond the cage bars, sunset shadows elongating, {base_style}"
            ]
        else:
            # 기타 (일반 보호 중)
            mood_header = "Normal: Waiting for a miracle."
            mood_prompts = [
                f"A {animal_type} looking through the shelter bars, soft documentary lighting, {base_style}",
                f"A {animal_type} sitting quietly in its own world, cinematic observational shot, {base_style}"
            ]

        animal_data = {
            "animal_id": animal_id,
            "D-day": d_day,
            "breed": breed,
            "status": status,
            "mood_theme": mood_header,
            "총_생성된_프롬프트_수": len(mood_prompts),
            "prompts": mood_prompts
        }
        all_prompts_data.append(animal_data)

    # 결과를 prompts.json 파일로 저장합니다.
    with open(output_file, "w", encoding="utf-8") as json_file:
        json.dump(all_prompts_data, json_file, ensure_ascii=False, indent=4)

    print(f"\n[다큐멘터리 원칙 적용 완료] {len(animals)}마리에 대한 고도화된 프롬프트를 생성했습니다.")
    print(f"결과는 '{output_file}' 파일에 저장되었습니다.")

if __name__ == "__main__":
    generate_video_prompts()
