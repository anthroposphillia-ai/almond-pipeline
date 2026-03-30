"""
Almond Pipeline — upload_youtube.py
YouTube Shorts 업로드 (OAuth2 인증)

Manifesto ref: §2 투명성 (AI 제작 명시), §7 자동화 윤리
"""

import os
import json
import pickle
from pathlib import Path

from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

CLIENT_SECRETS = Path(__file__).parents[4] / "client_secrets.json"
TOKEN_PATH = Path(__file__).parents[4] / "token.pickle"

SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]


def get_credentials():
    """OAuth2 인증 토큰 발급 및 갱신."""
    creds = None

    if TOKEN_PATH.exists():
        with open(TOKEN_PATH, "rb") as f:
            creds = pickle.load(f)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                str(CLIENT_SECRETS), SCOPES
            )
            creds = flow.run_local_server(port=0)

        with open(TOKEN_PATH, "wb") as f:
            pickle.dump(creds, f)

    return creds


def upload_youtube_shorts(video_path: str, title: str, description: str) -> dict:
    """
    YouTube Shorts 업로드.
    - 제목에 #Shorts 자동 추가
    - Manifesto §2: AI 제작 명시는 description에 포함
    """
    creds = get_credentials()
    youtube = build("youtube", "v3", credentials=creds)

    # Shorts 태그 자동 추가
    if "#Shorts" not in title:
        title = f"{title[:90]} #Shorts"

    body = {
        "snippet": {
            "title": title,
            "description": description,
            "tags": ["유기동물", "입양", "Shorts", "AIgenerated", "동물보호"],
            "categoryId": "15",  # Pets & Animals
        },
        "status": {
            "privacyStatus": "public",
            "selfDeclaredMadeForKids": False,
        },
    }

    media = MediaFileUpload(video_path, chunksize=-1, resumable=True)

    print(f"  [YouTube] 업로드 중: {Path(video_path).name}")
    request = youtube.videos().insert(
        part=",".join(body.keys()),
        body=body,
        media_body=media,
    )

    response = None
    while response is None:
        status, response = request.next_chunk()
        if status:
            print(f"  [YouTube] 진행률: {int(status.progress() * 100)}%")

    video_id = response["id"]
    url = f"https://www.youtube.com/shorts/{video_id}"
    print(f"  [YouTube] 업로드 완료: {url}")

    return {
        "status": "success",
        "platform": "youtube",
        "video_id": video_id,
        "url": url,
    }
