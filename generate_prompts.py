import json
import os
import random
from datetime import datetime

def detect_animal_type(breed, special_mark=""):
    """
    품종 문자열에서 개/고양이를 판별합니다.
    '[개] 믹스견' 형태뿐 아니라, 코드값만 올 경우 특징 텍스트에서도 유추합니다.
    """
    breed_lower = breed.lower()

    # 1차: 품종 텍스트에서 직접 판별
    dog_keywords = ["개", "견", "dog", "테리어", "리트리버", "셰퍼드", "불독", "푸들", "비글", "말티즈", "시추", "치와와", "진돗", "풍산", "삽살"]
    cat_keywords = ["고양이", "묘", "cat", "페르시안", "러시안", "스코티시", "먼치킨", "벵갈", "샴", "코리안숏헤어", "터키시", "랙돌"]

    for kw in dog_keywords:
        if kw in breed_lower:
            return "dog"
    for kw in cat_keywords:
        if kw in breed_lower:
            return "cat"

    # 2차: 특징 텍스트에서 유추
    if special_mark:
        dog_hints = ["강아지", "개", "짖", "산책", "지켜", "경비", "물지"]
        cat_hints = ["고양이", "묘", "그루밍", "캣", "야옹"]
        for hint in dog_hints:
            if hint in special_mark:
                return "dog"
        for hint in cat_hints:
            if hint in special_mark:
                return "cat"

    # 판별 불가 시 기본값
    return "animal"

