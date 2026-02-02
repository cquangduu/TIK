#!/usr/bin/env python3
"""
TOPIK Daily - Main Automation Scheduler
Orchestrates all daily tasks for content generation, rendering, and publishing.
Optimized for low-resource server (1vCPU/2GB RAM).

TÍCH HỢP với các module hiện có:
    - main.py: Pipeline tạo nội dung chính
    - youtube_uploader.py: Upload YouTube
    - blog_generator.py: Tạo blog
    - podcast_generator.py: Tạo podcast
    - social_publisher.py: Đăng social media
    - github_deployer.py: Deploy GitHub Pages
    - telegram_bot.py: Bot Telegram
    - monetization.py: Quản lý doanh thu
"""

import os
import sys
import logging
import asyncio
import schedule
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Dict, Any
import json
import sqlite3
from dataclasses import dataclass, asdict
from enum import Enum

# Add parent directory to path (để import các module gốc)
ROOT_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT_DIR))

from dotenv import load_dotenv
load_dotenv()

# ═══════════════════════════════════════════════════════════════════════════════
# IMPORT CÁC MODULE HIỆN CÓ TỪ THƯ MỤC GỐC
# ═══════════════════════════════════════════════════════════════════════════════
try:
    from main import (
        generate_phase_1_news,
        generate_phase_2_deep_news,
        generate_phase_3_essay,
        generate_phase_4_quiz,
        process_all_assets,
        run_full_pipeline
    )
    MAIN_AVAILABLE = True
except ImportError as e:
    logging.warning(f"⚠️ Không thể import main.py: {e}")
    MAIN_AVAILABLE = False

try:
    from youtube_uploader import YouTubeUploader, upload_tiktok_to_youtube, upload_deep_dive_to_youtube
    YOUTUBE_AVAILABLE = True
except ImportError as e:
    logging.warning(f"⚠️ Không thể import youtube_uploader: {e}")
    YOUTUBE_AVAILABLE = False

try:
    from blog_generator import generate_blog_from_data, BlogGenerator
    BLOG_AVAILABLE = True
except ImportError as e:
    logging.warning(f"⚠️ Không thể import blog_generator: {e}")
    BLOG_AVAILABLE = False

try:
    from podcast_generator import generate_podcast_from_data, PodcastGenerator
    PODCAST_AVAILABLE = True
except ImportError as e:
    logging.warning(f"⚠️ Không thể import podcast_generator: {e}")
    PODCAST_AVAILABLE = False

try:
    from social_publisher import publish_to_social_media, SocialMediaPublisher
    SOCIAL_AVAILABLE = True
except ImportError as e:
    logging.warning(f"⚠️ Không thể import social_publisher: {e}")
    SOCIAL_AVAILABLE = False

try:
    from github_deployer import deploy_blog_to_github, GitHubDeployer
    GITHUB_AVAILABLE = True
except ImportError as e:
    logging.warning(f"⚠️ Không thể import github_deployer: {e}")
    GITHUB_AVAILABLE = False

try:
    from telegram_bot import send_daily_push, TOPIKBot
    TELEGRAM_AVAILABLE = True
except ImportError as e:
    logging.warning(f"⚠️ Không thể import telegram_bot: {e}")
    TELEGRAM_AVAILABLE = False

try:
    from monetization import MonetizationManager
    MONETIZATION_AVAILABLE = True
except ImportError as e:
    logging.warning(f"⚠️ Không thể import monetization: {e}")
    MONETIZATION_AVAILABLE = False

# ═══════════════════════════════════════════════════════════════════════════════
# IMPORT CÁC MODULE CHUYÊN NGHIỆP MỚI
# ═══════════════════════════════════════════════════════════════════════════════
try:
    from email_marketing import EmailMarketingManager, LeadMagnetGenerator, DripCampaignManager
    EMAIL_MARKETING_AVAILABLE = True
except ImportError as e:
    logging.warning(f"⚠️ Không thể import email_marketing: {e}")
    EMAIL_MARKETING_AVAILABLE = False

try:
    from anki_generator import AnkiDeckGenerator
    ANKI_AVAILABLE = True
except ImportError as e:
    logging.warning(f"⚠️ Không thể import anki_generator: {e}")
    ANKI_AVAILABLE = False

