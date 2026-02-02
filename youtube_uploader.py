"""
================================================================================
YOUTUBE UPLOADER MODULE — Auto Upload Videos to YouTube
================================================================================
Features:
    - OAuth2 authentication with Google
    - Upload videos with title, description, tags
    - Set privacy (public, unlisted, private)
    - Add to playlist
    - Support for TikTok shorts and YouTube long-form
================================================================================
"""

import os
import json
import logging
import time
import pickle
import httplib2
from datetime import datetime

# Google API imports
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload

# ==================== CONFIGURATION ====================
YOUTUBE_SCOPES = [
    'https://www.googleapis.com/auth/youtube.upload',
    'https://www.googleapis.com/auth/youtube',
    'https://www.googleapis.com/auth/youtube.force-ssl'
]

# YouTube category IDs
YOUTUBE_CATEGORIES = {
    "education": "27",
    "entertainment": "24", 
    "howto": "26",
    "people": "22",
    "news": "25",
}

# Default settings
DEFAULT_CATEGORY = "27"  # Education
DEFAULT_PRIVACY = "unlisted"  # Start as unlisted for safety

# Token file for YouTube (separate from Drive)
YOUTUBE_TOKEN_FILE = "youtube_token.json"
CLIENT_SECRETS_FILE = "client_secrets.json"


