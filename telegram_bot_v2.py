"""
================================================================================
TELEGRAM BOT — Interactive Korean Learning Bot (Professional Version)
================================================================================
Features:
    - Daily vocabulary push with persistence
    - Interactive quizzes with analytics
    - User progress tracking in SQLite
    - Premium content access
    - Scheduled daily notifications
    - Error recovery & graceful shutdown
================================================================================
"""

from __future__ import annotations

import os
import asyncio
import random
from datetime import datetime, timedelta
from typing import Dict, Optional, Any, List
from dataclasses import dataclass, field
from pathlib import Path
from contextlib import asynccontextmanager

# Core framework
from core import (
    Config, Logger, Database,
    safe_json_load, retry_with_backoff, truncate_text
)

# Initialize core components
config = Config()
logger = Logger(__name__)
db = Database()

# Try to import telegram library
try:
    from telegram import (
        Update, 
        InlineKeyboardButton, 
        InlineKeyboardMarkup, 
        Poll,
        Bot,
        Message
    )
    from telegram.ext import (
        Application, 
        CommandHandler, 
        CallbackQueryHandler,
        MessageHandler,
        PollAnswerHandler,
        filters,
        ContextTypes
    )
    from telegram.error import TelegramError, NetworkError, TimedOut
    TELEGRAM_BOT_AVAILABLE = True
except ImportError:
    TELEGRAM_BOT_AVAILABLE = False
    logger.warning("python-telegram-bot not installed. pip install python-telegram-bot")


# ==================== DATA CLASSES ====================

@dataclass
class UserStats:
    """User statistics for tracking progress"""
    user_id: int
    username: str = ""
    first_name: str = ""
    joined_at: str = ""
    quizzes_taken: int = 0
    correct_answers: int = 0
    current_streak: int = 0
    best_streak: int = 0
    last_active: str = ""
    is_premium: bool = False
    
    @property
    def accuracy(self) -> float:
        """Calculate accuracy percentage"""
        if self.quizzes_taken == 0:
            return 0.0
        return (self.correct_answers / self.quizzes_taken) * 100
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage"""
        return {
            "user_id": self.user_id,
            "username": self.username,
            "first_name": self.first_name,
            "joined_at": self.joined_at,
            "quizzes_taken": self.quizzes_taken,
            "correct_answers": self.correct_answers,
            "current_streak": self.current_streak,
            "best_streak": self.best_streak,
            "last_active": self.last_active,
            "is_premium": self.is_premium
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "UserStats":
        """Create from dictionary"""
        return cls(
            user_id=data.get("user_id", 0),
            username=data.get("username", ""),
            first_name=data.get("first_name", ""),
            joined_at=data.get("joined_at", ""),
            quizzes_taken=data.get("quizzes_taken", 0),
            correct_answers=data.get("correct_answers", 0),
            current_streak=data.get("current_streak", 0),
            best_streak=data.get("best_streak", 0),
            last_active=data.get("last_active", ""),
            is_premium=data.get("is_premium", False)
        )


@dataclass
class QuizData:
    """Quiz data structure"""
    poll_id: str
    user_id: int
    quiz_type: str  # "vocab" or "grammar"
    correct_index: int
    question: str
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())


# ==================== MESSAGE TEMPLATES ====================

MESSAGES = {
    "welcome": """
🇰🇷 **Xin chào {name}!**

Chào mừng bạn đến với **데일리 코리안 Bot**!

Tôi sẽ giúp bạn học tiếng Hàn mỗi ngày với:
📚 Từ vựng TOPIK
📝 Ngữ pháp nâng cao
🎯 Quiz tương tác
📰 Tin tức Hàn Quốc

**Các lệnh:**
• /today - Bài học hôm nay
• /vocab - Từ vựng ngẫu nhiên
• /quiz - Làm quiz
• /grammar - Ngữ pháp hôm nay
• /news - Tin tức Hàn Quốc
• /stats - Thống kê của bạn
• /premium - Nâng cấp Premium

