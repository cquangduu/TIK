"""
================================================================================
YOUTUBE UPLOADER MODULE — Professional Version
================================================================================
Auto-upload videos to YouTube with retry logic, analytics, and scheduling.

Features:
    - OAuth2 authentication with token refresh
    - Resumable uploads with progress tracking
    - Exponential backoff retry logic
    - Upload analytics and logging
    - Batch upload support
    - Scheduled publishing
================================================================================
"""

from __future__ import annotations

import os
import json
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum

# Core framework
from core import (
    Config, Logger, Database,
    safe_json_load, safe_json_save,
    retry_with_backoff, ensure_directory,
    format_duration, truncate_text
)

# Initialize core components
config = Config()
logger = Logger(__name__)
db = Database()

# Google API imports
try:
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build
    from googleapiclient.errors import HttpError
    from googleapiclient.http import MediaFileUpload
    YOUTUBE_API_AVAILABLE = True
except ImportError:
    YOUTUBE_API_AVAILABLE = False
    logger.warning("Google API not installed. Run: pip install google-api-python-client google-auth-oauthlib")


# ==================== CONSTANTS ====================

YOUTUBE_SCOPES = [
    'https://www.googleapis.com/auth/youtube.upload',
    'https://www.googleapis.com/auth/youtube',
    'https://www.googleapis.com/auth/youtube.force-ssl'
]

RETRYABLE_STATUS_CODES = [500, 502, 503, 504]
MAX_RETRIES = 5
CHUNK_SIZE = 10 * 1024 * 1024  # 10MB


class VideoCategory(Enum):
    """YouTube video categories"""
    EDUCATION = "27"
    ENTERTAINMENT = "24"
    HOWTO = "26"
    PEOPLE = "22"
    NEWS = "25"
    SCIENCE = "28"


class PrivacyStatus(Enum):
    """YouTube privacy statuses"""
    PUBLIC = "public"
    UNLISTED = "unlisted"
    PRIVATE = "private"


# ==================== DATA CLASSES ====================

@dataclass
class UploadResult:
    """Result of a video upload"""
    success: bool
    video_id: str = ""
    url: str = ""
    title: str = ""
    privacy: str = ""
    error: str = ""
    upload_time: float = 0.0
    file_size: int = 0
    video_type: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "success": self.success,
            "video_id": self.video_id,
            "url": self.url,
            "title": self.title,
            "privacy": self.privacy,
            "error": self.error,
            "upload_time": self.upload_time,
            "file_size": self.file_size,
            "video_type": self.video_type,
        }


@dataclass
class VideoMetadata:
    """Video metadata for upload"""
    title: str
    description: str = ""
    tags: List[str] = field(default_factory=list)
    category_id: str = VideoCategory.EDUCATION.value
    privacy: str = PrivacyStatus.UNLISTED.value
    is_short: bool = False
    playlist_id: str = ""
    thumbnail_path: str = ""
    scheduled_time: str = ""
    notify_subscribers: bool = True
    
    def __post_init__(self):
        """Validate and sanitize metadata"""
        # Truncate title
        self.title = truncate_text(self.title, 100)
        
        # Truncate description
        self.description = truncate_text(self.description, 5000)
        
        # Limit tags
        self.tags = self.tags[:500]
        
        # Add #Shorts for shorts
        if self.is_short and "#Shorts" not in self.title:
            self.title = f"{self.title} #Shorts"
        if self.is_short and "Shorts" not in self.tags:
            self.tags.append("Shorts")


# ==================== VIDEO TEMPLATES ====================