class YouTubeUploader:
    """
    YouTube Video Uploader with OAuth2 authentication.
    
    Usage:
        uploader = YouTubeUploader()
        uploader.authenticate()
        video_id = uploader.upload_video(
            video_path="path/to/video.mp4",
            title="Video Title",
            description="Video description",
            tags=["tag1", "tag2"],
            privacy="public"
        )
    """
    
    def __init__(self, credentials_file=CLIENT_SECRETS_FILE, token_file=YOUTUBE_TOKEN_FILE):
        self.credentials_file = credentials_file
        self.token_file = token_file
        self.youtube = None
        self.credentials = None
        
    def authenticate(self):
        """
        Authenticate with YouTube API using OAuth2.
        First time will open browser for authorization.
        
        Can use credentials from:
        1. client_secrets.json file
        2. YOUTUBE_CREDENTIALS_JSON environment variable
        3. GDRIVE_CREDENTIALS_JSON environment variable (same Google project)
        """
        creds = None
        
        # Load existing token
        if os.path.exists(self.token_file):
            try:
                creds = Credentials.from_authorized_user_file(self.token_file, YOUTUBE_SCOPES)
                logging.info("✅ Loaded existing YouTube credentials")
            except Exception as e:
                logging.warning(f"⚠️ Could not load token: {e}")
                creds = None
        
        # Refresh or get new credentials
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                try:
                    creds.refresh(Request())
                    logging.info("🔄 Refreshed YouTube credentials")
                except Exception as e:
                    logging.warning(f"⚠️ Could not refresh token: {e}")
                    creds = None
            
            if not creds:
                # Try multiple sources for client secrets
                client_config = None
                
                # Option 1: client_secrets.json file
                if os.path.exists(self.credentials_file):
                    logging.info(f"📁 Using {self.credentials_file}")
                    flow = InstalledAppFlow.from_client_secrets_file(
                        self.credentials_file, 
                        YOUTUBE_SCOPES
                    )
                # Option 2: YOUTUBE_CREDENTIALS_JSON env var
                elif os.getenv("YOUTUBE_CREDENTIALS_JSON"):
                    logging.info("🔑 Using YOUTUBE_CREDENTIALS_JSON from environment")
                    client_config = json.loads(os.getenv("YOUTUBE_CREDENTIALS_JSON"))
                    flow = InstalledAppFlow.from_client_config(client_config, YOUTUBE_SCOPES)
                # Option 3: GDRIVE_CREDENTIALS_JSON env var (same Google project)
                elif os.getenv("GDRIVE_CREDENTIALS_JSON"):
                    logging.info("🔑 Using GDRIVE_CREDENTIALS_JSON from environment (same Google project)")
                    client_config = json.loads(os.getenv("GDRIVE_CREDENTIALS_JSON"))
                    flow = InstalledAppFlow.from_client_config(client_config, YOUTUBE_SCOPES)
                else:
                    logging.error(f"❌ No credentials found!")
                    logging.info("   Please provide one of:")
                    logging.info(f"   1. {self.credentials_file} file")
                    logging.info("   2. YOUTUBE_CREDENTIALS_JSON environment variable")
                    logging.info("   3. GDRIVE_CREDENTIALS_JSON environment variable")
                    logging.info("")
                    logging.info("   To get credentials:")
                    logging.info("   1. Go to https://console.cloud.google.com/")
                    logging.info("   2. Enable YouTube Data API v3")
                    logging.info("   3. Create OAuth 2.0 Client ID (Desktop app)")
                    logging.info("   4. Download and use the JSON")
                    return False
                
                creds = flow.run_local_server(port=8080)
                logging.info("✅ New YouTube credentials obtained")
        
        # Save credentials
        with open(self.token_file, 'w') as token:
            token.write(creds.to_json())
        
        # Build YouTube service
        self.credentials = creds
        self.youtube = build('youtube', 'v3', credentials=creds)
        logging.info("✅ YouTube API authenticated successfully")
        return True
    
    def upload_video(
        self,
        video_path: str,
        title: str,
        description: str = "",
        tags: list = None,
        category_id: str = DEFAULT_CATEGORY,
        privacy: str = DEFAULT_PRIVACY,
        is_short: bool = False,
        playlist_id: str = None,
        notify_subscribers: bool = True,
        thumbnail_path: str = None,
        scheduled_time: str = None
    ) -> dict:
        """
        Upload a video to YouTube.
        
        Args:
            video_path: Path to video file
            title: Video title (max 100 chars)
            description: Video description (max 5000 chars)
            tags: List of tags
            category_id: YouTube category ID
            privacy: 'public', 'unlisted', or 'private'
            is_short: If True, adds #Shorts to title
            playlist_id: Optional playlist to add video to
            notify_subscribers: Whether to notify subscribers
            thumbnail_path: Optional custom thumbnail
            scheduled_time: ISO 8601 datetime for scheduled publish
            
        Returns:
            dict with video_id, url, status
        """
        if not self.youtube:
            if not self.authenticate():
                return {"success": False, "error": "Authentication failed"}
        
        if not os.path.exists(video_path):
            logging.error(f"❌ Video file not found: {video_path}")
            return {"success": False, "error": "Video file not found"}
        
        # Prepare title (add #Shorts for shorts)
        if is_short and "#Shorts" not in title:
            title = f"{title} #Shorts"
        
        # Truncate if too long
        title = title[:100]
        description = description[:5000]
        
        # Prepare tags
        if tags is None:
            tags = []
        if is_short and "Shorts" not in tags:
            tags.append("Shorts")
        
        # Build request body
        body = {
            "snippet": {
                "title": title,
                "description": description,
                "tags": tags[:500],  # Max 500 tags
                "categoryId": category_id,
            },
            "status": {
                "privacyStatus": privacy,
                "selfDeclaredMadeForKids": False,
                "notifySubscribers": notify_subscribers,
            }
        }
        
        # Add scheduled time if provided
        if scheduled_time and privacy == "private":
            body["status"]["publishAt"] = scheduled_time
        
        # Create media upload
        media = MediaFileUpload(
            video_path,
            chunksize=10 * 1024 * 1024,  # 10MB chunks
            resumable=True,
            mimetype='video/mp4'
        )
        
        try:
            logging.info(f"📤 Uploading: {os.path.basename(video_path)}")
            logging.info(f"   Title: {title[:50]}...")
            logging.info(f"   Privacy: {privacy}")
            
            # Execute upload
            request = self.youtube.videos().insert(
                part="snippet,status",
                body=body,
                media_body=media
            )
            
            response = None
            retry_count = 0
            max_retries = 3
            
            while response is None:
                try:
                    status, response = request.next_chunk()
                    if status:
                        progress = int(status.progress() * 100)
                        logging.info(f"   Upload progress: {progress}%")
                except HttpError as e:
                    if e.resp.status in [500, 502, 503, 504] and retry_count < max_retries:
                        retry_count += 1
                        logging.warning(f"   Retry {retry_count}/{max_retries}...")
                        time.sleep(5 * retry_count)
                        continue
                    raise
            
            video_id = response['id']
            video_url = f"https://youtu.be/{video_id}"
            
            logging.info(f"✅ Upload successful!")
            logging.info(f"   Video ID: {video_id}")
            logging.info(f"   URL: {video_url}")
            
            # Upload thumbnail if provided
            if thumbnail_path and os.path.exists(thumbnail_path):
                self._set_thumbnail(video_id, thumbnail_path)
            
            # Add to playlist if specified
            if playlist_id:
                self._add_to_playlist(video_id, playlist_id)
            
            return {
                "success": True,
                "video_id": video_id,
                "url": video_url,
                "title": title,
                "privacy": privacy
            }
            
        except HttpError as e:
            error_content = json.loads(e.content.decode('utf-8'))
            error_reason = error_content.get('error', {}).get('errors', [{}])[0].get('reason', 'unknown')
            logging.error(f"❌ YouTube API Error: {error_reason}")
            logging.error(f"   Details: {e}")
            return {"success": False, "error": str(error_reason)}
        except Exception as e:
            logging.error(f"❌ Upload failed: {e}")
            return {"success": False, "error": str(e)}
    
    def _set_thumbnail(self, video_id: str, thumbnail_path: str):
        """Set custom thumbnail for a video."""
        try:
            media = MediaFileUpload(thumbnail_path, mimetype='image/jpeg')
            self.youtube.thumbnails().set(
                videoId=video_id,
                media_body=media
            ).execute()
            logging.info(f"   ✅ Thumbnail set successfully")
        except Exception as e:
            logging.warning(f"   ⚠️ Could not set thumbnail: {e}")
    
    def _add_to_playlist(self, video_id: str, playlist_id: str):
        """Add video to a playlist."""
        try:
            body = {
                "snippet": {
                    "playlistId": playlist_id,
                    "resourceId": {
                        "kind": "youtube#video",
                        "videoId": video_id
                    }
                }
            }
            self.youtube.playlistItems().insert(
                part="snippet",
                body=body
            ).execute()
            logging.info(f"   ✅ Added to playlist: {playlist_id}")
        except Exception as e:
            logging.warning(f"   ⚠️ Could not add to playlist: {e}")
    
    def create_playlist(self, title: str, description: str = "", privacy: str = "public") -> str:
        """Create a new playlist and return its ID."""
        if not self.youtube:
            if not self.authenticate():
                return None
        
        try:
            body = {
                "snippet": {
                    "title": title,
                    "description": description
                },
                "status": {
                    "privacyStatus": privacy
                }
            }
            response = self.youtube.playlists().insert(
                part="snippet,status",
                body=body
            ).execute()
            
            playlist_id = response['id']
            logging.info(f"✅ Created playlist: {title} (ID: {playlist_id})")
            return playlist_id
            
        except Exception as e:
            logging.error(f"❌ Could not create playlist: {e}")
            return None
    
    def get_channel_info(self) -> dict:
        """Get information about the authenticated channel."""
        if not self.youtube:
            if not self.authenticate():
                return None
        
        try:
            response = self.youtube.channels().list(
                part="snippet,statistics",
                mine=True
            ).execute()
            
            if response['items']:
                channel = response['items'][0]
                return {
                    "id": channel['id'],
                    "title": channel['snippet']['title'],
                    "subscriber_count": channel['statistics'].get('subscriberCount', 'hidden'),
                    "video_count": channel['statistics'].get('videoCount', 0)
                }
            return None
            
        except Exception as e:
            logging.error(f"❌ Could not get channel info: {e}")
            return None


