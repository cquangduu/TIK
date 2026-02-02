"""
================================================================================
DAILY KOREAN — Database Management
================================================================================
SQLite database for analytics, user tracking, and content management.
================================================================================
"""

import sqlite3
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from contextlib import contextmanager
from dataclasses import dataclass, asdict

# ==================== CONFIGURATION ====================
DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)
DB_PATH = DATA_DIR / "dailykorean.db"


@dataclass
class ContentRecord:
    """Content generation record"""
    id: Optional[int] = None
    date: str = ""
    topic_ko: str = ""
    topic_vi: str = ""
    news_url: str = ""
    status: str = "pending"  # pending, generated, published
    data_json: str = ""
    created_at: str = ""
    published_at: Optional[str] = None


@dataclass
class VideoRecord:
    """Video render/upload record"""
    id: Optional[int] = None
    content_id: int = 0
    video_type: str = ""  # news, writing, vocab_quiz, grammar_quiz, deep_dive
    platform: str = ""    # tiktok, youtube
    local_path: str = ""
    upload_url: str = ""
    video_id: str = ""
    status: str = "pending"  # pending, rendered, uploaded, published
    duration_sec: float = 0.0
    created_at: str = ""
    uploaded_at: Optional[str] = None


@dataclass  
class AnalyticsRecord:
    """Platform analytics record"""
    id: Optional[int] = None
    platform: str = ""
    date: str = ""
    followers: int = 0
    views: int = 0
    likes: int = 0
    comments: int = 0
    shares: int = 0
    revenue: float = 0.0
    engagement_rate: float = 0.0
    created_at: str = ""


@dataclass
class SubscriberRecord:
    """Email/Telegram subscriber record"""
    id: Optional[int] = None
    platform: str = ""  # email, telegram, discord
    user_id: str = ""
    name: str = ""
    email: str = ""
    is_premium: bool = False
    joined_at: str = ""
    last_active: str = ""
    preferences: str = "{}"  # JSON