class VideoTemplates:
    """Pre-defined templates for different video types"""
    
    @staticmethod
    def get_template(video_type: str, topic: str = "", date_str: str = "") -> VideoMetadata:
        """Get metadata template for video type"""
        if not date_str:
            date_str = datetime.now().strftime("%Y-%m-%d")
        
        templates = {
            "V1_News": VideoMetadata(
                title=f"[TOPIK 뉴스] {topic} | Tin tức tiếng Hàn {date_str}",
                description="""📰 TOPIK 뉴스 - Tin tức bằng tiếng Hàn đơn giản

🎯 Luyện nghe tiếng Hàn mỗi ngày với tin tức thời sự!

📚 Nội dung:
• Tin tức tiếng Hàn level TOPIK II
• Giải thích từ vựng quan trọng
• Subtitle song ngữ Hàn-Việt

🔔 Subscribe để nhận video mới mỗi ngày!

#TOPIK #TiengHan #LearnKorean #KoreanNews #HocTiengHan #Shorts""",
                tags=["TOPIK", "tiếng Hàn", "Korean", "news", "학습", "한국어", "베트남", "Shorts"],
                is_short=True
            ),
            
            "V2_Writing": VideoMetadata(
                title=f"[TOPIK 쓰기] Bài văn mẫu | Luyện viết {date_str}",
                description="""✍️ TOPIK 쓰기 - Hướng dẫn viết văn TOPIK II

🎯 Cấu trúc bài văn hoàn chỉnh!

📚 Nội dung:
• Dàn ý chi tiết (서론, 본론, 결론)
• Từ vựng và ngữ pháp hay
• Mẹo viết văn đạt điểm cao

🔔 Subscribe để nhận video mới mỗi ngày!

#TOPIK쓰기 #TOPIK #Writing #TiengHan #HocTiengHan #Shorts""",
                tags=["TOPIK", "쓰기", "writing", "tiếng Hàn", "Korean", "essay", "Shorts"],
                is_short=True
            ),
            
            "V3_Vocab": VideoMetadata(
                title=f"[TOPIK Quiz] Từ vựng | Vocabulary {date_str}",
                description="""📝 TOPIK Quiz - Kiểm tra từ vựng!

🎯 Test kiến thức tiếng Hàn của bạn!

📚 Format:
• Câu hỏi từ vựng TOPIK II
• 4 lựa chọn đáp án
• Giải thích chi tiết

🔔 Subscribe để nhận video mới mỗi ngày!

#TOPIKQuiz #Vocabulary #TiengHan #LearnKorean #Shorts""",
                tags=["TOPIK", "vocabulary", "quiz", "từ vựng", "tiếng Hàn", "Shorts"],
                is_short=True
            ),
            
            "V4_Grammar": VideoMetadata(
                title=f"[TOPIK Quiz] Ngữ pháp | Grammar {date_str}",
                description="""📝 TOPIK Quiz - Kiểm tra ngữ pháp!

🎯 Test ngữ pháp tiếng Hàn của bạn!

📚 Format:
• Câu hỏi ngữ pháp TOPIK II
• 4 lựa chọn đáp án
• Giải thích chi tiết

🔔 Subscribe để nhận video mới mỗi ngày!

#TOPIKQuiz #Grammar #NgữPháp #TiengHan #Shorts""",
                tags=["TOPIK", "grammar", "quiz", "ngữ pháp", "tiếng Hàn", "Shorts"],
                is_short=True
            ),
            
            "V5_DeepDive": VideoMetadata(
                title=f"[Deep Dive] {topic} | Phân tích chuyên sâu {date_str}",
                description=f"""🎓 Deep Dive - Phân tích chuyên sâu tiếng Hàn

📌 Chủ đề: {topic}

📚 Nội dung:
• Phân tích bài báo gốc
• Từ vựng nâng cao
• Ngữ pháp TOPIK II
• Luyện đọc hiểu

🔔 Subscribe để nhận video mới mỗi ngày!

#TOPIK #DeepDive #TiengHan #LearnKorean #한국어""",
                tags=["TOPIK", "deep dive", "analysis", "tiếng Hàn", "Korean", "learning"],
                is_short=False
            ),
        }
        
        return templates.get(video_type, VideoMetadata(title=topic or "TOPIK Daily"))


# ==================== YOUTUBE UPLOADER ====================

