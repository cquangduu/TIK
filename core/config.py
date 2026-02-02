"""
================================================================================
DAILY KOREAN — Configuration Management
================================================================================
Centralized configuration for all modules.
Supports environment variables, .env files, and defaults.
================================================================================
"""

import os
from pathlib import Path
from typing import Optional, Dict, Any
from dataclasses import dataclass, field
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


@dataclass
class APIConfig:
    """API-related configuration"""
    gemini_api_key: str = ""
    azure_speech_key: str = ""
    azure_speech_region: str = "koreacentral"
    openai_api_key: str = ""


@dataclass
class TelegramConfig:
    """Telegram bot configuration"""
    bot_token: str = ""
    admin_id: str = ""
    channel_id: str = ""
    payment_token: str = ""
    premium_price: float = 5.00
    patreon_url: str = "https://patreon.com/topikdaily"
    kofi_url: str = "https://ko-fi.com/topikdaily"


@dataclass
class YouTubeConfig:
    """YouTube configuration"""
    client_secrets_file: str = "client_secrets.json"
    token_file: str = "youtube_token.json"
    default_privacy: str = "unlisted"
    default_category: str = "27"  # Education


@dataclass
class GoogleDriveConfig:
    """Google Drive configuration"""
    folder_id: str = ""
    token_file: str = "drive_token.json"
    client_secrets_file: str = "client_secrets.json"


@dataclass
class EmailConfig:
    """Email configuration"""
    smtp_server: str = "smtp.gmail.com"
    smtp_port: int = 587
    address: str = ""
    password: str = ""
    convertkit_api_key: str = ""
    mailchimp_api_key: str = ""


@dataclass
class SocialConfig:
    """Social media configuration"""
    twitter_bearer_token: str = ""
    discord_webhook_url: str = ""
    tiktok_access_token: str = ""


@dataclass
class PathsConfig:
    """File paths configuration"""
    root_dir: Path = field(default_factory=lambda: Path(__file__).parent.parent)
    data_dir: Path = field(default_factory=lambda: Path("data"))
    logs_dir: Path = field(default_factory=lambda: Path("logs"))
    output_dir: Path = field(default_factory=lambda: Path("temp_processing"))
    remotion_dir: Path = field(default_factory=lambda: Path("topik-video"))
    blog_dir: Path = field(default_factory=lambda: Path("blog_output"))
    podcast_dir: Path = field(default_factory=lambda: Path("podcast_output"))
    anki_dir: Path = field(default_factory=lambda: Path("anki_decks"))
    premium_dir: Path = field(default_factory=lambda: Path("premium_content"))
    data_file: str = "topik-video/public/final_data.json"
    
    def __post_init__(self):
        """Ensure directories exist"""
        for dir_attr in ['data_dir', 'logs_dir', 'output_dir', 'blog_dir', 
                         'podcast_dir', 'anki_dir', 'premium_dir']:
            path = getattr(self, dir_attr)
            if isinstance(path, Path):
                path.mkdir(parents=True, exist_ok=True)


@dataclass
class ContentConfig:
    """Content generation settings"""
    max_tiktok_duration: int = 59  # seconds
    max_youtube_duration: int = 1800  # 30 minutes
    default_tts_voice_ko: str = "ko-KR-SunHiNeural"
    default_tts_voice_vi: str = "vi-VN-HoaiMyNeural"
    tts_rate: str = "+5%"
    audio_format: str = "mp3"
    video_fps: int = 30


@dataclass
class Config:
    """Master configuration class"""
    api: APIConfig = field(default_factory=APIConfig)
    telegram: TelegramConfig = field(default_factory=TelegramConfig)
    youtube: YouTubeConfig = field(default_factory=YouTubeConfig)
    google_drive: GoogleDriveConfig = field(default_factory=GoogleDriveConfig)
    email: EmailConfig = field(default_factory=EmailConfig)
    social: SocialConfig = field(default_factory=SocialConfig)
    paths: PathsConfig = field(default_factory=PathsConfig)
    content: ContentConfig = field(default_factory=ContentConfig)
    
    # Metadata
    app_name: str = "DAILY KOREAN"
    version: str = "2.0.0"
    debug: bool = False
    
    @classmethod
    def from_env(cls) -> "Config":
        """Load configuration from environment variables"""
        return cls(
            api=APIConfig(
                gemini_api_key=os.getenv("GEMINI_API_KEY", ""),
                azure_speech_key=os.getenv("AZURE_SPEECH_KEY", ""),
                azure_speech_region=os.getenv("AZURE_SPEECH_REGION", "koreacentral"),
                openai_api_key=os.getenv("OPENAI_API_KEY", ""),
            ),
            telegram=TelegramConfig(
                bot_token=os.getenv("TELEGRAM_BOT_TOKEN", ""),
                admin_id=os.getenv("TELEGRAM_ADMIN_ID", ""),
                channel_id=os.getenv("TELEGRAM_CHANNEL_ID", ""),
                payment_token=os.getenv("TELEGRAM_PAYMENT_TOKEN", ""),
            ),
            youtube=YouTubeConfig(
                default_privacy=os.getenv("YOUTUBE_DEFAULT_PRIVACY", "unlisted"),
            ),
            google_drive=GoogleDriveConfig(
                folder_id=os.getenv("GOOGLE_DRIVE_FOLDER_ID", ""),
            ),
            email=EmailConfig(
                smtp_server=os.getenv("EMAIL_SMTP_SERVER", "smtp.gmail.com"),
                smtp_port=int(os.getenv("EMAIL_SMTP_PORT", "587")),
                address=os.getenv("EMAIL_ADDRESS", ""),
                password=os.getenv("EMAIL_PASSWORD", ""),
                convertkit_api_key=os.getenv("CONVERTKIT_API_KEY", ""),
                mailchimp_api_key=os.getenv("MAILCHIMP_API_KEY", ""),
            ),
            social=SocialConfig(
                twitter_bearer_token=os.getenv("TWITTER_BEARER_TOKEN", ""),
                discord_webhook_url=os.getenv("DISCORD_WEBHOOK_URL", ""),
            ),
            debug=os.getenv("DEBUG", "false").lower() == "true",
        )
    
    def validate(self) -> Dict[str, bool]:
        """Validate configuration and return status for each component"""
        return {
            "gemini_api": bool(self.api.gemini_api_key),
            "azure_tts": bool(self.api.azure_speech_key),
            "telegram_bot": bool(self.telegram.bot_token),
            "youtube_upload": Path(self.youtube.client_secrets_file).exists(),
            "google_drive": bool(self.google_drive.folder_id),
            "email": bool(self.email.address and self.email.password),
            "twitter": bool(self.social.twitter_bearer_token),
            "discord": bool(self.social.discord_webhook_url),
        }


# Singleton instance
_config: Optional[Config] = None


def get_config() -> Config:
    """Get or create configuration singleton"""
    global _config
    if _config is None:
        _config = Config.from_env()
    return _config


def reload_config() -> Config:
    """Force reload configuration from environment"""
    global _config
    load_dotenv(override=True)
    _config = Config.from_env()
    return _config