try:
    from seo_optimizer import SEOOptimizer, KeywordResearcher
    SEO_AVAILABLE = True
except ImportError as e:
    logging.warning(f"⚠️ Không thể import seo_optimizer: {e}")
    SEO_AVAILABLE = False

try:
    from analytics_dashboard import AnalyticsDatabase, PlatformCollector, ReportGenerator
    ANALYTICS_AVAILABLE = True
except ImportError as e:
    logging.warning(f"⚠️ Không thể import analytics_dashboard: {e}")
    ANALYTICS_AVAILABLE = False

try:
    from course_generator import CourseGenerator, create_topik1_course, create_topik2_course
    COURSE_AVAILABLE = True
except ImportError as e:
    logging.warning(f"⚠️ Không thể import course_generator: {e}")
    COURSE_AVAILABLE = False

try:
    from affiliate_manager import AffiliateManager, AffiliateReporter
    AFFILIATE_AVAILABLE = True
except ImportError as e:
    logging.warning(f"⚠️ Không thể import affiliate_manager: {e}")
    AFFILIATE_AVAILABLE = False

try:
    from community_manager import CommunityBot, PremiumManager, get_community_stats
    COMMUNITY_AVAILABLE = True
except ImportError as e:
    logging.warning(f"⚠️ Không thể import community_manager: {e}")
    COMMUNITY_AVAILABLE = False

try:
    from premium_gatekeeper import AccessController, SubscriptionManager
    PREMIUM_AVAILABLE = True
except ImportError as e:
    logging.warning(f"⚠️ Không thể import premium_gatekeeper: {e}")
    PREMIUM_AVAILABLE = False

# ═══════════════════════════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════════

BASE_DIR = ROOT_DIR  # Sử dụng ROOT_DIR đã định nghĩa ở trên
DATA_DIR = BASE_DIR / "data"
CONTENT_DIR = DATA_DIR / "content"
AUDIO_DIR = DATA_DIR / "audio"
VIDEO_DIR = BASE_DIR / "topik-video" / "out"  # Thư mục output video từ Remotion
LOG_DIR = BASE_DIR / "logs"
DB_PATH = DATA_DIR / "analytics.db"

# Đường dẫn đến các file dữ liệu chính
FINAL_DATA_PATH = BASE_DIR / "topik-video" / "public" / "final_data.json"

# Create directories
for d in [DATA_DIR, CONTENT_DIR, AUDIO_DIR, VIDEO_DIR, LOG_DIR]:
    d.mkdir(parents=True, exist_ok=True)

