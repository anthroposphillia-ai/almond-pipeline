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
        status = video.get("status", "waiting")
        animal_id = video.get("animal_id")

        # 2. 안락사 결말로 판정된 경우 업로드 처리 건너뛰기 (추후 수동 알림 등으로 보완 가능)
        if status == "euthanized":
            print(f"[{animal_id}] 안락사 결말 영상입니다. 정책에 따라 업로드하지 않고 건너뜁니다.")
            continue

        # 3. 쇼츠 제목 및 본문 구성 (메타데이터 활용 가능하도록 확장성 유지)
        title = f"[긴급] 안락사 D-{d_day} {breed} 가족을 찾습니다 #shorts"
        description = f"공공보호소에서 가족을 기다리는 {breed}입니다. 안락사까지 단 {d_day}일 남았습니다. 사지 말고 입양해주세요.\n\n#유기동물 #입양공고 #shorts"

        try:
            # 실제 업로드 실행
            youtube_video_id = upload_video(youtube, final_path, title, description)
            if youtube_video_id:
                video["uploaded"] = True
                video["youtube_url"] = f"https://youtu.be/{youtube_video_id}"
                
                # 4. 업로드 후 고정(안내) 댓글 자동 작성 (API를 통한 Pin은 수동 필요 / 내용만 작성)
                comment_body = "입양 문의는 영상 설명란의 보호소 연락처로 직접 해주세요. 저희는 콘텐츠 제작팀입니다. 모든 데이터는 국가동물보호정보시스템 공식 공공데이터입니다."
                try:
                    youtube.commentThreads().insert(
                        part="snippet",
                        body={
                            "snippet": {
                                "videoId": youtube_video_id,
                                "topLevelComment": {"snippet": {"textOriginal": comment_body}}
                            }
                        }
                    ).execute()
                except Exception as ce:
                    print(f"[{animal_id}] 안내 댓글 작성 실패: {ce}")

                # 5. 상태 변화(입양 등) 발생 시 이전 영상들에 댓글 추가 로직 (개념적 구현)
                if status == "adopted":
                    # 이전 영상들의 ID를 찾는 로직은 DB/로그 확장이 필요함 (여기서는 현재 영상에 기록만 남김)
                    print(f"[{animal_id}] 입양 완료 상태 감지. 이전 영상들에 순차적으로 댓글 작성이 권장됩니다.")

                # 매 업로드 성공마다 즉시 저장 (유실 방지)
                with open(input_file, "w", encoding="utf-8") as f:
                    json.dump(videos_data, f, ensure_ascii=False, indent=4)
                    
        except Exception as e:
            print(f"업로드 중 오류 발생: {e}")

if __name__ == "__main__":
    start_upload_process()
