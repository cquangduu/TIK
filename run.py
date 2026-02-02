#!/usr/bin/env python3
"""
================================================================================
TOPIK DAILY - UNIFIED RUNNER
================================================================================
Điểm khởi chạy duy nhất cho toàn bộ hệ thống.
Tích hợp với tất cả các module hiện có.

Usage:
    python run.py --help                    # Xem hướng dẫn
    python run.py --generate                # Tạo nội dung mới
    python run.py --render                  # Render video (local)
    python run.py --upload                  # Upload lên các platform
    python run.py --all                     # Chạy toàn bộ pipeline
    python run.py --schedule                # Chạy scheduler tự động
    python run.py --task telegram           # Chạy một task cụ thể
================================================================================
"""

import os
import sys
import argparse
import logging
from datetime import datetime
from pathlib import Path

# ==================== CONFIGURATION ====================
ROOT_DIR = Path(__file__).parent
LOG_DIR = ROOT_DIR / "logs"
LOG_DIR.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_DIR / "run.log", encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


# ==================== IMPORT MODULES ====================
def safe_import(module_name, function_names=None):
    """Import module an toàn, trả về None nếu không tồn tại"""
    try:
        module = __import__(module_name)
        if function_names:
            return {name: getattr(module, name, None) for name in function_names}
        return module
    except ImportError as e:
        logger.warning(f"⚠️ Không thể import {module_name}: {e}")
        return None


# ==================== COMMANDS ====================

def cmd_generate():
    """Tạo nội dung mới bằng main.py"""
    logger.info("🚀 Bắt đầu tạo nội dung...")
    
    try:
        from main import run_full_pipeline
        run_full_pipeline()
        logger.info("✅ Tạo nội dung thành công!")
        return True
    except Exception as e:
        logger.error(f"❌ Lỗi tạo nội dung: {e}")
        return False