Bắt đầu học thôi! 📖
""",
    
    "daily_lesson": """
📅 **TOPIK Daily - {date}**

📚 **Chủ đề:** {topic}

━━━━━━━━━━━━━━━━━━

📖 **Từ Vựng Hôm Nay:**
🔤 `{target_word}`

{explanation}

━━━━━━━━━━━━━━━━━━

📝 **Ngữ Pháp Hôm Nay:**
✏️ `{target_grammar}`

━━━━━━━━━━━━━━━━━━

Nhấn nút bên dưới để làm quiz! 👇
""",
    
    "vocab": """
📚 **Từ Vựng TOPIK**

🔤 **{word}**

{explanation}

━━━━━━━━━━━━━━━━━━

💡 Muốn học thêm? Dùng /vocab để xem từ khác!
""",
    
    "news": """
📰 **Tin Tức Hàn Quốc Hôm Nay**

🇰🇷 **Tiếng Hàn (쉬운 한국어):**

{news_kr}

━━━━━━━━━━━━━━━━━━

💡 Đọc chậm và tìm từ mới bạn chưa biết!
""",
    
    "essay": """
✍️ **Bài Văn Mẫu TOPIK 54**

{essay}

━━━━━━━━━━━━━━━━━━

📊 Xem phân tích chi tiết trên YouTube!
""",
    
    "stats": """
📊 **Thống Kê Của Bạn**

🎯 Quiz đã làm: {quizzes}
✅ Đúng: {correct}
📈 Tỷ lệ đúng: {accuracy:.1f}%
🔥 Streak hiện tại: {streak}
🏆 Streak tốt nhất: {best_streak}

━━━━━━━━━━━━━━━━━━

{motivation}
""",
    
    "premium": """
⭐ **데일리 코리안 Premium**

Nâng cấp để nhận:

✅ Từ vựng mở rộng (50+ từ/ngày)
✅ Bài tập thực hành
✅ Đáp án chi tiết
✅ PDF tải về
✅ Anki flashcards
✅ Không quảng cáo
✅ Hỗ trợ 1-1

💰 **Giá:** ${price}/tháng

━━━━━━━━━━━━━━━━━━

Liên hệ @topikdaily để đăng ký!
""",
    
    "daily_push": """
🌅 **Chào Buổi Sáng! - {date}**

📚 **Từ vựng hôm nay:** `{target_word}`

{explanation}

━━━━━━━━━━━━━━━━━━

🎯 Chat với @TOPIKDailyBot để làm quiz!

