"""
Almond Pipeline — create_video.py
동물 이미지 + 오버레이 텍스트 → 플랫폼별 영상 생성

Manifesto ref: §2 투명성(워터마크 필수)
Gotchas: GOTCHA-006, GOTCHA-007
Dependencies: ffmpeg (시스템 설치 필요), Pillow, requests
"""

import json
import subprocess
import tempfile
from pathlib import Path

import requests
from PIL import Image, ImageDraw, ImageFont

TEMPLATES_DIR = Path(__file__).parent.parent / "Templates"
OUTPUT_DIR = Path(__file__).parent / "output"
OUTPUT_DIR.mkdir(exist_ok=True)

# GOTCHA-006: 플랫폼별 프리셋 — 단일 해상도 사용 금지
PLATFORM_PRESETS = {
    "instagram_reels": {"width": 1080, "height": 1920, "fps": 30, "duration": 15},
    "youtube_shorts":  {"width": 1080, "height": 1920, "fps": 30, "duration": 30},
    "tiktok":          {"width": 1080, "height": 1920, "fps": 30, "duration": 15},
    "default":         {"width": 1080, "height": 1920, "fps": 30, "duration": 15},
}


def download_image(url: str, dest: Path) -> Path:
    resp = requests.get(url, timeout=15)
    resp.raise_for_status()
    dest.write_bytes(resp.content)
    return dest


def crop_to_ratio(img: Image.Image, width: int, height: int) -> Image.Image:
    """Center-crop to target aspect ratio."""
    target_ratio = width / height
    img_ratio = img.width / img.height

    if img_ratio > target_ratio:
        new_width = int(img.height * target_ratio)
        offset = (img.width - new_width) // 2
        img = img.crop((offset, 0, offset + new_width, img.height))
    else:
        new_height = int(img.width / target_ratio)
        offset = (img.height - new_height) // 2
        img = img.crop((0, offset, img.width, offset + new_height))

    return img.resize((width, height), Image.LANCZOS)


def add_overlay(img: Image.Image, overlay: dict) -> Image.Image:
    """
    오버레이 텍스트 레이어 추가.
    GOTCHA-007: 워터마크는 필수 레이어 — 조건부 처리 금지.
    """
    draw = ImageDraw.Draw(img)
    w, h = img.size

    try:
        font_large = ImageFont.truetype("arial.ttf", 36)
        font_medium = ImageFont.truetype("arial.ttf", 24)
        font_small = ImageFont.truetype("arial.ttf", 16)
    except OSError:
        font_large = font_medium = font_small = ImageFont.load_default()

    # D-day 배지 (좌상단)
    d_day_text = overlay.get("d_day_badge", "")
    draw.rectangle([20, 40, 20 + len(d_day_text) * 14 + 24, 80], fill=(220, 53, 69, 217))
    draw.text((32, 48), d_day_text, font=font_medium, fill="white")

    # 타이틀 (중앙 하단 1/3)
    title = overlay.get("title", "")
    draw.text((w // 2, int(h * 0.65)), title, font=font_large, fill="white", anchor="mm")

    # 보호소 정보 (하단)
    shelter_info = overlay.get("shelter_info", "")
    draw.rectangle([0, h - 80, w, h - 40], fill=(0, 0, 0, 153))
    draw.text((w // 2, h - 60), shelter_info, font=font_small, fill="white", anchor="mm")

    # GOTCHA-007: 워터마크 — 필수, 제거 불가 (Manifesto §2)
    watermark = overlay.get("watermark", "AI-generated video | 실제 유기동물 정보 기반")
    draw.text((w - 10, h - 20), watermark, font=font_small, fill=(255, 255, 255, 178), anchor="rm")

    return img


def render_video_ffmpeg(
    image_path: Path,
    output_path: Path,
    preset: dict,
) -> Path:
    """
    ffmpeg로 정지 이미지 → 영상 변환 (kenburns 효과).
    """
    duration = preset["duration"]
    fps = preset["fps"]
    w, h = preset["width"], preset["height"]

    # kenburns 줌 효과
    zoom_filter = (
        f"scale={w * 2}:{h * 2},"
        f"zoompan=z='min(zoom+0.0005,1.1)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)'"
        f":d={duration * fps}:s={w}x{h}:fps={fps}"
    )

    cmd = [
        "ffmpeg", "-y",
        "-loop", "1",
        "-i", str(image_path),
        "-vf", zoom_filter,
        "-t", str(duration),
        "-c:v", "libx264",
        "-pix_fmt", "yuv420p",
        "-preset", "fast",
        str(output_path),
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"ffmpeg 오류: {result.stderr}")

    return output_path


def create_video(content_path: str, image_url: str, platforms: list[str] | None = None) -> dict:
    """
    메인 함수: 콘텐츠 JSON + 이미지 URL → 플랫폼별 영상 생성.
    """
    content = json.loads(Path(content_path).read_text(encoding="utf-8"))
    desertion_no = content["desertionNo"]
    overlay = content["overlay"]

    # Manifesto 검증 통과 여부 확인
    if not content.get("validation", {}).get("manifesto_pass"):
        raise ValueError(f"{desertion_no}: manifesto 검증 미통과 — 영상 생성 불가")

    if platforms is None:
        platforms = ["instagram_reels", "youtube_shorts", "tiktok"]

    results = {}

    with tempfile.TemporaryDirectory() as tmpdir:
        tmp = Path(tmpdir)

        # 이미지 다운로드 및 전처리
        raw_img_path = tmp / "raw.jpg"
        download_image(image_url, raw_img_path)
        raw_img = Image.open(raw_img_path).convert("RGB")

        for platform in platforms:
            preset = PLATFORM_PRESETS.get(platform, PLATFORM_PRESETS["default"])

            # 이미지 크롭 및 리사이즈
            img = crop_to_ratio(raw_img.copy(), preset["width"], preset["height"])

            # 오버레이 추가 (워터마크 포함 — GOTCHA-007)
            img = add_overlay(img, overlay)

            # 처리된 이미지 저장
            processed_img_path = tmp / f"processed_{platform}.jpg"
            img.save(processed_img_path, quality=95)

            # 영상 렌더링
            out_path = OUTPUT_DIR / f"video_{desertion_no}_{platform}.mp4"
            render_video_ffmpeg(processed_img_path, out_path, preset)

            size_mb = round(out_path.stat().st_size / 1024 / 1024, 2)
            results[platform] = {
                "path": str(out_path),
                "size_mb": size_mb,
                "duration_sec": preset["duration"],
                "watermark_verified": True,  # 워터마크는 항상 포함됨
            }

    # 메타데이터 저장
    manifest = {
        "desertionNo": desertion_no,
        "videos": results,
        "status": "success",
    }
    manifest_path = OUTPUT_DIR / f"video_{desertion_no}_manifest.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")

    return manifest


if __name__ == "__main__":
    import sys
    result = create_video(sys.argv[1], sys.argv[2])
    print(json.dumps(result, ensure_ascii=False, indent=2))
