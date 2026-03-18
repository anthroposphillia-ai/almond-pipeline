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
    # 단계별 짧은 가이드라인 매핑
    guidelines = {
        "track_animals.py": "[생존 확인] 한 명의 생명이라도 놓치지 않고 끝까지 추적합니다.",
        "fetch_animals.py": "[데이터 수집] 사실만을 담습니다. 있는 그대로의 정보를 가져옵니다.",
        "generate_prompts.py": "[AI 프롬프트] 과장하지 않습니다. 동물들 본연의 모습을 담아냅니다.",
        "generate_thumbnail.py": "[이미지 제작] 불쌍함을 팔지 않습니다. 동물의 기한을 명확히 알립니다.",
        "generate_metadata.py": "[메타데이터] 시청자의 마음을 두드리되 공유를 강요하지 않습니다.",
        "generate_videos.py": "[영상 생성] 플랫폼이 지속 가능하도록, 매일 새로운 동물들을 알립니다.",
        "add_subtitles.py": "[자막 합성] 긴급성을 부풀리지 않고, 사실에 기반한 정보를 알립니다.",
        "upload_youtube.py": "[유튜브 업로드] 돈과 명성보다 동물들의 생명이 최우선입니다."
    }

    log(f"--- 스텝 시작: {script_name} ---")
    if script_name in guidelines:
        log(f"💡 원칙 확인: {guidelines[script_name]}")
        time.sleep(1) # 짧은 성찰의 시간

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
    
    # 선언문 출력
    log("\n=== 오늘도 시작합니다 ===")
    manifesto_path = "manifesto.txt"
    if os.path.exists(manifesto_path):
        with open(manifesto_path, "r", encoding="utf-8") as f:
            print(f.read())
        time.sleep(3) # 3초 대기
    
    pipeline = [
        "track_animals.py",
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

# 매일 오전 08:50에 상태 추적 실행
schedule.every().day.at("08:50").do(lambda: run_script("track_animals.py"))

# 매일 오전 09:00에 전체 파이프라인 실행 예약
schedule.every().day.at("09:00").do(job)

# 매월 1일 오전 09:05에 월간 통계 요약 게시 (Step 1046)
def run_monthly_summary():
    if datetime.now().day == 1:
        run_script("post_monthly_summary.py")

schedule.every().day.at("09:05").do(run_monthly_summary)

if __name__ == "__main__":
    log("파이프라인 스케줄러 시작. 매일 08:50(상태 체크) 및 09:00(전체 실행)에 작동합니다.")
    
    # 시작 시 테스트를 위해 즉시 실행하고 싶다면 아래 주석을 해제하세요
    # job()
    
    try:
        while True:
            schedule.run_pending()
            time.sleep(60) # 1분마다 작업 확인
    except KeyboardInterrupt:
        log("스케줄러가 사용자에 의해 중단되었습니다.")