class YouTubeUploader:
    """
    Professional YouTube uploader with retry logic and analytics.
    
    Features:
        - OAuth2 authentication with token refresh
        - Resumable uploads with progress callback
        - Exponential backoff for transient errors
        - Upload analytics logging
    """
    
    def __init__(
        self,
        credentials_file: str = None,
        token_file: str = None
    ):
        """
        Initialize uploader.
        
        Args:
            credentials_file: Path to client_secrets.json
            token_file: Path to token file for caching credentials
        """
        self.credentials_file = credentials_file or config.youtube.client_secrets_file
        self.token_file = token_file or config.youtube.token_file
        self.youtube = None
        self.credentials = None
        self._channel_info = None
        
        if not YOUTUBE_API_AVAILABLE:
            logger.error("YouTube API not available")
    
    def authenticate(self) -> bool:
        """
        Authenticate with YouTube API using OAuth2.
        
        Returns:
            True if authentication successful
        """
        if not YOUTUBE_API_AVAILABLE:
            return False
        
        creds = None
        
        # Load existing token
        if os.path.exists(self.token_file):
            try:
                creds = Credentials.from_authorized_user_file(
                    self.token_file, 
                    YOUTUBE_SCOPES
                )
                logger.debug("Loaded existing YouTube credentials")
            except Exception as e:
                logger.warning(f"Could not load token: {e}")
                creds = None
        
        # Refresh or get new credentials
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                try:
                    creds.refresh(Request())
                    logger.info("Refreshed YouTube credentials")
                except Exception as e:
                    logger.warning(f"Could not refresh token: {e}")
                    creds = None
            
            if not creds:
                creds = self._get_new_credentials()
                if not creds:
                    return False
        
        # Save credentials
        with open(self.token_file, 'w') as token:
            token.write(creds.to_json())
        
        # Build YouTube service
        self.credentials = creds
        self.youtube = build('youtube', 'v3', credentials=creds)
        logger.info("YouTube API authenticated successfully")
        
        return True
    
    def _get_new_credentials(self) -> Optional[Credentials]:
        """Get new credentials through OAuth flow"""
        flow = None
        
        # Try multiple credential sources
        if os.path.exists(self.credentials_file):
            logger.info(f"Using credentials from {self.credentials_file}")
            flow = InstalledAppFlow.from_client_secrets_file(
                self.credentials_file,
                YOUTUBE_SCOPES
            )
        elif os.getenv("YOUTUBE_CREDENTIALS_JSON"):
            logger.info("Using YOUTUBE_CREDENTIALS_JSON from environment")
            client_config = json.loads(os.getenv("YOUTUBE_CREDENTIALS_JSON"))
            flow = InstalledAppFlow.from_client_config(client_config, YOUTUBE_SCOPES)
        elif os.getenv("GDRIVE_CREDENTIALS_JSON"):
            logger.info("Using GDRIVE_CREDENTIALS_JSON from environment")
            client_config = json.loads(os.getenv("GDRIVE_CREDENTIALS_JSON"))
            flow = InstalledAppFlow.from_client_config(client_config, YOUTUBE_SCOPES)
        else:
            logger.error("No credentials found!")
            logger.info("Please provide one of:")
            logger.info(f"  1. {self.credentials_file} file")
            logger.info("  2. YOUTUBE_CREDENTIALS_JSON environment variable")
            logger.info("  3. GDRIVE_CREDENTIALS_JSON environment variable")
            return None
        
        try:
            creds = flow.run_local_server(port=8080)
            logger.info("New YouTube credentials obtained")
            return creds
        except Exception as e:
            logger.error(f"OAuth flow failed: {e}")
            return None
    
    def upload_video(
        self,
        video_path: str,
        metadata: VideoMetadata,
        progress_callback: callable = None
    ) -> UploadResult:
        """
        Upload a video to YouTube with retry logic.
        
        Args:
            video_path: Path to video file
            metadata: VideoMetadata with title, description, etc.
            progress_callback: Optional callback(progress_percent)
            
        Returns:
            UploadResult with success status and video info
        """
        start_time = time.time()
        
        # Ensure authenticated
        if not self.youtube:
            if not self.authenticate():
                return UploadResult(
                    success=False,
                    error="Authentication failed"
                )
        
        # Validate video file
        video_path = Path(video_path)
        if not video_path.exists():
            logger.error(f"Video file not found: {video_path}")
            return UploadResult(
                success=False,
                error=f"Video file not found: {video_path}"
            )
        
        file_size = video_path.stat().st_size
        
        # Build request body
        body = {
            "snippet": {
                "title": metadata.title,
                "description": metadata.description,
                "tags": metadata.tags,
                "categoryId": metadata.category_id,
            },
            "status": {
                "privacyStatus": metadata.privacy,
                "selfDeclaredMadeForKids": False,
                "notifySubscribers": metadata.notify_subscribers,
            }
        }
        
        # Add scheduled time if provided
        if metadata.scheduled_time and metadata.privacy == PrivacyStatus.PRIVATE.value:
            body["status"]["publishAt"] = metadata.scheduled_time
        
        # Create media upload
        media = MediaFileUpload(
            str(video_path),
            chunksize=CHUNK_SIZE,
            resumable=True,
            mimetype='video/mp4'
        )
        
        logger.info(f"Uploading: {video_path.name}")
        logger.info(f"  Title: {truncate_text(metadata.title, 50)}")
        logger.info(f"  Size: {file_size / (1024*1024):.1f} MB")
        logger.info(f"  Privacy: {metadata.privacy}")
        
        try:
            # Execute upload with retry
            request = self.youtube.videos().insert(
                part="snippet,status",
                body=body,
                media_body=media
            )
            
            response = self._execute_upload_with_retry(request, progress_callback)
            
            video_id = response['id']
            video_url = f"https://youtu.be/{video_id}"
            
            upload_time = time.time() - start_time
            
            logger.info(f"Upload successful!")
            logger.info(f"  Video ID: {video_id}")
            logger.info(f"  URL: {video_url}")
            logger.info(f"  Time: {format_duration(upload_time)}")
            
            # Upload thumbnail if provided
            if metadata.thumbnail_path:
                self._set_thumbnail(video_id, metadata.thumbnail_path)
            
            # Add to playlist if specified
            if metadata.playlist_id:
                self._add_to_playlist(video_id, metadata.playlist_id)
            
            # Log to database
            db.insert_video(
                video_id=video_id,
                title=metadata.title,
                platform="youtube",
                video_type="short" if metadata.is_short else "long",
                duration=0,  # Would need to get from response
                status="uploaded"
            )
            
            # Log analytics
            db.log_analytics(
                event_type="youtube_upload",
                event_data={
                    "video_id": video_id,
                    "title": metadata.title,
                    "privacy": metadata.privacy,
                    "is_short": metadata.is_short,
                    "upload_time": upload_time,
                    "file_size": file_size,
                }
            )
            
            return UploadResult(
                success=True,
                video_id=video_id,
                url=video_url,
                title=metadata.title,
                privacy=metadata.privacy,
                upload_time=upload_time,
                file_size=file_size
            )
            
        except HttpError as e:
            error_content = json.loads(e.content.decode('utf-8'))
            error_reason = error_content.get('error', {}).get('errors', [{}])[0].get('reason', 'unknown')
            logger.error(f"YouTube API Error: {error_reason}")
            logger.error(f"  Details: {e}")
            
            return UploadResult(
                success=False,
                error=str(error_reason),
                upload_time=time.time() - start_time,
                file_size=file_size
            )
            
        except Exception as e:
            logger.error(f"Upload failed: {e}")
            return UploadResult(
                success=False,
                error=str(e),
                upload_time=time.time() - start_time,
                file_size=file_size
            )
    
    def _execute_upload_with_retry(
        self,
        request,
        progress_callback: callable = None
    ):
        """Execute upload with exponential backoff retry"""
        response = None
        retry_count = 0
        
        while response is None:
            try:
                status, response = request.next_chunk()
                
                if status:
                    progress = int(status.progress() * 100)
                    logger.debug(f"  Upload progress: {progress}%")
                    
                    if progress_callback:
                        progress_callback(progress)
                        
            except HttpError as e:
                if e.resp.status in RETRYABLE_STATUS_CODES and retry_count < MAX_RETRIES:
                    retry_count += 1
                    delay = min(2 ** retry_count, 60)  # Exponential backoff, max 60s
                    
                    logger.warning(f"  Retry {retry_count}/{MAX_RETRIES} after {delay}s...")
                    time.sleep(delay)
                    continue
                raise
        
        return response
    
    def _set_thumbnail(self, video_id: str, thumbnail_path: str):
        """Set custom thumbnail for a video"""
        try:
            if not os.path.exists(thumbnail_path):
                logger.warning(f"Thumbnail not found: {thumbnail_path}")
                return
            
            media = MediaFileUpload(thumbnail_path, mimetype='image/jpeg')
            self.youtube.thumbnails().set(
                videoId=video_id,
                media_body=media
            ).execute()
            logger.info(f"  Thumbnail set successfully")
        except Exception as e:
            logger.warning(f"  Could not set thumbnail: {e}")
    
    def _add_to_playlist(self, video_id: str, playlist_id: str):
        """Add video to a playlist"""
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
            logger.info(f"  Added to playlist: {playlist_id}")
        except Exception as e:
            logger.warning(f"  Could not add to playlist: {e}")
    
    def create_playlist(
        self,
        title: str,
        description: str = "",
        privacy: str = PrivacyStatus.PUBLIC.value
    ) -> Optional[str]:
        """
        Create a new playlist.
        
        Returns:
            Playlist ID or None if failed
        """
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
            logger.info(f"Created playlist: {title} (ID: {playlist_id})")
            return playlist_id
            
        except Exception as e:
            logger.error(f"Could not create playlist: {e}")
            return None
    
    def get_channel_info(self) -> Optional[Dict[str, Any]]:
        """Get information about the authenticated channel"""
        if self._channel_info:
            return self._channel_info
        
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
                self._channel_info = {
                    "id": channel['id'],
                    "title": channel['snippet']['title'],
                    "subscriber_count": channel['statistics'].get('subscriberCount', 'hidden'),
                    "video_count": channel['statistics'].get('videoCount', 0)
                }
                return self._channel_info
            return None
            
        except Exception as e:
            logger.error(f"Could not get channel info: {e}")
            return None


