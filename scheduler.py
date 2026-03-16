import schedule
import time
import subprocess
import os
from datetime import datetime

# 로그 디렉토리 설정
LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)

def get_log_file():
    """오늘 날짜의 로그 파일 경로를 반환합니다."""
    today = datetime.now().strftime("%Y-%m-%d")
    return os.path.join(LOG_DIR, f"{today}.log")

def log(message):
    """메시지를 콘솔에 출력하고 로그 파일에 기록합니다."""
    timestamp = datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
    log_msg = f"{timestamp} {message}"
    print(log_msg)
    with open(get_log_file(), "a", encoding="utf-8") as f:
        f.write(log_msg + "\n")

def run_script(script_name):
    """지정한 파이썬 스크립트를 실행합니다."""
    log(f"--- 스텝 시작: {script_name} ---")
    try:
        # subprocess.run을 사용하여 스크립트 실행
        # capture_output=True로 설정하여 출력 내용을 로그에 담을 수 있음
        result = subprocess.run(["python", script_name], capture_output=True, text=True, encoding="utf-8")
        
        if result.returncode == 0:
            log(f"성공: {script_name} 실행 완료")
            return True
        else:
            log(f"실패: {script_name} 실행 중 오류 발생 (종료 코드: {result.returncode})")
            log(f"에러 내용:\n{result.stderr}")
            return False
    except Exception as e:
        log(f"예외 발생: {script_name} 실행 불가 - {e}")
        return False

def job():
    """전체 파이프라인을 순차적으로 실행하는 메인 작업입니다."""
    pipeline = [
        "fetch_animals.py",
        "generate_prompts.py",
        "generate_thumbnail.py",
        "generate_metadata.py",
        "generate_videos.py",
        "add_subtitles.py",
        "upload_youtube.py"
    ]
    
    log("=== [전체 파이프라인 자동 실행 시작] ===")
    
    for script in pipeline:
        success = run_script(script)
        if not success:
            log(f"!!! 파이프라인 중단됨: {script} 단계에서 오류 발생 !!!")
            break
    else:
        log("=== [전체 파이프라인 성공적으로 완료됨] ===")

# 매일 오전 09:00에 실행 예약
schedule.every().day.at("09:00").do(job)

if __name__ == "__main__":
    log("파이프라인 스케줄러 시작. 매일 09:00에 실행됩니다.")
    
    # 시작 시 테스트를 위해 즉시 실행하고 싶다면 아래 주석을 해제하세요
    # job()
    
    try:
        while True:
            schedule.run_pending()
            time.sleep(60) # 1분마다 작업 확인
    except KeyboardInterrupt:
        log("스케줄러가 사용자에 의해 중단되었습니다.")
