import os
import json
import requests
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont, ImageEnhance

def generate_thumbnails():
    # 경로 설정
    animals_file = "animals.json"
    videos_file = "videos.json"
    output_dir = "thumbnails"
    os.makedirs(output_dir, exist_ok=True)

    # 데이터 로드
    if not os.path.exists(videos_file):
        print("videos.json 파일이 없습니다. 영상 생성을 먼저 진행해주세요.")
        return

    with open(videos_file, "r", encoding="utf-8") as f:
        videos_data = json.load(f)
        
    if not os.path.exists(animals_file):
        print("animals.json 파일이 없습니다.")
        return
        
    with open(animals_file, "r", encoding="utf-8") as f:
        animals_data = {a["id"]: a for a in json.load(f)}

    if not videos_data:
        print("썸네일을 생성할 영상 데이터가 없습니다.")
        return

    print(f"총 {len(videos_data)}개의 썸네일 생성을 시작합니다...")

    # 폰트 설정 (Windows 기준 맑은 고딕 사용 가능성 높음)
    # 시스템에 따라 폰트 파일 경로 직접 지정이 필요할 수 있습니다.
    try:
        # 큰 폰트 (D-day용)
        font_large = ImageFont.truetype("malgun.ttf", 120)
        # 작은 폰트 (품종용)
        font_small = ImageFont.truetype("malgun.ttf", 40)
    except:
        # 폰트 로드 실패 시 기본 폰트 사용 (한글 깨질 수 있음)
        font_large = ImageFont.load_default()
        font_small = ImageFont.load_default()
        print("경고: 'malgun.ttf' 폰트를 찾을 수 없어 기본 폰트를 사용합니다. 한글이 깨질 수 있습니다.")

    for video in videos_data:
        animal_id = video.get("animal_id")
        # videos.json에 정보가 부족하면 animals.json에서 가져옴
        animal_info = animals_data.get(animal_id, {})
        
        img_url = video.get("사진URL") or animal_info.get("사진URL")
        breed = video.get("breed") or animal_info.get("품종", "유기동물")
        d_day = video.get("D-day") or animal_info.get("D-day", "?")
        
        if not img_url:
            print(f"[{animal_id}] 사진 URL이 없어 썸네일을 생성할 수 없습니다.")
            continue

        try:
            # 1. 이미지 다운로드
            response = requests.get(img_url)
            img = Image.open(BytesIO(response.content))
            
            # 2. 해상도 조정 (1280x720) - 비율 유지하며 자르기
            target_ratio = 1280 / 720
            img_ratio = img.width / img.height
            
            if img_ratio > target_ratio:
                # 가로가 더 김 -> 세로에 맞춰 자름
                new_width = int(target_ratio * img.height)
                left = (img.width - new_width) / 2
                img = img.crop((left, 0, left + new_width, img.height))
            else:
                # 세로가 더 김 -> 가로에 맞춰 자름
                new_height = int(img.width / target_ratio)
                top = (img.height - new_height) / 2
                img = img.crop((0, top, img.width, top + new_height))
                
            img = img.resize((1280, 720), Image.Resampling.LANCZOS)
            
            # 3. 전체적으로 어둡게 필터 적용 (밝기 60%)
            enhancer = ImageEnhance.Brightness(img)
            img = enhancer.enhance(0.6)
            
            # 4. 텍스트 합성
            draw = ImageDraw.Draw(img)
            
            # D-day 텍스트 (화면 하단 중앙)
            dday_text = f"D-{d_day}"
            # 텍스트 크기 계산 (Pillow 버전에 따라 다름)
            try:
                # Pillow 10.0.0+
                left, top, right, bottom = draw.textbbox((0, 0), dday_text, font=font_large)
                text_width = right - left
                text_height = bottom - top
            except:
                text_width, text_height = draw.textsize(dday_text, font=font_large)
            
            # 하단에서 100픽셀 위
            x_dday = (1280 - text_width) / 2
            y_dday = 720 - text_height - 100
            
            # 그림자 효과 (약간의 오프셋으로 검은색 텍스트 먼저 쓰기)
            draw.text((x_dday+3, y_dday+3), dday_text, font=font_large, fill="black")
            draw.text((x_dday, y_dday), dday_text, font=font_large, fill="white")
            
            # 품종 텍스트 (좌하단)
            try:
                left, top, right, bottom = draw.textbbox((0, 0), breed, font=font_small)
                b_width = right - left
                b_height = bottom - top
            except:
                b_width, b_height = draw.textsize(breed, font=font_small)
                
            x_breed = 50
            y_breed = 720 - b_height - 50
            
            draw.text((x_breed+2, y_breed+2), breed, font=font_small, fill="black")
            draw.text((x_breed, y_breed), breed, font=font_small, fill="white")
            
            # 5. 저장
            output_path = os.path.join(output_dir, f"{animal_id}_{d_day}.jpg")
            img.save(output_path, "JPEG", quality=90)
            
        except Exception as e:
            print(f"[{animal_id}] 썸네일 생성 중 오류: {e}")

    print("================================")
    print(f"[09:03] generate_thumbnail.py 실행")
    print("================================")
    print(f"- 생성된 썸네일 수: {len(videos_data)}개")
    if videos_data:
        print("- 저장 경로 목록:")
        for v in videos_data:
            aid = v.get("animal_id")
            dd = v.get("D-day")
            path = os.path.join(output_dir, f"{aid}_{dd}.jpg")
            print(f"  * {path}")
    print("")

if __name__ == "__main__":
    generate_thumbnails()