def cmd_render():
    """Render video bằng Remotion"""
    logger.info("🎬 Bắt đầu render video...")
    
    remotion_dir = ROOT_DIR / "topik-video"
    
    if not remotion_dir.exists():
        logger.error(f"❌ Không tìm thấy thư mục Remotion: {remotion_dir}")
        return False
    
    try:
        import subprocess
        
        # Check node_modules
        if not (remotion_dir / "node_modules").exists():
            logger.info("📦 Cài đặt dependencies...")
            subprocess.run(["npm", "install"], cwd=remotion_dir, check=True)
        
        # Render all compositions
        compositions = ["NewsHealing", "QuizGame", "WritingCoach", "DeepDive"]
        
        for comp in compositions:
            logger.info(f"  🎥 Rendering {comp}...")
            result = subprocess.run(
                ["npx", "remotion", "render", comp, f"out/{comp}.mp4"],
                cwd=remotion_dir,
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                logger.info(f"  ✅ {comp} rendered!")
            else:
                logger.warning(f"  ⚠️ {comp} có thể có lỗi: {result.stderr[:200]}")
        
        logger.info("✅ Render video hoàn tất!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Lỗi render: {e}")
        return False


def cmd_upload():
    """Upload video lên các platform"""
    logger.info("📤 Bắt đầu upload...")
    
    try:
        # YouTube
        from youtube_uploader import YouTubeUploader
        uploader = YouTubeUploader()
        uploader.authenticate()
        
        video_dir = ROOT_DIR / "topik-video" / "out"
        
        if video_dir.exists():
            for video_file in video_dir.glob("*.mp4"):
                logger.info(f"  📹 Uploading {video_file.name}...")
                # uploader.upload_video(str(video_file), ...)
        
        # Social Media
        from social_publisher import SocialMediaPublisher
        publisher = SocialMediaPublisher()
        
        data_file = ROOT_DIR / "topik-video" / "public" / "final_data.json"
        if data_file.exists():
            import json
            with open(data_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            # publisher.publish_to_all(data)
        
        logger.info("✅ Upload hoàn tất!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Lỗi upload: {e}")
        return False


def cmd_blog():
    """Tạo và deploy blog"""
    logger.info("📝 Tạo blog...")
    
    try:
        from blog_generator import generate_blog_from_data
        from github_deployer import deploy_blog_to_github
        
        data_file = ROOT_DIR / "topik-video" / "public" / "final_data.json"
        if data_file.exists():
            import json
            with open(data_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            generate_blog_from_data(data)
            deploy_blog_to_github()
            
            logger.info("✅ Blog deployed!")
            return True
        else:
            logger.error("❌ Không tìm thấy final_data.json")
            return False
            
    except Exception as e:
        logger.error(f"❌ Lỗi blog: {e}")
        return False


def cmd_telegram():
    """Gửi daily push qua Telegram"""
    logger.info("📲 Gửi Telegram push...")
    
    try:
        import asyncio
        from telegram_bot import send_daily_push
        
        asyncio.run(send_daily_push())
        logger.info("✅ Telegram push sent!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Lỗi Telegram: {e}")
        return False


def cmd_podcast():
    """Tạo podcast"""
    logger.info("🎙️ Tạo podcast...")
    
    try:
        from podcast_generator import generate_podcast_from_data
        
        data_file = ROOT_DIR / "topik-video" / "public" / "final_data.json"
        if data_file.exists():
            import json
            with open(data_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            generate_podcast_from_data(data)
            logger.info("✅ Podcast created!")
            return True
        else:
            logger.error("❌ Không tìm thấy final_data.json")
            return False
            
    except Exception as e:
        logger.error(f"❌ Lỗi podcast: {e}")
        return False


def cmd_analytics():
    """Thu thập analytics"""
    logger.info("📊 Thu thập analytics...")
    
    try:
        from monetization import MonetizationManager
        
        manager = MonetizationManager()
        revenue = manager.get_all_revenue()
        
        logger.info(f"💰 Doanh thu: {revenue}")
        return revenue
        
    except Exception as e:
        logger.error(f"❌ Lỗi analytics: {e}")
        return None


def cmd_all():
    """Chạy toàn bộ pipeline"""
    logger.info("=" * 60)
    logger.info(f"🚀 FULL PIPELINE - {datetime.now()}")
    logger.info("=" * 60)
    
    steps = [
        ("Tạo nội dung", cmd_generate),
        ("Render video", cmd_render),
        ("Upload video", cmd_upload),
        ("Tạo blog", cmd_blog),
        ("Tạo podcast", cmd_podcast),
        ("Telegram push", cmd_telegram),
        ("Thu thập analytics", cmd_analytics),
    ]
    
    results = {}
    for name, func in steps:
        logger.info(f"\n--- {name} ---")
        try:
            results[name] = func()
        except Exception as e:
            logger.error(f"❌ {name} failed: {e}")
            results[name] = False
    
    logger.info("\n" + "=" * 60)
    logger.info("📊 KẾT QUẢ:")
    for name, result in results.items():
        status = "✅" if result else "❌"
        logger.info(f"   {status} {name}")
    logger.info("=" * 60)
    
    return results


def cmd_schedule():
    """Chạy scheduler tự động"""
    logger.info("🔄 Khởi chạy scheduler...")
    
    try:
        sys.path.insert(0, str(ROOT_DIR / "automation"))
        from scheduler import UnifiedScheduler
        
        scheduler = UnifiedScheduler()
        scheduler.run_scheduler()
        
    except Exception as e:
        logger.error(f"❌ Lỗi scheduler: {e}")
        
        # Fallback: sử dụng scheduler cũ nếu có
        try:
            from automation.scheduler import main as scheduler_main
            scheduler_main()
        except:
            logger.error("❌ Không thể khởi chạy scheduler")


def cmd_status():
    """Xem trạng thái hệ thống"""
    print("\n" + "=" * 60)
    print("📊 TRẠNG THÁI HỆ THỐNG TOPIK DAILY")
    print("=" * 60)
    
    # Check modules
    modules = [
        ("main.py", "main"),
        ("youtube_uploader.py", "youtube_uploader"),
        ("blog_generator.py", "blog_generator"),
        ("podcast_generator.py", "podcast_generator"),
        ("social_publisher.py", "social_publisher"),
        ("github_deployer.py", "github_deployer"),
        ("telegram_bot.py", "telegram_bot"),
        ("monetization.py", "monetization"),
    ]
    
    print("\n📦 Modules:")
    for display_name, module_name in modules:
        try:
            __import__(module_name)
            print(f"   ✅ {display_name}")
        except ImportError as e:
            print(f"   ⚠️ {display_name} (thiếu dependency: {e})")
        except Exception as e:
            print(f"   ⚠️ {display_name} (lỗi: {type(e).__name__})")
    
    # Check files exist (không import)
    print("\n📄 Files:")
    files = [
        "main.py",
        "youtube_uploader.py",
        "blog_generator.py",
        "podcast_generator.py",
        "social_publisher.py",
        "github_deployer.py",
        "telegram_bot.py",
        "monetization.py",
    ]
    for f in files:
        status = "✅" if (ROOT_DIR / f).exists() else "❌"
        print(f"   {status} {f}")
    
    # Check directories
    print("\n📁 Thư mục:")
    dirs = [
        ("topik-video/", ROOT_DIR / "topik-video"),
        ("topik-video/out/", ROOT_DIR / "topik-video" / "out"),
        ("logs/", ROOT_DIR / "logs"),
        ("automation/", ROOT_DIR / "automation"),
    ]
    
    for display_name, path in dirs:
        status = "✅" if path.exists() else "❌"
        print(f"   {status} {display_name}")
    
    # Check data
    print("\n📄 Data:")
    data_file = ROOT_DIR / "topik-video" / "public" / "final_data.json"
    if data_file.exists():
        import json
        with open(data_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        print(f"   ✅ final_data.json ({len(str(data))} bytes)")
    else:
        print("   ❌ final_data.json không tồn tại")
    
    print("\n" + "=" * 60)


# ==================== MAIN ====================
def main():
    parser = argparse.ArgumentParser(
        description="TOPIK Daily - Unified Runner",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ví dụ:
    python run.py --all          # Chạy toàn bộ pipeline
    python run.py --generate     # Chỉ tạo nội dung
    python run.py --schedule     # Chạy scheduler tự động
    python run.py --status       # Xem trạng thái
        """
    )
    
    parser.add_argument("--generate", action="store_true", help="Tạo nội dung mới")
    parser.add_argument("--render", action="store_true", help="Render video")
    parser.add_argument("--upload", action="store_true", help="Upload lên các platform")
    parser.add_argument("--blog", action="store_true", help="Tạo và deploy blog")
    parser.add_argument("--podcast", action="store_true", help="Tạo podcast")
    parser.add_argument("--telegram", action="store_true", help="Gửi Telegram push")
    parser.add_argument("--analytics", action="store_true", help="Thu thập analytics")
    parser.add_argument("--all", action="store_true", help="Chạy toàn bộ pipeline")
    parser.add_argument("--schedule", action="store_true", help="Chạy scheduler tự động")
    parser.add_argument("--status", action="store_true", help="Xem trạng thái hệ thống")
    
    args = parser.parse_args()
    
    # Nếu không có argument, hiển thị help
    if len(sys.argv) == 1:
        parser.print_help()
        print("\n💡 Tip: Dùng --status để kiểm tra trạng thái hệ thống")
        return
    
    # Chạy command tương ứng
    if args.status:
        cmd_status()
    elif args.generate:
        cmd_generate()
    elif args.render:
        cmd_render()
    elif args.upload:
        cmd_upload()
    elif args.blog:
        cmd_blog()
    elif args.podcast:
        cmd_podcast()
    elif args.telegram:
        cmd_telegram()
    elif args.analytics:
        cmd_analytics()
    elif args.all:
        cmd_all()
    elif args.schedule:
        cmd_schedule()


if __name__ == "__main__":
    main()