def upload_tiktok_to_youtube(
    video_paths: list,
    video_data: dict,
    uploader: YouTubeUploader = None,
    playlist_id: str = None,
    privacy: str = "unlisted"
) -> list:
    """
    Batch upload TikTok videos to YouTube as Shorts.
    
    Args:
        video_paths: List of video file paths
        video_data: Dictionary containing video metadata from final_data.json
        uploader: YouTubeUploader instance (creates one if None)
        playlist_id: Optional playlist to add all videos to
        privacy: Privacy status for all videos
        
    Returns:
        List of upload results
    """
    if uploader is None:
        uploader = YouTubeUploader()
        if not uploader.authenticate():
            return []
    
    results = []
    meta = video_data.get("meta", {})
    topic = meta.get("topic", "TOPIK")
    date_str = datetime.now().strftime("%Y-%m-%d")
    
    # Video type configurations
    video_configs = {
        "V1_News": {
            "title_template": f"[TOPIK 뉴스] {topic} | Tin tức tiếng Hàn {date_str}",
            "description_template": """📰 TOPIK 뉴스 - Tin tức bằng tiếng Hàn đơn giản

🎯 Luyện nghe tiếng Hàn mỗi ngày với tin tức thời sự!

📚 Nội dung:
• Tin tức tiếng Hàn level TOPIK II
• Giải thích từ vựng quan trọng
• Subtitle song ngữ Hàn-Việt

#TOPIK #TiengHan #LearnKorean #KoreanNews #HocTiengHan #Shorts""",
            "tags": ["TOPIK", "tiếng Hàn", "Korean", "news", "학습", "한국어", "베트남", "Shorts"],
            "is_short": True
        },
        "V2_Writing": {
            "title_template": f"[TOPIK 쓰기] Bài văn mẫu | Luyện viết {date_str}",
            "description_template": """✍️ TOPIK 쓰기 - Hướng dẫn viết văn TOPIK II

🎯 Cấu trúc bài văn hoàn chỉnh!

📚 Nội dung:
• Dàn ý chi tiết (서론, 본론, 결론)
• Từ vựng và ngữ pháp hay
• Mẹo viết văn đạt điểm cao

#TOPIK쓰기 #TOPIK #Writing #TiengHan #HocTiengHan #Shorts""",
            "tags": ["TOPIK", "쓰기", "writing", "tiếng Hàn", "Korean", "essay", "Shorts"],
            "is_short": True
        },
        "V3_Vocab": {
            "title_template": f"[TOPIK Quiz] Từ vựng | Vocabulary {date_str}",
            "description_template": """📝 TOPIK Quiz - Kiểm tra từ vựng!

🎯 Test kiến thức tiếng Hàn của bạn!

📚 Format:
• Câu hỏi từ vựng TOPIK II
• 4 lựa chọn đáp án
• Giải thích chi tiết

#TOPIKQuiz #Vocabulary #TiengHan #LearnKorean #Shorts""",
            "tags": ["TOPIK", "vocabulary", "quiz", "từ vựng", "tiếng Hàn", "Shorts"],
            "is_short": True
        },
        "V4_Grammar": {
            "title_template": f"[TOPIK Quiz] Ngữ pháp | Grammar {date_str}",
            "description_template": """📝 TOPIK Quiz - Kiểm tra ngữ pháp!

🎯 Test ngữ pháp tiếng Hàn của bạn!

📚 Format:
• Câu hỏi ngữ pháp TOPIK II
• 4 lựa chọn đáp án
• Giải thích chi tiết

#TOPIKQuiz #Grammar #NgữPháp #TiengHan #Shorts""",
            "tags": ["TOPIK", "grammar", "quiz", "ngữ pháp", "tiếng Hàn", "Shorts"],
            "is_short": True
        },
        "V5_DeepDive": {
            "title_template": f"[Deep Dive] {topic} | Phân tích chuyên sâu {date_str}",
            "description_template": """🎓 Deep Dive - Phân tích chuyên sâu tiếng Hàn

🎯 Video dài giải thích chi tiết!

📚 Nội dung:
• Phân tích bài báo gốc
• Từ vựng nâng cao
• Ngữ pháp TOPIK II
• Luyện đọc hiểu

#TOPIK #DeepDive #TiengHan #LearnKorean #한국어""",
            "tags": ["TOPIK", "deep dive", "analysis", "tiếng Hàn", "Korean", "learning"],
            "is_short": False
        }
    }
    
    for video_path in video_paths:
        if not os.path.exists(video_path):
            logging.warning(f"⚠️ Video not found: {video_path}")
            continue
        
        # Determine video type from filename
        filename = os.path.basename(video_path)
        video_type = None
        config = None
        
        for prefix, cfg in video_configs.items():
            if prefix in filename:
                video_type = prefix
                config = cfg
                break
        
        if not config:
            logging.warning(f"⚠️ Unknown video type: {filename}")
            continue
        
        # Upload
        result = uploader.upload_video(
            video_path=video_path,
            title=config["title_template"],
            description=config["description_template"],
            tags=config["tags"],
            category_id=YOUTUBE_CATEGORIES["education"],
            privacy=privacy,
            is_short=config["is_short"],
            playlist_id=playlist_id
        )
        
        result["video_type"] = video_type
        result["filename"] = filename
        results.append(result)
        
        # Small delay between uploads
        if len(video_paths) > 1:
            time.sleep(2)
    
    return results


