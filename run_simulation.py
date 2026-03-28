import subprocess
import os
import time
import sys
from datetime import datetime

# 윈도우 터미널(CP949)에서도 UTF-8 출력을 안전하게 하기 위해 설정
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def log_section(title):
    print("\n" + "="*50)
    print(f" {title} ")
    print("="*50)

def run_script(script_name):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {script_name} 실행 중...")
    # 윈도우 환경의 cp949/utf-8 혼용 문제를 방지하기 위해 errors='replace' 사용
    result = subprocess.run(["python", script_name], capture_output=True, text=True, encoding="utf-8", errors="replace")
    print(result.stdout)
    if result.stderr:
        print(f"로그 (stderr):\n{result.stderr}")
    return result.returncode == 0

def run_simulation():
    start_time = time.time()
    
    # 실행할 스크립트 순서 (시뮬레이션 버전 포함)
    pipeline = [
        ("동물 데이터 수집", "fetch_animals.py"),
        ("프롬프트 생성", "generate_prompts.py"),
        ("썸네일 생성", "generate_thumbnail.py"),
        ("메타데이터 생성", "generate_metadata.py"),
        ("영상 생성 (시뮬레이션)", "generate_videos_sim.py"),
        ("자막 합성", "add_subtitles.py"),
        ("유튜브 업로드 (시뮬레이션)", "upload_youtube_sim.py")
    ]

    total_steps = len(pipeline)
    success_steps = 0

    log_section("유기동물 자동화 파이프라인 시뮬레이션 시작")

    for i, (name, script) in enumerate(pipeline, 1):
        log_section(f"단계 {i}/{total_steps}: {name}")
        if run_script(script):
            success_steps += 1
        else:
            print(f"!!! {name} 단계에서 오류가 발생했습니다. 시뮬레이션을 중단합니다. !!!")
            break

    # 요약 출력
    duration = time.time() - start_time
    
    # 처리된 동물 수 확인 (videos.json 기준)
    try:
        import json
        with open("videos.json", "r", encoding="utf-8") as f:
            processed_count = len(json.load(f))
    except:
        processed_count = 0

    log_section("시뮬레이션 결과 요약")
    print(f"전체 소요 시간: {duration:.2f}초")
    print(f"완료된 단계: {success_steps}/{total_steps}")
    print(f"오늘 처리된 동물 수: {processed_count}마리")
    print("상태: " + ("성공" if success_steps == total_steps else "실패"))
    print("="*50)

if __name__ == "__main__":
    run_simulation()
