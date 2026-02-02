"""
================================================================================
COMMUNITY MANAGER — Discord & Telegram Community Automation
================================================================================
Brand: DAILY KOREAN (데일리 코리안)
Features:
    1. Auto-welcome new members
    2. DAILY KOREAN tips in chat
    3. Answer FAQs automatically
    4. Track engagement metrics
    5. Manage premium members
================================================================================
Revenue Potential: $100-500/month (premium community memberships)
================================================================================
"""

import os
import json
import logging
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from pathlib import Path

# ==================== CONFIGURATION ====================
COMMUNITY_DIR = Path("community_data")
COMMUNITY_DIR.mkdir(exist_ok=True)

DB_PATH = COMMUNITY_DIR / "community.db"


# ==================== TEMPLATES ====================

WELCOME_MESSAGES = {
    "en": """
🎉 **Welcome to TOPIK Daily Community!**

Hello {name}! We're excited to have you here! 👋

📚 **Getting Started:**
1. Introduce yourself in #introductions
2. Check out #daily-korean for daily tips
3. Ask questions in #questions

💡 **Pro tip:** React to the daily posts to track your streak!

화이팅! 💪
""",
    "vi": """
🎉 **Chào mừng đến với TOPIK Daily Community!**

Xin chào {name}! Rất vui được gặp bạn! 👋

📚 **Bắt đầu nào:**
1. Giới thiệu bản thân ở #introductions
2. Theo dõi #daily-korean để học mỗi ngày
3. Đặt câu hỏi ở #questions

💡 **Mẹo:** React vào bài đăng hàng ngày để theo dõi streak!

화이팅! 💪
""",
    "ko": """
🎉 **TOPIK Daily 커뮤니티에 오신 것을 환영합니다!**

안녕하세요 {name}님! 만나서 반갑습니다! 👋

📚 **시작하기:**
1. #introductions에서 자기소개를 해주세요
2. #daily-korean에서 매일 팁을 확인하세요
3. #questions에서 질문해주세요

💡 **팁:** 매일 포스트에 리액션을 달아 스트릭을 기록하세요!

화이팅! 💪
"""
}

DAILY_TIP_TEMPLATES = [
    """
📝 **오늘의 단어 (Word of the Day)**

**{korean}** ({romanization})
📖 {meaning}
✍️ {example_ko}
🔊 {example_vi}

React với ✅ nếu bạn đã học từ này!
""",
    """
📗 **오늘의 문법 (Grammar of the Day)**

**{pattern}**
📖 {meaning}
✍️ Ví dụ: {example}

Bình luận với câu ví dụ của riêng bạn! 💬
""",
    """
🎧 **Listening Challenge**

Nghe audio và trả lời câu hỏi:
{question}

Đáp án sẽ được công bố sau 24h!
"""
]

FAQ_RESPONSES = {
    "topik_date": """
📅 **Lịch thi TOPIK 2024-2025:**

- TOPIK 88: 13/04/2024
- TOPIK 89: 12/05/2024
- TOPIK 90: 14/07/2024
- TOPIK 91: 13/10/2024
- TOPIK 92: 16/11/2024
- TOPIK 93: 12/01/2025

🔗 Đăng ký tại: topik.go.kr
""",
    "how_to_study": """
📚 **Cách học tiếng Hàn hiệu quả:**

1. **Hangul trước** - 1-2 tuần đầu
2. **Từ vựng cơ bản** - 500 từ đầu tiên
3. **Ngữ pháp cơ bản** - 50 cấu trúc
4. **Luyện nghe nói** - Mỗi ngày 30 phút
5. **Đọc hiểu** - Bắt đầu từ webtoon, bài hát

💡 Mẹo: Consistency > Intensity
""",
    "free_resources": """
📖 **Tài liệu miễn phí:**

1. **TOPIK Daily** - topikdaily.com
2. **Talk To Me In Korean** - talktomeinkorean.com
3. **How To Study Korean** - howtostudykorean.com
4. **Korean Class 101** - koreanclass101.com
5. **Billy Go Korean** - YouTube

🎥 Xem thêm video tại kênh YouTube của chúng tôi!
"""
}