def upload_deep_dive_to_youtube(
    video_path: str,
    video_data: dict,
    youtube_info_path: str = None,
    uploader: YouTubeUploader = None,
    privacy: str = "unlisted"
) -> dict:
    """
    Upload Deep Dive video to YouTube with full metadata.
    
    Args:
        video_path: Path to the Deep Dive video
        video_data: Dictionary containing video metadata
        youtube_info_path: Path to youtube_info.txt with timestamps
        uploader: YouTubeUploader instance
        privacy: Privacy status
        
    Returns:
        Upload result dict
    """
    if uploader is None:
        uploader = YouTubeUploader()
        if not uploader.authenticate():
            return {"success": False, "error": "Authentication failed"}
    
    if not os.path.exists(video_path):
        return {"success": False, "error": f"Video not found: {video_path}"}
    
    # Get metadata
    meta = video_data.get("meta", {})
    topic = meta.get("topic", "TOPIK Deep Dive")
    date_str = datetime.now().strftime("%Y-%m-%d")
    
    # Build title
    title = f"[TOPIK Deep Dive] {topic} | Phân tích chuyên sâu tiếng Hàn"
    
    # Build description
    description_parts = [
        f"🎓 TOPIK Deep Dive - {topic}",
        "",
        "📚 Trong video này:",
        "• Phân tích bài báo tiếng Hàn gốc",
        "• Giải thích từ vựng nâng cao TOPIK II",
        "• Ngữ pháp quan trọng",
        "• Luyện đọc hiểu chuyên sâu",
        "",
    ]
    
    # Add timestamps from youtube_info.txt if available
    if youtube_info_path and os.path.exists(youtube_info_path):
        with open(youtube_info_path, 'r', encoding='utf-8') as f:
            youtube_info = f.read()
        
        # Extract timestamps section
        if "TIMESTAMPS:" in youtube_info or "⏰" in youtube_info:
            description_parts.append("⏰ TIMESTAMPS:")
            for line in youtube_info.split('\n'):
                if line.strip().startswith(('0:', '1:', '2:', '3:', '4:', '5:', '6:', '7:', '8:', '9:')):
                    description_parts.append(line.strip())
            description_parts.append("")
    
    description_parts.extend([
        "🔔 Subscribe để nhận video mới mỗi ngày!",
        "",
        "#TOPIK #TiengHan #LearnKorean #한국어 #DeepDive #KoreanNews"
    ])
    
    description = "\n".join(description_parts)
    
    # Tags
    tags = [
        "TOPIK", "TOPIK II", "tiếng Hàn", "Korean", "học tiếng Hàn",
        "learn Korean", "한국어", "deep dive", "analysis", "vocabulary",
        "grammar", "reading", "news", "베트남"
    ]
    
    # Upload
    result = uploader.upload_video(
        video_path=video_path,
        title=title,
        description=description,
        tags=tags,
        category_id=YOUTUBE_CATEGORIES["education"],
        privacy=privacy,
        is_short=False,
        notify_subscribers=True
    )
    
    return result


