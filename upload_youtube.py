import os
import json
import pickle
import google.oauth2.credentials
import google_auth_oauthlib.flow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

# 유튜브 API 권한 범위 (업로드 권한)
SCOPES = ['https://www.googleapis.com/auth/youtube.upload']

def get_authenticated_service():
    """인증을 수행하고 유튜브 서비스 객체를 반환합니다."""
    creds = None
    # 이전에 발급받은 토큰이 있다면 불러옵니다.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
            
    # 유효한 인증 정보가 없으면 로그인을 수행합니다.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists('client_secrets.json'):
                print("에러: 'client_secrets.json' 파일이 없습니다.")
                print("유튜브 API를 사용하려면 Google Cloud Console에서 OAuth 2.0 클라이언트 ID를 생성하고 JSON 파일을 다운로드해야 합니다.")
                return None
            
            flow = InstalledAppFlow.from_client_secrets_file('client_secrets.json', SCOPES)
            creds = flow.run_local_server(port=0)
            
        # 다음 실행을 위해 인증 정보를 저장합니다.
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    return build('youtube', 'v3', credentials=creds)

def upload_video(youtube, file_path, title, description):
    """지정한 파일을 유튜브에 업로드합니다."""
    body = {
        'snippet': {
            'title': title,
            'description': description,
            'tags': ['유기동물', '사지말고입양하세요', 'shorts', '강아지', '고양이'],
            'categoryId': '15' # 동물/애완동물 카테고리
        },
        'status': {
            'privacyStatus': 'public', # 'private'로 설정하여 테스트 가능
            'selfDeclaredMadeForKids': False,
        }
    }

    media = MediaFileUpload(file_path, chunksize=-1, resumable=True, mimetype='video/mp4')
    
    request = youtube.videos().insert(
        part='snippet,status',
        body=body,
        media_body=media
    )
    
    print(f"업로드 시작: {title}")
    response = None
    while response is None:
        status, response = request.next_chunk()
        if status:
            print(f"업로드 중... {int(status.progress() * 100)}%")

    print(f"업로드 완료! 영상 ID: {response.get('id')}")
    return response.get('id')

def start_upload_process():
    input_file = "videos.json"
    
    if not os.path.exists(input_file):
        print("videos.json 파일이 없습니다.")
        return

    youtube = get_authenticated_service()
    if not youtube:
        return

    with open(input_file, "r", encoding="utf-8") as f:
        videos_data = json.load(f)

    for video in videos_data:
        final_path = video.get("final_path")
        
        # 이미 업로드 되었거나 파일이 없는 경우 건너뜁니다.
        if video.get("uploaded"):
            print(f"[{video.get('animal_id')}] 이미 업로드된 영상입니다.")
            continue
            
        if not final_path or not os.path.exists(final_path):
            print(f"[{video.get('animal_id')}] 합성 완료된 영상 파일이 없습니다.")
            continue

        breed = video.get("breed", "유기동물")
        d_day = video.get("D-day")
        
        # 쇼츠 제목 및 본문 구성
        title = f"[긴급] 안락사 D-{d_day} {breed} 가족을 찾습니다 #shorts"
        description = f"공공보호소에서 가족을 기다리는 {breed}입니다. 안락사까지 단 {d_day}일 남았습니다. 사지 말고 입양해주세요.\n\n#유기동물 #입양공고 #shorts"

        try:
            video_id = upload_video(youtube, final_path, title, description)
            if video_id:
                video["uploaded"] = True
                video["youtube_url"] = f"https://youtu.be/{video_id}"
                
                # 매 업로드 성공마다 즉시 저장 (유실 방지)
                with open(input_file, "w", encoding="utf-8") as f:
                    json.dump(videos_data, f, ensure_ascii=False, indent=4)
                    
        except Exception as e:
            print(f"업로드 중 오류 발생: {e}")

if __name__ == "__main__":
    start_upload_process()