class CommunityDatabase:
    """SQLite database for community management"""
    
    def __init__(self, db_path: str = str(DB_PATH)):
        self.db_path = db_path
        self.init_db()
    
    def init_db(self):
        """Initialize database tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Members table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS members (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                platform TEXT NOT NULL,
                platform_id TEXT NOT NULL,
                username TEXT,
                display_name TEXT,
                language TEXT DEFAULT 'vi',
                is_premium BOOLEAN DEFAULT 0,
                joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                streak_days INTEGER DEFAULT 0,
                total_points INTEGER DEFAULT 0,
                UNIQUE(platform, platform_id)
            )
        """)
        
        # Activity log
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS activity_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                member_id INTEGER,
                activity_type TEXT,
                details TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (member_id) REFERENCES members(id)
            )
        """)
        
        # Premium subscriptions
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS subscriptions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                member_id INTEGER,
                plan TEXT,
                amount REAL,
                currency TEXT DEFAULT 'USD',
                started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP,
                is_active BOOLEAN DEFAULT 1,
                FOREIGN KEY (member_id) REFERENCES members(id)
            )
        """)
        
        conn.commit()
        conn.close()
    
    def add_member(self, platform: str, platform_id: str, username: str = None, 
                   display_name: str = None, language: str = "vi") -> int:
        """Add or update member"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO members (platform, platform_id, username, display_name, language)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(platform, platform_id) DO UPDATE SET
                username = excluded.username,
                display_name = excluded.display_name,
                last_active = CURRENT_TIMESTAMP
        """, (platform, platform_id, username, display_name, language))
        
        member_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return member_id
    
    def log_activity(self, member_id: int, activity_type: str, details: str = None):
        """Log member activity"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO activity_log (member_id, activity_type, details)
            VALUES (?, ?, ?)
        """, (member_id, activity_type, details))
        
        conn.commit()
        conn.close()
    
    def update_streak(self, member_id: int):
        """Update member streak"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Check if active yesterday
        cursor.execute("""
            SELECT last_active FROM members WHERE id = ?
        """, (member_id,))
        row = cursor.fetchone()
        
        if row:
            last_active = datetime.fromisoformat(row[0]) if row[0] else None
            yesterday = datetime.now() - timedelta(days=1)
            
            if last_active and last_active.date() >= yesterday.date():
                # Continue streak
                cursor.execute("""
                    UPDATE members SET streak_days = streak_days + 1, last_active = CURRENT_TIMESTAMP
                    WHERE id = ?
                """, (member_id,))
            else:
                # Reset streak
                cursor.execute("""
                    UPDATE members SET streak_days = 1, last_active = CURRENT_TIMESTAMP
                    WHERE id = ?
                """, (member_id,))
        
        conn.commit()
        conn.close()
    
    def add_points(self, member_id: int, points: int):
        """Add points to member"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE members SET total_points = total_points + ?
            WHERE id = ?
        """, (points, member_id))
        
        conn.commit()
        conn.close()
    
    def get_leaderboard(self, limit: int = 10) -> List[Dict]:
        """Get leaderboard"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT display_name, username, total_points, streak_days
            FROM members
            ORDER BY total_points DESC
            LIMIT ?
        """, (limit,))
        
        results = []
        for row in cursor.fetchall():
            results.append({
                "name": row[0] or row[1] or "Unknown",
                "points": row[2],
                "streak": row[3],
            })
        
        conn.close()
        return results
    
    def get_stats(self) -> Dict:
        """Get community stats"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Total members
        cursor.execute("SELECT COUNT(*) FROM members")
        total_members = cursor.fetchone()[0]
        
        # Premium members
        cursor.execute("SELECT COUNT(*) FROM members WHERE is_premium = 1")
        premium_members = cursor.fetchone()[0]
        
        # Active today
        today = datetime.now().date().isoformat()
        cursor.execute("""
            SELECT COUNT(*) FROM members 
            WHERE date(last_active) = ?
        """, (today,))
        active_today = cursor.fetchone()[0]
        
        # New this week
        week_ago = (datetime.now() - timedelta(days=7)).isoformat()
        cursor.execute("""
            SELECT COUNT(*) FROM members 
            WHERE joined_at >= ?
        """, (week_ago,))
        new_this_week = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            "total_members": total_members,
            "premium_members": premium_members,
            "active_today": active_today,
            "new_this_week": new_this_week,
        }