# ==================== BATCH UPLOAD ====================

def upload_batch(
    video_paths: List[str],
    video_data: Dict,
    uploader: YouTubeUploader = None,
    playlist_id: str = None,
    privacy: str = PrivacyStatus.UNLISTED.value
) -> List[UploadResult]:
    """
    Batch upload videos to YouTube.
    
    Args:
        video_paths: List of video file paths
        video_data: Dictionary containing metadata from final_data.json
        uploader: YouTubeUploader instance
        playlist_id: Optional playlist to add videos to
        privacy: Privacy status for all videos
        
    Returns:
        List of UploadResult objects
    """
    if uploader is None:
        uploader = YouTubeUploader()
        if not uploader.authenticate():
            return []
    
    results = []
    meta = video_data.get("meta", {})
    topic = meta.get("topic", "TOPIK")
    date_str = datetime.now().strftime("%Y-%m-%d")
    
    for video_path in video_paths:
        path = Path(video_path)
        
        if not path.exists():
            logger.warning(f"Video not found: {video_path}")
            results.append(UploadResult(
                success=False,
                error=f"File not found: {video_path}"
            ))
            continue
        
        # Determine video type from filename
        video_type = None
        for prefix in ["V1_News", "V2_Writing", "V3_Vocab", "V4_Grammar", "V5_DeepDive"]:
            if prefix in path.name:
                video_type = prefix
                break
        
        if not video_type:
            logger.warning(f"Unknown video type: {path.name}")
            continue
        
        # Get template
        metadata = VideoTemplates.get_template(video_type, topic, date_str)
        metadata.privacy = privacy
        if playlist_id:
            metadata.playlist_id = playlist_id
        
        # Upload
        result = uploader.upload_video(video_path, metadata)
        result.video_type = video_type
        results.append(result)
        
        # Small delay between uploads
        if len(video_paths) > 1:
            time.sleep(2)
    
    # Summary
    successful = sum(1 for r in results if r.success)
    logger.info(f"Batch upload complete: {successful}/{len(results)} successful")
    
    return results