class Database:
    """Professional SQLite database manager"""
    
    def __init__(self, db_path: Path = DB_PATH):
        self.db_path = db_path
        self._init_db()
    
    @contextmanager
    def get_connection(self):
        """Context manager for database connections"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()
    
    def _init_db(self):
        """Initialize database tables"""
        with self.get_connection() as conn:
            # Content table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS content (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date TEXT NOT NULL UNIQUE,
                    topic_ko TEXT,
                    topic_vi TEXT,
                    news_url TEXT,
                    status TEXT DEFAULT 'pending',
                    data_json TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    published_at TIMESTAMP
                )
            """)
            
            # Videos table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS videos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    content_id INTEGER,
                    video_type TEXT NOT NULL,
                    platform TEXT NOT NULL,
                    local_path TEXT,
                    upload_url TEXT,
                    video_id TEXT,
                    status TEXT DEFAULT 'pending',
                    duration_sec REAL DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    uploaded_at TIMESTAMP,
                    FOREIGN KEY (content_id) REFERENCES content(id)
                )
            """)
            
            # Analytics table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS analytics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    platform TEXT NOT NULL,
                    date TEXT NOT NULL,
                    followers INTEGER DEFAULT 0,
                    views INTEGER DEFAULT 0,
                    likes INTEGER DEFAULT 0,
                    comments INTEGER DEFAULT 0,
                    shares INTEGER DEFAULT 0,
                    revenue REAL DEFAULT 0,
                    engagement_rate REAL DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(platform, date)
                )
            """)
            
            # Subscribers table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS subscribers (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    platform TEXT NOT NULL,
                    user_id TEXT NOT NULL,
                    name TEXT,
                    email TEXT,
                    is_premium INTEGER DEFAULT 0,
                    joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_active TIMESTAMP,
                    preferences TEXT DEFAULT '{}',
                    UNIQUE(platform, user_id)
                )
            """)
            
            # Revenue table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS revenue (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date TEXT NOT NULL,
                    source TEXT NOT NULL,
                    amount REAL NOT NULL,
                    currency TEXT DEFAULT 'USD',
                    description TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create indexes
            conn.execute("CREATE INDEX IF NOT EXISTS idx_content_date ON content(date)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_videos_content ON videos(content_id)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_analytics_date ON analytics(date)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_revenue_date ON revenue(date)")
    
    # ─── Content Methods ─────────────────────────────────────────────────────
    
    def save_content(self, record: ContentRecord) -> int:
        """Save or update content record"""
        with self.get_connection() as conn:
            if record.id:
                conn.execute("""
                    UPDATE content SET 
                        topic_ko=?, topic_vi=?, news_url=?, status=?, 
                        data_json=?, published_at=?
                    WHERE id=?
                """, (record.topic_ko, record.topic_vi, record.news_url,
                      record.status, record.data_json, record.published_at, record.id))
                return record.id
            else:
                cursor = conn.execute("""
                    INSERT OR REPLACE INTO content 
                    (date, topic_ko, topic_vi, news_url, status, data_json)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (record.date, record.topic_ko, record.topic_vi,
                      record.news_url, record.status, record.data_json))
                return cursor.lastrowid
    
    def get_content_by_date(self, date: str) -> Optional[ContentRecord]:
        """Get content for a specific date"""
        with self.get_connection() as conn:
            row = conn.execute(
                "SELECT * FROM content WHERE date=?", (date,)
            ).fetchone()
            
            if row:
                return ContentRecord(**dict(row))
            return None
    
    def get_recent_content(self, days: int = 7) -> List[ContentRecord]:
        """Get recent content records"""
        with self.get_connection() as conn:
            rows = conn.execute("""
                SELECT * FROM content 
                ORDER BY date DESC 
                LIMIT ?
            """, (days,)).fetchall()
            
            return [ContentRecord(**dict(row)) for row in rows]
    
    # ─── Video Methods ───────────────────────────────────────────────────────
    
    def save_video(self, record: VideoRecord) -> int:
        """Save video record"""
        with self.get_connection() as conn:
            if record.id:
                conn.execute("""
                    UPDATE videos SET 
                        status=?, upload_url=?, video_id=?, uploaded_at=?
                    WHERE id=?
                """, (record.status, record.upload_url, record.video_id,
                      record.uploaded_at, record.id))
                return record.id
            else:
                cursor = conn.execute("""
                    INSERT INTO videos 
                    (content_id, video_type, platform, local_path, status, duration_sec)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (record.content_id, record.video_type, record.platform,
                      record.local_path, record.status, record.duration_sec))
                return cursor.lastrowid
    
    def get_videos_by_content(self, content_id: int) -> List[VideoRecord]:
        """Get all videos for a content record"""
        with self.get_connection() as conn:
            rows = conn.execute(
                "SELECT * FROM videos WHERE content_id=?", (content_id,)
            ).fetchall()
            
            return [VideoRecord(**dict(row)) for row in rows]
    
    # ─── Analytics Methods ───────────────────────────────────────────────────
    
    def save_analytics(self, record: AnalyticsRecord):
        """Save analytics record"""
        with self.get_connection() as conn:
            conn.execute("""
                INSERT OR REPLACE INTO analytics 
                (platform, date, followers, views, likes, comments, shares, revenue, engagement_rate)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (record.platform, record.date, record.followers, record.views,
                  record.likes, record.comments, record.shares, 
                  record.revenue, record.engagement_rate))
    
    def get_analytics_summary(self, days: int = 30) -> Dict[str, Any]:
        """Get analytics summary across all platforms"""
        with self.get_connection() as conn:
            rows = conn.execute("""
                SELECT 
                    platform,
                    SUM(views) as total_views,
                    SUM(likes) as total_likes,
                    SUM(comments) as total_comments,
                    SUM(revenue) as total_revenue,
                    MAX(followers) as current_followers
                FROM analytics
                WHERE date >= date('now', ?)
                GROUP BY platform
            """, (f'-{days} days',)).fetchall()
            
            return {row['platform']: dict(row) for row in rows}
    
    # ─── Subscriber Methods ──────────────────────────────────────────────────
    
    def add_subscriber(self, record: SubscriberRecord) -> int:
        """Add or update subscriber"""
        with self.get_connection() as conn:
            cursor = conn.execute("""
                INSERT OR REPLACE INTO subscribers 
                (platform, user_id, name, email, is_premium, preferences)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (record.platform, record.user_id, record.name, record.email,
                  1 if record.is_premium else 0, record.preferences))
            return cursor.lastrowid
    
    def get_subscriber_count(self) -> Dict[str, int]:
        """Get subscriber count by platform"""
        with self.get_connection() as conn:
            rows = conn.execute("""
                SELECT platform, COUNT(*) as count
                FROM subscribers
                GROUP BY platform
            """).fetchall()
            
            return {row['platform']: row['count'] for row in rows}
    
    def get_premium_subscribers(self) -> List[SubscriberRecord]:
        """Get all premium subscribers"""
        with self.get_connection() as conn:
            rows = conn.execute(
                "SELECT * FROM subscribers WHERE is_premium=1"
            ).fetchall()
            
            return [SubscriberRecord(**dict(row)) for row in rows]
    
    # ─── Revenue Methods ─────────────────────────────────────────────────────
    
    def add_revenue(self, date: str, source: str, amount: float, 
                    currency: str = "USD", description: str = ""):
        """Add revenue entry"""
        with self.get_connection() as conn:
            conn.execute("""
                INSERT INTO revenue (date, source, amount, currency, description)
                VALUES (?, ?, ?, ?, ?)
            """, (date, source, amount, currency, description))
    
    def get_revenue_summary(self, days: int = 30) -> Dict[str, float]:
        """Get revenue summary by source"""
        with self.get_connection() as conn:
            rows = conn.execute("""
                SELECT source, SUM(amount) as total
                FROM revenue
                WHERE date >= date('now', ?)
                GROUP BY source
            """, (f'-{days} days',)).fetchall()
            
            return {row['source']: row['total'] for row in rows}
    
    def get_total_revenue(self, days: int = 30) -> float:
        """Get total revenue"""
        with self.get_connection() as conn:
            row = conn.execute("""
                SELECT SUM(amount) as total
                FROM revenue
                WHERE date >= date('now', ?)
            """, (f'-{days} days',)).fetchone()
            
            return row['total'] or 0.0


# Singleton instance
_db: Optional[Database] = None


def get_db() -> Database:
    """Get or create database singleton"""
    global _db
    if _db is None:
        _db = Database()
    return _db