class CommunityBot:
    """Bot for Discord/Telegram community management"""
    
    def __init__(self):
        self.db = CommunityDatabase()
    
    def handle_new_member(self, platform: str, user_id: str, username: str = None, 
                          display_name: str = None, language: str = "vi") -> str:
        """Handle new member join"""
        
        # Add to database
        member_id = self.db.add_member(platform, user_id, username, display_name, language)
        
        # Log activity
        self.db.log_activity(member_id, "join", f"Joined from {platform}")
        
        # Get welcome message
        welcome = WELCOME_MESSAGES.get(language, WELCOME_MESSAGES["vi"])
        name = display_name or username or "bạn"
        
        return welcome.format(name=name)
    
    def handle_message(self, platform: str, user_id: str, message: str) -> Optional[str]:
        """Handle user message, return response if applicable"""
        
        message_lower = message.lower()
        
        # Check for FAQ triggers
        if any(word in message_lower for word in ["thi topik", "lịch thi", "ngày thi", "topik date"]):
            return FAQ_RESPONSES["topik_date"]
        
        if any(word in message_lower for word in ["học thế nào", "cách học", "how to study", "bắt đầu"]):
            return FAQ_RESPONSES["how_to_study"]
        
        if any(word in message_lower for word in ["tài liệu", "free", "miễn phí", "resources"]):
            return FAQ_RESPONSES["free_resources"]
        
        # Update activity
        member_id = self.db.add_member(platform, user_id)
        self.db.log_activity(member_id, "message", message[:100])
        
        return None
    
    def handle_reaction(self, platform: str, user_id: str, emoji: str):
        """Handle reaction to daily content"""
        
        member_id = self.db.add_member(platform, user_id)
        
        # Award points
        if emoji in ["✅", "👍", "💪"]:
            self.db.add_points(member_id, 10)
            self.db.update_streak(member_id)
            self.db.log_activity(member_id, "reaction", emoji)
    
    def get_daily_content(self, content_data: Dict) -> str:
        """Generate daily content post"""
        
        if not content_data:
            return ""
        
        # Get vocabulary
        vocab = content_data.get("vocabulary", [])
        if vocab:
            word = vocab[0]
            template = DAILY_TIP_TEMPLATES[0]
            return template.format(
                korean=word.get("korean", ""),
                romanization=word.get("romanization", ""),
                meaning=word.get("meaning", ""),
                example_ko=word.get("example_ko", ""),
                example_vi=word.get("example_vi", ""),
            )
        
        # Get grammar
        grammar = content_data.get("grammar", [])
        if grammar:
            g = grammar[0]
            template = DAILY_TIP_TEMPLATES[1]
            return template.format(
                pattern=g.get("pattern", ""),
                meaning=g.get("meaning", ""),
                example=g.get("example1_ko", ""),
            )
        
        return ""
    
    def get_leaderboard_message(self) -> str:
        """Generate leaderboard message"""
        
        leaderboard = self.db.get_leaderboard(10)
        
        message = "🏆 **Bảng xếp hạng tuần này**\n\n"
        
        medals = ["🥇", "🥈", "🥉"]
        for i, member in enumerate(leaderboard):
            prefix = medals[i] if i < 3 else f"{i+1}."
            streak_emoji = "🔥" if member["streak"] >= 7 else ""
            message += f"{prefix} **{member['name']}** - {member['points']} điểm {streak_emoji}\n"
        
        message += "\n💡 Tham gia daily challenges để kiếm điểm!"
        
        return message