#TOPIK #Korean #한국어
""",
    
    "error": "❌ Xin lỗi, có lỗi xảy ra. Vui lòng thử lại sau.",
    
    "no_data": "❌ Không có dữ liệu hôm nay. Vui lòng thử lại sau.",
}

MOTIVATIONS = [
    "Tiếp tục cố gắng nhé! 화이팅! 💪",
    "Bạn đang làm rất tốt! 잘하고 있어요! 🌟",
    "Mỗi ngày một bước tiến! 조금씩 발전해요! 📈",
    "Đừng bỏ cuộc! 포기하지 마세요! 🔥",
    "Cố lên nào! 힘내세요! 💫"
]


# ==================== BOT CLASS ====================

class TOPIKBot:
    """
    Interactive Telegram bot for Korean learning.
    
    Features:
        - Interactive quizzes with progress tracking
        - Daily vocabulary and grammar lessons
        - User statistics with SQLite persistence
        - Premium subscription management
    """
    
    def __init__(self, token: Optional[str] = None):
        """
        Initialize the bot.
        
        Args:
            token: Telegram bot token (defaults to config value)
        """
        self.token = token or config.telegram.bot_token
        self.data: Dict[str, Any] = {}
        self.user_stats: Dict[int, UserStats] = {}
        self.quiz_answers: Dict[str, QuizData] = {}
        self.data_file = config.paths.data_file
        
        self._load_user_stats()
        logger.info("TOPIKBot initialized")
    
    def _load_user_stats(self):
        """Load user stats from database"""
        try:
            # Load from JSON file as backup
            stats_file = Path("data/user_stats.json")
            if stats_file.exists():
                data = safe_json_load(stats_file, {})
                for user_id, stats_dict in data.items():
                    self.user_stats[int(user_id)] = UserStats.from_dict(stats_dict)
                logger.info(f"Loaded {len(self.user_stats)} user stats")
        except Exception as e:
            logger.error(f"Failed to load user stats: {e}")
    
    def _save_user_stats(self):
        """Save user stats to file"""
        try:
            from core import safe_json_save, ensure_directory
            ensure_directory("data")
            
            data = {
                str(uid): stats.to_dict() 
                for uid, stats in self.user_stats.items()
            }
            safe_json_save(data, "data/user_stats.json")
        except Exception as e:
            logger.error(f"Failed to save user stats: {e}")
    
    def load_data(self) -> bool:
        """
        Load today's learning data from JSON file.
        
        Returns:
            True if data loaded successfully
        """
        self.data = safe_json_load(self.data_file, {})
        if self.data:
            logger.debug(f"Loaded data from {self.data_file}")
            return True
        else:
            logger.warning(f"Data file not found or empty: {self.data_file}")
            return False
    
    def _get_or_create_user(self, user) -> UserStats:
        """Get or create user stats"""
        user_id = user.id
        
        if user_id not in self.user_stats:
            self.user_stats[user_id] = UserStats(
                user_id=user_id,
                username=user.username or "",
                first_name=user.first_name or "",
                joined_at=datetime.now().isoformat()
            )
            logger.info(f"New user registered: {user_id}")
        
        # Update last active
        self.user_stats[user_id].last_active = datetime.now().isoformat()
        return self.user_stats[user_id]
    
    # ─── Command Handlers ────────────────────────────────────────────────────
    
    @logger.log_execution_time
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        user = update.effective_user
        user_stats = self._get_or_create_user(user)
        
        message = MESSAGES["welcome"].format(name=user.first_name)
        
        keyboard = [
            [
                InlineKeyboardButton("📚 Từ Vựng", callback_data="vocab"),
                InlineKeyboardButton("🎯 Quiz", callback_data="quiz")
            ],
            [
                InlineKeyboardButton("📖 Bài Học", callback_data="today"),
                InlineKeyboardButton("📰 Tin Tức", callback_data="news")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            message, 
            parse_mode="Markdown",
            reply_markup=reply_markup
        )
        
        # Log analytics
        db.log_analytics(
            event_type="bot_start",
            event_data={"user_id": user.id},
            user_id=str(user.id)
        )
    
    async def today(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Send today's lesson"""
        if not self.load_data():
            await self._send_message(update, MESSAGES["no_data"])
            return
        
        meta = self.data.get("meta", {})
        phase3 = self.data.get("phase3", {})
        
        topic = meta.get("topic_title_vi", "TOPIK Daily")
        
        vocab_quiz = phase3.get("video_3_vocab_quiz", {})
        target_word = vocab_quiz.get("target_word", "")
        explanation = truncate_text(vocab_quiz.get("explanation_vi", ""), 300)
        
        grammar_quiz = phase3.get("video_4_grammar_quiz", {})
        target_grammar = grammar_quiz.get("target_grammar", "")
        
        message = MESSAGES["daily_lesson"].format(
            date=datetime.now().strftime('%d/%m/%Y'),
            topic=topic,
            target_word=target_word,
            explanation=explanation,
            target_grammar=target_grammar
        )
        
        keyboard = [
            [
                InlineKeyboardButton("🎯 Quiz Từ Vựng", callback_data="quiz_vocab"),
                InlineKeyboardButton("📝 Quiz Ngữ Pháp", callback_data="quiz_grammar")
            ],
            [
                InlineKeyboardButton("📰 Xem Tin Tức", callback_data="news"),
                InlineKeyboardButton("✍️ Bài Văn Mẫu", callback_data="essay")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await self._send_message(update, message, reply_markup)
    
    async def send_vocab(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Send random vocabulary"""
        if not self.load_data():
            await self._send_message(update, MESSAGES["no_data"])
            return
        
        phase2 = self.data.get("phase2", {})
        analysis_list = phase2.get("analysis_list", [])
        
        if not analysis_list:
            await self._send_message(update, MESSAGES["no_data"])
            return
        
        vocab = random.choice(analysis_list)
        word = vocab.get("item", "")
        explanation = vocab.get("professor_explanation", "")
        
        message = MESSAGES["vocab"].format(word=word, explanation=explanation)
        
        keyboard = [[InlineKeyboardButton("🔄 Từ Khác", callback_data="vocab")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await self._send_message(update, message, reply_markup)
    
    async def send_quiz(
        self, 
        update: Update, 
        context: ContextTypes.DEFAULT_TYPE, 
        quiz_type: str = "vocab"
    ):
        """
        Send interactive quiz.
        
        Args:
            quiz_type: "vocab" or "grammar"
        """
        if not self.load_data():
            await self._send_message(update, MESSAGES["no_data"])
            return
        
        phase3 = self.data.get("phase3", {})
        
        if quiz_type == "vocab":
            quiz_data = phase3.get("video_3_vocab_quiz", {})
        else:
            quiz_data = phase3.get("video_4_grammar_quiz", {})
        
        if not quiz_data:
            await self._send_message(update, MESSAGES["no_data"])
            return
        
        # Get quiz content
        question = quiz_data.get("question_vi", quiz_data.get("question_ko", ""))
        options = quiz_data.get("options_vi", quiz_data.get("options_ko", []))
        correct = quiz_data.get("correct_answer", "A")
        explanation = truncate_text(quiz_data.get("explanation_vi", ""), 200)
        
        # Convert answer to index
        correct_index = ord(correct.upper()) - ord('A')
        
        # Clean options
        clean_options = []
        for opt in options:
            clean_opt = opt.strip()
            if clean_opt.startswith(("A.", "B.", "C.", "D.")):
                clean_opt = clean_opt[2:].strip()
            clean_options.append(clean_opt[:100])  # Telegram option limit
        
        # Send poll
        chat_id = update.effective_chat.id
        user_id = update.effective_user.id
        
        try:
            poll_message = await context.bot.send_poll(
                chat_id=chat_id,
                question=question[:300],
                options=clean_options[:4],
                type=Poll.QUIZ,
                correct_option_id=correct_index,
                explanation=explanation,
                is_anonymous=False
            )
            
            # Store quiz data
            self.quiz_answers[poll_message.poll.id] = QuizData(
                poll_id=poll_message.poll.id,
                user_id=user_id,
                quiz_type=quiz_type,
                correct_index=correct_index,
                question=question[:100]
            )
            
            logger.debug(f"Quiz sent to user {user_id}, type: {quiz_type}")
            
        except TelegramError as e:
            logger.error(f"Failed to send quiz: {e}")
            await self._send_message(update, MESSAGES["error"])
    
    async def handle_poll_answer(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle quiz answer"""
        answer = update.poll_answer
        poll_id = answer.poll_id
        user_id = answer.user.id
        selected = answer.option_ids[0] if answer.option_ids else -1
        
        quiz_info = self.quiz_answers.get(poll_id)
        if not quiz_info:
            return
        
        correct_index = quiz_info.correct_index
        
        # Update user stats
        user_stats = self._get_or_create_user(answer.user)
        user_stats.quizzes_taken += 1
        
        if selected == correct_index:
            user_stats.correct_answers += 1
            user_stats.current_streak += 1
            user_stats.best_streak = max(user_stats.best_streak, user_stats.current_streak)
        else:
            user_stats.current_streak = 0
        
        # Save stats
        self._save_user_stats()
        
        # Log analytics
        db.log_analytics(
            event_type="quiz_answer",
            event_data={
                "quiz_type": quiz_info.quiz_type,
                "correct": selected == correct_index
            },
            user_id=str(user_id)
        )
        
        logger.debug(f"User {user_id} answered quiz: {'correct' if selected == correct_index else 'wrong'}")
    
    async def send_news(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Send today's news"""
        if not self.load_data():
            await self._send_message(update, MESSAGES["no_data"])
            return
        
        phase1 = self.data.get("phase1", {})
        news_kr = phase1.get("news_summary_easy_kr", "")
        
        if not news_kr:
            await self._send_message(update, MESSAGES["no_data"])
            return
        
        message = MESSAGES["news"].format(news_kr=news_kr)
        await self._send_message(update, message)
    
    async def send_essay(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Send model essay"""
        if not self.load_data():
            await self._send_message(update, MESSAGES["no_data"])
            return
        
        phase2 = self.data.get("phase2", {})
        essay = truncate_text(phase2.get("essay", ""), 2000)
        
        if not essay:
            await self._send_message(update, MESSAGES["no_data"])
            return
        
        message = MESSAGES["essay"].format(essay=essay)
        await self._send_message(update, message)
    
    async def send_stats(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Send user statistics"""
        user = update.effective_user
        stats = self._get_or_create_user(user)
        
        motivation = random.choice(MOTIVATIONS)
        
        message = MESSAGES["stats"].format(
            quizzes=stats.quizzes_taken,
            correct=stats.correct_answers,
            accuracy=stats.accuracy,
            streak=stats.current_streak,
            best_streak=stats.best_streak,
            motivation=motivation
        )
        
        await update.message.reply_text(message, parse_mode="Markdown")
    
    async def send_premium_info(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Send premium subscription info"""
        message = MESSAGES["premium"].format(price=config.telegram.premium_price)
        
        keyboard = [
            [InlineKeyboardButton("💳 Đăng Ký Premium", url=config.telegram.patreon_url)],
            [InlineKeyboardButton("☕ Mua Cà Phê", url=config.telegram.kofi_url)]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            message, 
            parse_mode="Markdown",
            reply_markup=reply_markup
        )
    
    async def handle_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle button callbacks"""
        query = update.callback_query
        await query.answer()
        
        callback_map = {
            "vocab": self.send_vocab,
            "quiz": lambda u, c: self.send_quiz(u, c, "vocab"),
            "quiz_vocab": lambda u, c: self.send_quiz(u, c, "vocab"),
            "quiz_grammar": lambda u, c: self.send_quiz(u, c, "grammar"),
            "today": self.today,
            "news": self.send_news,
            "essay": self.send_essay,
        }
        
        handler = callback_map.get(query.data)
        if handler:
            await handler(update, context)
    
    async def handle_error(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle errors gracefully"""
        logger.error(f"Bot error: {context.error}", exc_info=context.error)
        
        if update and update.effective_message:
            try:
                await update.effective_message.reply_text(MESSAGES["error"])
            except:
                pass
    
    # ─── Helper Methods ──────────────────────────────────────────────────────
    
    async def _send_message(
        self, 
        update: Update, 
        text: str, 
        reply_markup: Optional[InlineKeyboardMarkup] = None
    ):
        """Send message helper that works with both commands and callbacks"""
        if update.callback_query:
            await update.callback_query.message.reply_text(
                text, 
                parse_mode="Markdown",
                reply_markup=reply_markup
            )
        else:
            await update.message.reply_text(
                text, 
                parse_mode="Markdown",
                reply_markup=reply_markup
            )
    
    # ─── Run Bot ─────────────────────────────────────────────────────────────
    
    def run(self):
        """Start the bot with proper error handling"""
        if not TELEGRAM_BOT_AVAILABLE:
            logger.error("python-telegram-bot not installed")
            return
        
        if not self.token:
            logger.error("TELEGRAM_BOT_TOKEN not set")
            return
        
        logger.info("Starting TOPIK Daily Bot...")
        
        # Create application with custom settings
        app = (
            Application.builder()
            .token(self.token)
            .read_timeout(30)
            .write_timeout(30)
            .connect_timeout(30)
            .build()
        )
        
        # Add command handlers
        app.add_handler(CommandHandler("start", self.start))
        app.add_handler(CommandHandler("today", self.today))
        app.add_handler(CommandHandler("vocab", self.send_vocab))
        app.add_handler(CommandHandler("quiz", lambda u, c: self.send_quiz(u, c, "vocab")))
        app.add_handler(CommandHandler("grammar", lambda u, c: self.send_quiz(u, c, "grammar")))
        app.add_handler(CommandHandler("news", self.send_news))
        app.add_handler(CommandHandler("stats", self.send_stats))
        app.add_handler(CommandHandler("premium", self.send_premium_info))
        
        # Add callback and poll handlers
        app.add_handler(CallbackQueryHandler(self.handle_callback))
        app.add_handler(PollAnswerHandler(self.handle_poll_answer))
        
        # Add error handler
        app.add_error_handler(self.handle_error)
        
        # Start polling
        logger.info("Bot is running. Press Ctrl+C to stop.")
        app.run_polling(
            allowed_updates=Update.ALL_TYPES,
            drop_pending_updates=True
        )


# ==================== SCHEDULED PUSH ====================

@retry_with_backoff(max_retries=3, base_delay=5.0)
async def send_daily_push(
    bot_token: str, 
    channel_id: str, 
    data_file: str
) -> bool:
    """
    Send daily lesson to channel (for scheduled tasks).
    
    Args:
        bot_token: Telegram bot token
        channel_id: Channel ID to send to
        data_file: Path to data JSON file
    
    Returns:
        True if message sent successfully
    """
    if not TELEGRAM_BOT_AVAILABLE:
        logger.error("python-telegram-bot not installed")
        return False
    
    data = safe_json_load(data_file, {})
    if not data:
        logger.error(f"Failed to load data from {data_file}")
        return False
    
    meta = data.get("meta", {})
    phase3 = data.get("phase3", {})
    
    vocab_quiz = phase3.get("video_3_vocab_quiz", {})
    target_word = vocab_quiz.get("target_word", "")
    explanation = truncate_text(vocab_quiz.get("explanation_vi", ""), 300)
    
    message = MESSAGES["daily_push"].format(
        date=datetime.now().strftime('%d/%m/%Y'),
        target_word=target_word,
        explanation=explanation
    )
    
    bot = Bot(token=bot_token)
    await bot.send_message(
        chat_id=channel_id,
        text=message,
        parse_mode="Markdown"
    )
    
    logger.info(f"Daily push sent to channel {channel_id}")
    
    # Log analytics
    db.log_analytics(
        event_type="daily_push",
        event_data={"channel_id": channel_id}
    )
    
    return True


# ==================== CLI ====================

def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="TOPIK Daily Telegram Bot")
    parser.add_argument("--run", action="store_true", help="Run the bot")
    parser.add_argument("--push", action="store_true", help="Send daily push to channel")
    parser.add_argument("--channel", type=str, help="Channel ID for push")
    parser.add_argument("--data", type=str, help="Data file path")
    
    args = parser.parse_args()
    
    if args.run:
        bot = TOPIKBot()
        bot.run()
    
    elif args.push:
        channel_id = args.channel or config.telegram.channel_id
        data_file = args.data or config.paths.data_file
        
        if not channel_id:
            logger.error("Channel ID not set. Use --channel or TELEGRAM_CHANNEL_ID env var")
            return
        
        asyncio.run(send_daily_push(
            config.telegram.bot_token,
            channel_id,
            data_file
        ))
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