# ═══════════════════════════════════════════════════════════════════════════════
# LOGGING SETUP
# ═══════════════════════════════════════════════════════════════════════════════

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)-8s | %(name)s | %(message)s',
    handlers=[
        logging.FileHandler(LOG_DIR / "scheduler.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("TopikScheduler")

# ═══════════════════════════════════════════════════════════════════════════════
# TASK STATUS TRACKING
# ═══════════════════════════════════════════════════════════════════════════════

class TaskStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    SKIPPED = "skipped"

@dataclass
class TaskResult:
    task_name: str
    status: TaskStatus
    started_at: datetime
    completed_at: Optional[datetime] = None
    duration_seconds: float = 0
    error_message: Optional[str] = None
    output_data: Optional[Dict[str, Any]] = None

class TaskTracker:
    """Track task execution for monitoring and debugging."""
    
    def __init__(self, db_path: Path):
        self.db_path = db_path
        self._init_db()
    
    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS task_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    task_name TEXT NOT NULL,
                    status TEXT NOT NULL,
                    started_at TIMESTAMP NOT NULL,
                    completed_at TIMESTAMP,
                    duration_seconds REAL,
                    error_message TEXT,
                    output_data TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_task_date 
                ON task_history(task_name, started_at)
            """)
    
    def log_task(self, result: TaskResult):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO task_history 
                (task_name, status, started_at, completed_at, duration_seconds, error_message, output_data)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                result.task_name,
                result.status.value,
                result.started_at.isoformat(),
                result.completed_at.isoformat() if result.completed_at else None,
                result.duration_seconds,
                result.error_message,
                json.dumps(result.output_data) if result.output_data else None
            ))
    
    def get_today_tasks(self) -> list:
        today = datetime.now().date().isoformat()
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT task_name, status, started_at, duration_seconds, error_message
                FROM task_history 
                WHERE DATE(started_at) = ?
                ORDER BY started_at DESC
            """, (today,))
            return cursor.fetchall()

# ═══════════════════════════════════════════════════════════════════════════════
# TASK DEFINITIONS
# ═══════════════════════════════════════════════════════════════════════════════

tracker = TaskTracker(DB_PATH)

def run_task(task_name: str, task_func, *args, **kwargs) -> TaskResult:
    """Execute a task with tracking and error handling."""
    started_at = datetime.now()
    result = TaskResult(task_name=task_name, status=TaskStatus.RUNNING, started_at=started_at)
    
    logger.info(f"▶ Starting task: {task_name}")
    
    try:
        output = task_func(*args, **kwargs)
        result.status = TaskStatus.SUCCESS
        result.output_data = output if isinstance(output, dict) else {"result": str(output)}
        logger.info(f"✓ Task completed: {task_name}")
        
    except Exception as e:
        result.status = TaskStatus.FAILED
        result.error_message = str(e)
        logger.error(f"✗ Task failed: {task_name} - {e}")
        
    finally:
        result.completed_at = datetime.now()
        result.duration_seconds = (result.completed_at - started_at).total_seconds()
        tracker.log_task(result)
    
    return result

# ═══════════════════════════════════════════════════════════════════════════════
# DAILY TASKS - TÍCH HỢP VỚI CÁC MODULE HIỆN CÓ
# ═══════════════════════════════════════════════════════════════════════════════

def task_fetch_news():
    """Fetch latest TOPIK news - Sử dụng main.py generate_phase_1_news."""
    if MAIN_AVAILABLE:
        return generate_phase_1_news()
    else:
        raise ImportError("main.py không khả dụng")

def task_generate_content():
    """Generate daily content - Sử dụng run_full_pipeline từ main.py."""
    if MAIN_AVAILABLE:
        return run_full_pipeline()
    else:
        raise ImportError("main.py không khả dụng")

def task_generate_audio():
    """Generate TTS audio - Đã được tích hợp trong main.py process_all_assets."""
    if MAIN_AVAILABLE:
        return process_all_assets()
    else:
        raise ImportError("main.py không khả dụng")

def task_trigger_render():
    """Trigger video rendering on cloud (GitHub Actions)."""
    import requests
    
    github_token = os.getenv("GITHUB_TOKEN")
    repo = os.getenv("GITHUB_REPO", "user/topik-tiktok")
    
    if github_token:
        response = requests.post(
            f"https://api.github.com/repos/{repo}/dispatches",
            headers={
                "Authorization": f"token {github_token}",
                "Accept": "application/vnd.github.v3+json"
            },
            json={"event_type": "render-videos"}
        )
        
        if response.status_code == 204:
            return {"status": "triggered", "repo": repo}
        else:
            raise Exception(f"GitHub Actions trigger failed: {response.status_code}")
    else:
        raise ValueError("GITHUB_TOKEN không được cấu hình")

def task_download_videos():
    """Download rendered videos from cloud storage."""
    # Videos sẽ được tải về thư mục topik-video/out/ bởi GitHub Actions
    video_count = len(list(VIDEO_DIR.glob("*.mp4"))) if VIDEO_DIR.exists() else 0
    return {"video_count": video_count, "path": str(VIDEO_DIR)}

def task_upload_tiktok():
    """Upload videos to TikTok - Sử dụng social_publisher.py."""
    if SOCIAL_AVAILABLE:
        publisher = SocialMediaPublisher()
        # Load data
        if FINAL_DATA_PATH.exists():
            with open(FINAL_DATA_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
            return publisher.publish_to_tiktok(data)
        else:
            raise FileNotFoundError(f"Không tìm thấy {FINAL_DATA_PATH}")
    else:
        raise ImportError("social_publisher.py không khả dụng")

def task_upload_youtube():
    """Upload videos to YouTube - Sử dụng youtube_uploader.py."""
    if YOUTUBE_AVAILABLE:
        uploader = YouTubeUploader()
        uploader.authenticate()
        
        uploaded = []
        if VIDEO_DIR.exists():
            for video_file in VIDEO_DIR.glob("*.mp4"):
                if "deep" in video_file.name.lower():
                    result = upload_deep_dive_to_youtube(str(video_file))
                else:
                    result = upload_tiktok_to_youtube(str(video_file))
                uploaded.append({"file": video_file.name, "result": result})
        
        return {"uploaded": uploaded}
    else:
        raise ImportError("youtube_uploader.py không khả dụng")

def task_upload_facebook():
    """Upload videos to Facebook Reels - Sử dụng social_publisher.py."""
    if SOCIAL_AVAILABLE:
        publisher = SocialMediaPublisher()
        if FINAL_DATA_PATH.exists():
            with open(FINAL_DATA_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
            return publisher.publish_to_facebook(data)
        else:
            raise FileNotFoundError(f"Không tìm thấy {FINAL_DATA_PATH}")
    else:
        raise ImportError("social_publisher.py không khả dụng")

def task_generate_blog():
    """Generate and publish blog post - Sử dụng blog_generator.py."""
    if BLOG_AVAILABLE and GITHUB_AVAILABLE:
        if FINAL_DATA_PATH.exists():
            with open(FINAL_DATA_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            # Tạo blog
            generate_blog_from_data(data)
            
            # Deploy lên GitHub Pages
            deploy_blog_to_github()
            
            return {"status": "deployed"}
        else:
            raise FileNotFoundError(f"Không tìm thấy {FINAL_DATA_PATH}")
    else:
        raise ImportError("blog_generator.py hoặc github_deployer.py không khả dụng")

def task_generate_podcast():
    """Generate podcast episode - Sử dụng podcast_generator.py."""
    if PODCAST_AVAILABLE:
        if FINAL_DATA_PATH.exists():
            with open(FINAL_DATA_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
            return generate_podcast_from_data(data)
        else:
            raise FileNotFoundError(f"Không tìm thấy {FINAL_DATA_PATH}")
    else:
        raise ImportError("podcast_generator.py không khả dụng")

def task_post_telegram():
    """Post to Telegram channel - Sử dụng telegram_bot.py."""
    if TELEGRAM_AVAILABLE:
        return asyncio.run(send_daily_push())
    else:
        raise ImportError("telegram_bot.py không khả dụng")

def task_collect_analytics():
    """Collect analytics from all platforms - Sử dụng monetization.py."""
    if MONETIZATION_AVAILABLE:
        manager = MonetizationManager()
        return manager.get_all_revenue()
    else:
        raise ImportError("monetization.py không khả dụng")

def task_generate_report():
    """Generate daily performance report - Sử dụng monetization.py."""
    if MONETIZATION_AVAILABLE:
        manager = MonetizationManager()
        report = manager.generate_daily_report()
        
        # Lưu báo cáo
        report_path = LOG_DIR / f"report_{datetime.now().strftime('%Y-%m-%d')}.json"
        with open(report_path, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        return report
    else:
        raise ImportError("monetization.py không khả dụng")

def task_cleanup_old_files():
    """Clean up files older than 7 days to save disk space."""
    import shutil
    cutoff = datetime.now() - timedelta(days=7)
    cleaned = 0
    
    for date_dir in CONTENT_DIR.iterdir():
        if date_dir.is_dir():
            try:
                dir_date = datetime.strptime(date_dir.name, "%Y-%m-%d")
                if dir_date < cutoff:
                    shutil.rmtree(date_dir)
                    cleaned += 1
            except ValueError:
                pass
    
    return {"cleaned_directories": cleaned}

def task_health_check():
    """Check system health and notify if issues."""
    import psutil
    
    health = {
        "cpu_percent": psutil.cpu_percent(),
        "memory_percent": psutil.virtual_memory().percent,
        "disk_percent": psutil.disk_usage('/').percent,
        "status": "healthy"
    }
    
    # Alert if resources are critical
    if health["memory_percent"] > 90:
        health["status"] = "critical"
        logger.warning(f"⚠ Memory usage critical: {health['memory_percent']}%")
    elif health["disk_percent"] > 85:
        health["status"] = "warning"
        logger.warning(f"⚠ Disk usage high: {health['disk_percent']}%")
    
    return health

# ═══════════════════════════════════════════════════════════════════════════════
# PROFESSIONAL REVENUE TASKS - Các task kiếm tiền chuyên nghiệp
# ═══════════════════════════════════════════════════════════════════════════════

def task_send_daily_email():
    """Send daily email to subscribers - email_marketing.py."""
    if EMAIL_MARKETING_AVAILABLE:
        manager = EmailMarketingManager()
        if FINAL_DATA_PATH.exists():
            with open(FINAL_DATA_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
            return manager.send_daily_email(data)
        else:
            raise FileNotFoundError(f"Không tìm thấy {FINAL_DATA_PATH}")
    else:
        raise ImportError("email_marketing.py không khả dụng")

def task_generate_anki_deck():
    """Generate weekly Anki deck for sale - anki_generator.py."""
    if ANKI_AVAILABLE:
        generator = AnkiDeckGenerator()
        if FINAL_DATA_PATH.exists():
            with open(FINAL_DATA_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            vocab = data.get("vocabulary", [])
            grammar = data.get("grammar", [])
            
            # Generate daily deck (free) and premium deck (paid)
            daily_path = generator.generate_daily_deck(vocab[:10], grammar[:2])
            
            return {"daily_deck": daily_path}
        else:
            raise FileNotFoundError(f"Không tìm thấy {FINAL_DATA_PATH}")
    else:
        raise ImportError("anki_generator.py không khả dụng")

def task_optimize_seo():
    """Optimize blog SEO - seo_optimizer.py."""
    if SEO_AVAILABLE and BLOG_AVAILABLE:
        optimizer = SEOOptimizer()
        
        blog_dir = BASE_DIR / "blog" / "_posts"
        if blog_dir.exists():
            optimized = 0
            for post_file in blog_dir.glob("*.md"):
                with open(post_file, "r", encoding="utf-8") as f:
                    content = f.read()
                
                # Optimize content
                optimized_content = optimizer.optimize_content(content)
                
                with open(post_file, "w", encoding="utf-8") as f:
                    f.write(optimized_content)
                
                optimized += 1
            
            # Generate sitemap
            optimizer.generate_sitemap(str(blog_dir.parent))
            
            return {"optimized_posts": optimized}
        else:
            return {"optimized_posts": 0, "note": "Blog directory not found"}
    else:
        raise ImportError("seo_optimizer.py hoặc blog_generator.py không khả dụng")

def task_collect_platform_analytics():
    """Collect analytics from all platforms - analytics_dashboard.py."""
    if ANALYTICS_AVAILABLE:
        collector = PlatformCollector()
        
        # Collect from all platforms
        metrics = collector.collect_all()
        
        # Store in database
        db = AnalyticsDatabase()
        for platform, data in metrics.items():
            db.store_metrics(platform, data)
        
        return {"platforms_collected": list(metrics.keys())}
    else:
        raise ImportError("analytics_dashboard.py không khả dụng")

def task_generate_revenue_report():
    """Generate daily revenue report - analytics_dashboard.py."""
    if ANALYTICS_AVAILABLE:
        generator = ReportGenerator()
        report = generator.generate_daily_report()
        
        # Save report
        report_path = LOG_DIR / f"revenue_report_{datetime.now().strftime('%Y-%m-%d')}.md"
        with open(report_path, "w", encoding="utf-8") as f:
            f.write(report)
        
        return {"report_path": str(report_path)}
    else:
        raise ImportError("analytics_dashboard.py không khả dụng")

def task_update_affiliate_links():
    """Insert affiliate links into new content - affiliate_manager.py."""
    if AFFILIATE_AVAILABLE and BLOG_AVAILABLE:
        manager = AffiliateManager()
        
        blog_dir = BASE_DIR / "blog" / "_posts"
        if blog_dir.exists():
            updated = 0
            today = datetime.now().strftime("%Y-%m-%d")
            
            for post_file in blog_dir.glob(f"{today}*.md"):
                with open(post_file, "r", encoding="utf-8") as f:
                    content = f.read()
                
                # Check if already has affiliate section
                if "📚 Tài liệu đề xuất" not in content:
                    updated_content = manager.insert_affiliate_links(content)
                    
                    with open(post_file, "w", encoding="utf-8") as f:
                        f.write(updated_content)
                    
                    updated += 1
            
            return {"updated_posts": updated}
        else:
            return {"updated_posts": 0}
    else:
        raise ImportError("affiliate_manager.py hoặc blog_generator.py không khả dụng")

def task_post_community_daily():
    """Post daily content to Discord/Telegram community - community_manager.py."""
    if COMMUNITY_AVAILABLE:
        bot = CommunityBot()
        
        if FINAL_DATA_PATH.exists():
            with open(FINAL_DATA_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            daily_content = bot.get_daily_content(data)
            
            # Post to Telegram if available
            if TELEGRAM_AVAILABLE:
                from telegram_bot import send_message_to_channel
                asyncio.run(send_message_to_channel(daily_content))
            
            return {"content_posted": True}
        else:
            raise FileNotFoundError(f"Không tìm thấy {FINAL_DATA_PATH}")
    else:
        raise ImportError("community_manager.py không khả dụng")

def task_generate_weekly_anki():
    """Generate weekly premium Anki deck (Sundays) - anki_generator.py."""
    if ANKI_AVAILABLE:
        generator = AnkiDeckGenerator()
        
        # Collect content from the past week
        content_files = []
        for i in range(7):
            date = (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d")
            content_file = CONTENT_DIR / date / "final_data.json"
            if content_file.exists():
                content_files.append(str(content_file))
        
        if content_files:
            # Load all vocab and grammar
            all_vocab = []
            all_grammar = []
            
            for cf in content_files:
                with open(cf, "r", encoding="utf-8") as f:
                    data = json.load(f)
                all_vocab.extend(data.get("vocabulary", []))
                all_grammar.extend(data.get("grammar", []))
            
            # Generate premium deck
            premium_path = generator.generate_premium_deck(all_vocab, all_grammar)
            
            return {"premium_deck": premium_path, "vocab_count": len(all_vocab)}
        else:
            return {"premium_deck": None, "note": "No content files found"}
    else:
        raise ImportError("anki_generator.py không khả dụng")

# ═══════════════════════════════════════════════════════════════════════════════
# SCHEDULE CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════════

def setup_schedule():
    """Configure the daily schedule."""
    
    # Morning content pipeline (Vietnam timezone UTC+7)
    schedule.every().day.at("04:00").do(lambda: run_task("fetch_news", task_fetch_news))
    schedule.every().day.at("04:30").do(lambda: run_task("generate_content", task_generate_content))
    schedule.every().day.at("05:00").do(lambda: run_task("generate_audio", task_generate_audio))
    schedule.every().day.at("05:30").do(lambda: run_task("trigger_render", task_trigger_render))
    
    # Video download and upload
    schedule.every().day.at("07:00").do(lambda: run_task("download_videos", task_download_videos))
    schedule.every().day.at("07:30").do(lambda: run_task("upload_tiktok", task_upload_tiktok))
    schedule.every().day.at("08:00").do(lambda: run_task("upload_youtube", task_upload_youtube))
    schedule.every().day.at("08:30").do(lambda: run_task("upload_facebook", task_upload_facebook))
    
    # Content distribution
    schedule.every().day.at("09:00").do(lambda: run_task("generate_blog", task_generate_blog))
    schedule.every().day.at("09:30").do(lambda: run_task("generate_podcast", task_generate_podcast))
    schedule.every().day.at("10:00").do(lambda: run_task("post_telegram", task_post_telegram))
    
    # Professional revenue tasks - Các task kiếm tiền
    schedule.every().day.at("10:30").do(lambda: run_task("send_daily_email", task_send_daily_email))
    schedule.every().day.at("11:00").do(lambda: run_task("generate_anki_deck", task_generate_anki_deck))
    schedule.every().day.at("11:30").do(lambda: run_task("optimize_seo", task_optimize_seo))
    schedule.every().day.at("12:00").do(lambda: run_task("update_affiliate_links", task_update_affiliate_links))
    schedule.every().day.at("12:30").do(lambda: run_task("post_community_daily", task_post_community_daily))
    
    # Weekly premium content (Sunday only)
    schedule.every().sunday.at("14:00").do(lambda: run_task("generate_weekly_anki", task_generate_weekly_anki))
    
    # Evening analytics
    schedule.every().day.at("21:00").do(lambda: run_task("collect_platform_analytics", task_collect_platform_analytics))
    schedule.every().day.at("22:00").do(lambda: run_task("collect_analytics", task_collect_analytics))
    schedule.every().day.at("23:00").do(lambda: run_task("generate_report", task_generate_report))
    schedule.every().day.at("23:30").do(lambda: run_task("generate_revenue_report", task_generate_revenue_report))
    
    # Maintenance
    schedule.every().day.at("03:00").do(lambda: run_task("cleanup", task_cleanup_old_files))
    schedule.every().hour.do(lambda: run_task("health_check", task_health_check))
    
    logger.info("📅 Schedule configured successfully")
    logger.info("💰 Professional revenue tasks enabled: email, anki, seo, affiliate, community")

# ═══════════════════════════════════════════════════════════════════════════════
# MAIN ENTRY POINT
# ═══════════════════════════════════════════════════════════════════════════════

def run_now(task_name: str):
    """Run a specific task immediately."""
    tasks = {
        # Content pipeline
        "fetch_news": task_fetch_news,
        "generate_content": task_generate_content,
        "generate_audio": task_generate_audio,
        "trigger_render": task_trigger_render,
        "download_videos": task_download_videos,
        "upload_tiktok": task_upload_tiktok,
        "upload_youtube": task_upload_youtube,
        "upload_facebook": task_upload_facebook,
        "generate_blog": task_generate_blog,
        "generate_podcast": task_generate_podcast,
        "post_telegram": task_post_telegram,
        "collect_analytics": task_collect_analytics,
        "generate_report": task_generate_report,
        "cleanup": task_cleanup_old_files,
        "health_check": task_health_check,
        # Professional revenue tasks
        "send_daily_email": task_send_daily_email,
        "generate_anki_deck": task_generate_anki_deck,
        "optimize_seo": task_optimize_seo,
        "update_affiliate_links": task_update_affiliate_links,
        "post_community_daily": task_post_community_daily,
        "collect_platform_analytics": task_collect_platform_analytics,
        "generate_revenue_report": task_generate_revenue_report,
        "generate_weekly_anki": task_generate_weekly_anki,
    }
    
    if task_name in tasks:
        return run_task(task_name, tasks[task_name])
    elif task_name == "all":
        # Run full pipeline
        pipeline = [
            "fetch_news", "generate_content", "generate_audio", 
            "trigger_render", "download_videos", 
            "upload_tiktok", "upload_youtube", "upload_facebook",
            "generate_blog", "generate_podcast", "post_telegram"
        ]
        results = []
        for t in pipeline:
            result = run_task(t, tasks[t])
            results.append(result)
            if result.status == TaskStatus.FAILED:
                logger.error(f"Pipeline stopped at {t}")
                break
        return results
    else:
        logger.error(f"Unknown task: {task_name}")
        return None

def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="TOPIK Daily Automation Scheduler")
    parser.add_argument("--run", type=str, help="Run a specific task immediately")
    parser.add_argument("--daemon", action="store_true", help="Run as daemon with schedule")
    parser.add_argument("--status", action="store_true", help="Show today's task status")
    args = parser.parse_args()
    
    if args.run:
        result = run_now(args.run)
        if result:
            if isinstance(result, list):
                for r in result:
                    print(f"{r.task_name}: {r.status.value} ({r.duration_seconds:.1f}s)")
            else:
                print(f"{result.task_name}: {result.status.value} ({result.duration_seconds:.1f}s)")
    
    elif args.status:
        tasks = tracker.get_today_tasks()
        print("\n📊 Today's Task Status:")
        print("-" * 60)
        for task in tasks:
            status_icon = "✓" if task[1] == "success" else "✗" if task[1] == "failed" else "○"
            print(f"{status_icon} {task[0]:25} | {task[1]:8} | {task[3]:.1f}s")
        print("-" * 60)
    
    elif args.daemon:
        logger.info("🚀 Starting TOPIK Daily Scheduler in daemon mode...")
        setup_schedule()
        
        # Run health check on startup
        run_task("health_check", task_health_check)
        
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute
    
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