# ==================== CLI INTERFACE ====================
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="YouTube Video Uploader")
    parser.add_argument("--auth", action="store_true", help="Test authentication only")
    parser.add_argument("--video", type=str, help="Path to video file")
    parser.add_argument("--title", type=str, help="Video title")
    parser.add_argument("--description", type=str, default="", help="Video description")
    parser.add_argument("--privacy", type=str, default="unlisted", choices=["public", "unlisted", "private"])
    parser.add_argument("--short", action="store_true", help="Mark as YouTube Short")
    
    args = parser.parse_args()
    
    logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
    
    uploader = YouTubeUploader()
    
    if args.auth:
        if uploader.authenticate():
            channel = uploader.get_channel_info()
            if channel:
                print(f"\n✅ Authenticated as: {channel['title']}")
                print(f"   Channel ID: {channel['id']}")
                print(f"   Subscribers: {channel['subscriber_count']}")
                print(f"   Videos: {channel['video_count']}")
        else:
            print("❌ Authentication failed")
    
    elif args.video:
        if not args.title:
            args.title = os.path.splitext(os.path.basename(args.video))[0]
        
        result = uploader.upload_video(
            video_path=args.video,
            title=args.title,
            description=args.description,
            privacy=args.privacy,
            is_short=args.short
        )
        
        if result.get("success"):
            print(f"\n✅ Upload successful!")
            print(f"   URL: {result['url']}")
        else:
            print(f"\n❌ Upload failed: {result.get('error')}")
    
    else:
        parser.print_help()