def translate_features(color, special_mark):
    """
    한글 색상 및 특징 데이터를 영어 프롬프트 키워드로 변환합니다.
    더 넓은 키워드 매핑으로 다양한 특징을 빠짐없이 반영합니다.
    """
    color_map = {
        "흰색": "white", "검정색": "black", "갈색": "brown", "노란색": "golden yellow",
        "회색": "grey", "검정": "black", "하얀": "white", "노랑": "golden yellow",
        "초코": "chocolate brown", "크림": "cream", "베이지": "beige",
        "황색": "tawny", "적갈색": "reddish brown", "빨강": "reddish",
        "삼색": "tricolor", "얼룩": "spotted", "점박이": "spotted",
        "줄무늬": "striped", "치즈": "orange tabby", "턱시도": "tuxedo pattern"
    }

    keywords = []

    # 색상 반영 (복수 색상 가능)
    for kr, en in color_map.items():
        if kr in color:
            keywords.append(f"{en} fur")

    # 주요 특징 키워드 추출 (확장된 매핑)
    feature_map = {
        # 외형
        "목줄": "wearing a collar",
        "코": "distinctive nose",
        "퐁실": "fluffy fur",
        "곱슬": "curly fur",
        "단모": "short-haired",
        "장모": "long-haired",
        "큰 눈": "large expressive eyes",
        "접힌 귀": "folded ears",
        "쫑긋": "perked-up ears",
        "짧은 꼬리": "short tail",
        "긴 꼬리": "long tail",
        "단미": "docked tail",
        "큰 체구": "large build",
        "작은 체구": "small build",
        "마른": "thin build",
        "통통": "chubby build",
        # 성격 및 행동
        "사람을 좋아": "friendly and people-loving expression",
        "사람을 잘 따": "trusting and affectionate towards people",
        "순함": "gentle expression",
        "순한": "gentle expression",
        "착하": "docile and gentle demeanor",
        "겁이 많": "nervous posture, timid eyes",
        "겁 많": "nervous posture, timid eyes",
        "무서워": "fearful and cautious posture",
        "활발": "energetic movement",
        "해맑": "bright cheerful expression",
        "온순": "calm and mild-mannered",
        "경계": "alert and watchful",
        "지켜": "watchful guardian stance, alert and protective posture",
        "호기심": "curious expression",
        "장난": "playful pose",
        "얌전": "quiet and well-behaved",
        "낯가": "shy around strangers",
        "쉼 없이": "restless movement",
        "귀여": "adorable appearance",
        # 건강/상태
        "건강": "healthy-looking",
        "피부병": "skin condition visible",
        "눈병": "eye condition visible",
        "절뚝": "limping gait",
        "다리를 절": "limping gait",
        "임신": "visibly pregnant",
        "새끼": "with puppies",
        "수술": "surgery scar visible"
    }

    matched_features = []
    for kr, en in feature_map.items():
        if kr in special_mark:
            matched_features.append(en)

    # 매칭된 특징이 없으면 원본 특징 텍스트의 핵심만 간략히 기술
    if not matched_features and special_mark:
        # 기본 폴백: 원본 특징에서 자주 쓰이는 패턴 추출
        fallback_keywords = []
        if any(word in special_mark for word in ["강아지", "개", "견"]):
            fallback_keywords.append("dog-like features")
        if any(word in special_mark for word in ["고양이", "묘", "캣"]):
            fallback_keywords.append("cat-like features")
        fallback_keywords.append("natural appearance with character")
        matched_features = fallback_keywords

    keywords.extend(matched_features)
    return ", ".join(keywords) if keywords else "natural appearance"

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

    # 카메라 구도 무작위성 추가
    camera_angles = [
        "eye-level shot", "low angle shot looking up", "close-up shot", 
        "wide shot showing some cage bars", "side profile shot", "slightly high angle looking down"
    ]
    
    # 환경 디테일 무작위성
    background_details = [
        "dust motes floating in light", "slightly out of focus shelter bars in foreground", 
        "half-eaten food bowl in corner", "reflection on the metal cage surface", 
        "shadows of cage bars cast on floor"
    ]

    # 언캐니 밸리 감소 및 사실감 증대를 위한 원칙
    eye_fx = "natural eye blinking, subtle eye movement, not staring directly into camera, occasional glance away and return"
    fur_fx = "subtle fur movement from breathing, natural coat texture, realistic fur physics, slight movement from inhale exhale"
    camera_fx = "slight handheld camera shake, natural camera movement, slightly imperfect framing, documentary cinematography"
    light_fx = "uneven fluorescent lighting, slight shadows, realistic shelter lighting, imperfect light distribution"
    bg_fx = "worn shelter floor, slightly dirty kennel walls, realistic worn environment, authentic shelter details"
    motion_fx = "short natural movements, abrupt realistic stops and starts, no smooth artificial transitions"
    
    uncanny_reduction = f"{eye_fx}, {fur_fx}, {camera_fx}, {light_fx}, {bg_fx}, {motion_fx}"
    
    # 기본 다큐멘터리 스타일
    base_style = f"unscripted, authentic, no artificial poses, observational documentary style, camera as silent witness, visual storytelling without narration, emotion through observation not manipulation, {uncanny_reduction}"

    # 모든 프롬프트 마지막에 추가될 공통 오디오 및 메타 가이드
    meta_suffix = "slightly imperfect, authentic, this is AI-generated but the animal is real, documentary truth over visual perfection"
    audio_common_suffix = f"no background music, no narration, diegetic sound only, observational documentary style, {meta_suffix}"

    all_prompts_data = []

    for animal in animals:
        animal_id = animal.get("id")
        breed = animal.get("품종", "animal")
        d_day = animal.get("D-day")
        status = animal.get("status", "waiting")
        color = animal.get("색상", "")
        special_mark = animal.get("특징", "")

        # 품종에서 개/고양이 판별 ("[개] 믹스견" 형태 또는 코드값 대응)
        animal_type = detect_animal_type(breed, special_mark)

        # 개별 특징 번역 및 반영
        individual_features = translate_features(color, special_mark)
        
        # D-day별 오디오 디렉션 설정
        audio_direction = ""
        if status == "adopted":
            audio_direction = 'ambient audio: "door opening sound, outside air and traffic faintly, natural light ambience, hopeful quiet, no music"'
        elif status == "euthanized":
            audio_direction = 'audio: "complete silence, no sound"'
        elif d_day == 3:
            audio_direction = 'ambient audio: "animal shelter background sounds, distant dogs barking faintly, fluorescent light hum, occasional kennel door sound, no music, raw documentary feel"'
        elif d_day == 2:
            audio_direction = 'ambient audio: "quiet shelter afternoon, single dog breathing close up, distant footsteps of caretaker, natural room tone, no music"'
        elif d_day == 1:
            audio_direction = 'ambient audio: "very quiet shelter, minimal sound, slow breathing, almost silent, heavy atmosphere, no music"'
        else:
            audio_direction = 'ambient audio: "natural shelter room tone, distant animal sounds"'

        # 3. 진행형 구조 원칙: D-day별 다른 무드 적용
        mood_prompts = []
        
        # 무작위 요소 선택
        rand_angle = random.choice(camera_angles)
        rand_bg = random.choice(background_details)
        
        if status == "adopted":
            # 입양 결말 (가족을 찾은 기쁨)
            mood_header = "🎉 Ending: Found a forever home."
            mood_keywords = f"warm golden hour light, soft focus, {animal_type} wagging tail happily, cinematic resolution, hope, joy"
            mood_prompts = [
                f"A {individual_features} {animal_type} walking towards a bright light, {mood_keywords}, {rand_angle}, {base_style}",
                f"Close-up of {individual_features} {animal_type}'s happy eyes reflecting the sunset, {rand_angle}, {base_style}"
            ]
        elif status == "euthanized":
            # 기간 종료 (기억과 추모)
            mood_header = "🕯️ Ending: Memorial."
            mood_keywords = f"slow motion, black and white, subtle grain, {animal_type} fading into white background, peaceful, eternal silence"
            mood_prompts = [
                f"A {individual_features} {animal_type} sitting still as the screen slowly fades to white, {mood_keywords}, {rand_angle}, {base_style}",
                f"Empty cage floor where the {individual_features} {animal_type} used to be, emotional stillness, {base_style}"
            ]
        elif d_day == 3:
            # D-3: 처음 만남의 낯섦
            mood_header = "D-3: The Strange First Encounter."
            visual_contrast = "first frame resembles actual shelter documentation photo, cold clinical record aesthetic, then transition to warmer observational documentary style, intentional visual contrast, cold documentary record transitioning to living breathing presence, handheld shaky cam"
            mood_prompts = [
                f"A {individual_features} {animal_type} nervously sniffing the air in a cold shelter, {visual_contrast}, {rand_angle}, {rand_bg}, {base_style}",
                f"Extreme close-up of a {individual_features} {animal_type}'s eye reflecting a blue digital record screen, {rand_angle}, {base_style}",
                f"A {individual_features} {animal_type} huddling in the corner of a dimly lit cage, raw documentary footage, {rand_angle}, {base_style}"
            ]
        elif d_day == 2:
            # D-2: 관계가 생긴 하루
            mood_header = "D-2: A Day of Connection."
            connection_style = "shallow depth of field, focus on the animal's interaction with the camera person, natural morning light"
            mood_prompts = [
                f"A {individual_features} {animal_type} slowly approaching the camera, hesitant but curious, {connection_style}, {rand_angle}, {rand_bg}, {base_style}",
                f"A {individual_features} {animal_type} blinking slowly while looking into the lens, establishing eye contact, {rand_angle}, {base_style}",
                f"Close-up of a {individual_features} {animal_type} resting its chin on the cold floor, looking sadly but trustingly, {rand_angle}, {base_style}"
            ]
        elif d_day == 1:
            # D-1: 시간이 멈추는 느낌
            mood_header = "D-1: The Moment Time Stops."
            urgency_style = "high contrast lighting, long shadow, silence, extreme close-up of breath, frozen in time"
            mood_prompts = [
                f"A shot of a {individual_features} {animal_type} sitting under a single shaft of light, motionless as if time stopped, {urgency_style}, {rand_angle}, {rand_bg}, {base_style}",
                f"The ticking clock sound visualization through the {individual_features} {animal_type}'s heavy breathing, extreme close-up, {rand_angle}, {base_style}",
                f"A {individual_features} {animal_type} staring into infinity beyond the cage bars, sunset shadows elongating, {rand_angle}, {base_style}"
            ]
        else:
            mood_header = "Normal: Waiting for a miracle."
            mood_prompts = [
                f"A {individual_features} {animal_type} looking through the shelter bars, soft documentary lighting, {rand_angle}, {rand_bg}, {base_style}",
                f"A {individual_features} {animal_type} sitting quietly in its own world, cinematic observational shot, {rand_angle}, {base_style}"
            ]

        # 모든 프롬프트에 오디오 디렉션 및 공통 접미사 결합
        final_prompts = [f"{p}, {audio_direction}, {audio_common_suffix}" for p in mood_prompts]

        animal_data = {
            "animal_id": animal_id,
            "D-day": d_day,
            "breed": breed,
            "status": status,
            "mood_theme": mood_header,
            "총_생성된_프롬프트_수": len(final_prompts),
            "prompts": final_prompts
        }
        all_prompts_data.append(animal_data)

    # 결과 저장
    with open(output_file, "w", encoding="utf-8") as json_file:
        json.dump(all_prompts_data, json_file, ensure_ascii=False, indent=4)

    print("================================")
    print(f"[{datetime.now().strftime('%H:%M')}] generate_prompts.py 실행 (고유화 반영)")
    print("================================")
    print(f"- 생성된 프롬프트 수: {len(animals)}마리")
    if all_prompts_data:
        print("- 동물별 특징 반영 프롬프트 예시:")
        for data in all_prompts_data:
            example = data["prompts"][0][:120] + "..." if data["prompts"] else "없음"
            print(f"  * {data['animal_id']}: {example}")
    print("")

if __name__ == "__main__":
    generate_video_prompts()