# ==================== CLI ====================

def main():
    """CLI entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="YouTube Video Uploader")
    parser.add_argument("--auth", action="store_true", help="Test authentication only")
    parser.add_argument("--video", type=str, help="Path to video file")
    parser.add_argument("--title", type=str, help="Video title")
    parser.add_argument("--description", type=str, default="", help="Video description")
    parser.add_argument("--privacy", type=str, default="unlisted", 
                       choices=["public", "unlisted", "private"])
    parser.add_argument("--short", action="store_true", help="Mark as YouTube Short")
    parser.add_argument("--batch", type=str, help="Directory with videos to batch upload")
    
    args = parser.parse_args()
    
    uploader = YouTubeUploader()
    
    if args.auth:
        if uploader.authenticate():
            channel = uploader.get_channel_info()
            if channel:
                print(f"\nAuthenticated as: {channel['title']}")
                print(f"  Channel ID: {channel['id']}")
                print(f"  Subscribers: {channel['subscriber_count']}")
                print(f"  Videos: {channel['video_count']}")
        else:
            print("Authentication failed")
    
    elif args.video:
        title = args.title or Path(args.video).stem
        metadata = VideoMetadata(
            title=title,
            description=args.description,
            privacy=args.privacy,
            is_short=args.short
        )
        
        result = uploader.upload_video(args.video, metadata)
        
        if result.success:
            print(f"\nUpload successful!")
            print(f"  URL: {result.url}")
            print(f"  Time: {format_duration(result.upload_time)}")
        else:
            print(f"\nUpload failed: {result.error}")
    
    elif args.batch:
        batch_dir = Path(args.batch)
        if not batch_dir.exists():
            print(f"Directory not found: {args.batch}")
            return
        
        video_paths = list(batch_dir.glob("*.mp4"))
        results = upload_batch(
            [str(p) for p in video_paths],
            {},
            uploader,
            privacy=args.privacy
        )
        
        print(f"\nBatch upload results:")
        for r in results:
            status = "OK" if r.success else "FAILED"
            print(f"  [{status}] {r.title or r.error}")
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