class PremiumManager:
    """Manage premium memberships"""
    
    PLANS = {
        "monthly": {"name": "Monthly", "price": 4.99, "duration_days": 30},
        "yearly": {"name": "Yearly", "price": 39.99, "duration_days": 365},
        "lifetime": {"name": "Lifetime", "price": 99.99, "duration_days": 36500},
    }
    
    def __init__(self):
        self.db = CommunityDatabase()
    
    def add_subscription(self, member_id: int, plan: str) -> bool:
        """Add premium subscription"""
        
        if plan not in self.PLANS:
            return False
        
        plan_info = self.PLANS[plan]
        
        conn = sqlite3.connect(self.db.db_path)
        cursor = conn.cursor()
        
        expires_at = (datetime.now() + timedelta(days=plan_info["duration_days"])).isoformat()
        
        cursor.execute("""
            INSERT INTO subscriptions (member_id, plan, amount, expires_at)
            VALUES (?, ?, ?, ?)
        """, (member_id, plan, plan_info["price"], expires_at))
        
        # Update member status
        cursor.execute("""
            UPDATE members SET is_premium = 1 WHERE id = ?
        """, (member_id,))
        
        conn.commit()
        conn.close()
        
        return True
    
    def check_subscription(self, member_id: int) -> Dict:
        """Check subscription status"""
        
        conn = sqlite3.connect(self.db.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT plan, expires_at, is_active
            FROM subscriptions
            WHERE member_id = ? AND is_active = 1
            ORDER BY expires_at DESC
            LIMIT 1
        """, (member_id,))
        
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            return {"is_premium": False}
        
        expires_at = datetime.fromisoformat(row[1])
        is_expired = expires_at < datetime.now()
        
        return {
            "is_premium": not is_expired,
            "plan": row[0],
            "expires_at": row[1],
            "days_remaining": (expires_at - datetime.now()).days if not is_expired else 0,
        }
    
    def get_premium_benefits(self) -> str:
        """Get premium benefits message"""
        
        return """
👑 **TOPIK Daily Premium**

**Quyền lợi Premium:**

✅ Truy cập tất cả nội dung premium
✅ Không quảng cáo
✅ Anki decks hàng tuần
✅ PDF workbooks
✅ Q&A priority với giáo viên
✅ Badge đặc biệt trong community
✅ Early access tính năng mới

**Bảng giá:**
- Monthly: $4.99/tháng
- Yearly: $39.99/năm (tiết kiệm 33%!)
- Lifetime: $99.99 (một lần duy nhất)

🔗 Đăng ký: topikdaily.com/premium
"""


# ==================== UTILITY FUNCTIONS ====================

def get_community_stats() -> Dict:
    """Get community statistics"""
    db = CommunityDatabase()
    return db.get_stats()


def generate_weekly_report() -> str:
    """Generate weekly community report"""
    
    db = CommunityDatabase()
    stats = db.get_stats()
    leaderboard = db.get_leaderboard(5)
    
    report = f"""
# 📊 Community Report - Tuần này

**Ngày tạo:** {datetime.now().strftime('%Y-%m-%d')}

---

## 👥 Thành viên

| Metric | Số lượng |
|--------|----------|
| Tổng thành viên | {stats['total_members']:,} |
| Premium members | {stats['premium_members']:,} |
| Active hôm nay | {stats['active_today']:,} |
| Thành viên mới tuần này | {stats['new_this_week']:,} |

---

## 🏆 Top 5 tuần này

"""
    for i, member in enumerate(leaderboard, 1):
        report += f"{i}. {member['name']} - {member['points']} points (🔥 {member['streak']} ngày streak)\n"
    
    report += """

---

## 💡 Đề xuất

1. Tổ chức event cuối tuần
2. Thêm mini-games
3. Live Q&A session

---

화이팅! 💪
"""
    return report


# ==================== MAIN ====================

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Community Manager")
    parser.add_argument("--stats", action="store_true", help="Show community stats")
    parser.add_argument("--leaderboard", action="store_true", help="Show leaderboard")
    parser.add_argument("--report", action="store_true", help="Generate weekly report")
    parser.add_argument("--benefits", action="store_true", help="Show premium benefits")
    
    args = parser.parse_args()
    
    if args.stats:
        stats = get_community_stats()
        print(json.dumps(stats, indent=2))
    elif args.leaderboard:
        bot = CommunityBot()
        print(bot.get_leaderboard_message())
    elif args.report:
        print(generate_weekly_report())
    elif args.benefits:
        manager = PremiumManager()
        print(manager.get_premium_benefits())
    else:
        parser.print_help()
