"""
================================================================================
TELEGRAM BOT — Interactive Korean Learning Bot
================================================================================
Features:
    - Daily vocabulary push
    - Interactive quizzes
    - Answer questions
    - Premium content access
    - Revenue: Tips, Premium subscription
================================================================================
"""

import os
import json
import logging
import asyncio
from datetime import datetime
from typing import Dict, Optional
from dotenv import load_dotenv

load_dotenv()

# Try to import telegram library
try:
    from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, Poll
    from telegram.ext import (
        Application, 
        CommandHandler, 
        CallbackQueryHandler,
        MessageHandler,
        PollAnswerHandler,
        filters,
        ContextTypes
    )
    TELEGRAM_BOT_AVAILABLE = True
except ImportError:
    TELEGRAM_BOT_AVAILABLE = False
    logging.warning("⚠️ python-telegram-bot not installed. pip install python-telegram-bot")

# ==================== CONFIGURATION ====================
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
ADMIN_CHAT_ID = os.getenv("TELEGRAM_ADMIN_ID", "")
DATA_FILE = os.getenv("TELEGRAM_DATA_FILE", "topik-video/public/final_data.json")

# Premium features
PREMIUM_PRICE = 5.00  # USD per month
PAYMENT_PROVIDER_TOKEN = os.getenv("TELEGRAM_PAYMENT_TOKEN", "")


class TOPIKBot:
    """Interactive Telegram bot for Korean learning"""
    
    def __init__(self, token: str = BOT_TOKEN):
        self.token = token
        self.data = {}
        self.user_stats = {}  # Track user progress
        self.quiz_answers = {}  # Track quiz answers
        
    def load_data(self, filepath: str = DATA_FILE):
        """Load today's learning data"""
        if os.path.exists(filepath):
            with open(filepath, "r", encoding="utf-8") as f:
                self.data = json.load(f)
            logging.info(f"✅ Loaded data from {filepath}")
        else:
            logging.warning(f"⚠️ Data file not found: {filepath}")
    
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        user = update.effective_user
        
        welcome_message = f"""
🇰🇷 **Xin chào {user.first_name}!**

Chào mừng bạn đến với **TOPIK Daily Bot**!

Tôi sẽ giúp bạn học tiếng Hàn mỗi ngày với:
📚 Từ vựng TOPIK
📝 Ngữ pháp nâng cao
🎯 Quiz tương tác
📰 Tin tức Hàn Quốc

**Các lệnh:**
/today - Bài học hôm nay
/vocab - Từ vựng ngẫu nhiên
/quiz - Làm quiz
/grammar - Ngữ pháp hôm nay
/news - Tin tức Hàn Quốc
/stats - Thống kê của bạn
/premium - Nâng cấp Premium

Bắt đầu học thôi! 📖
"""
        
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
            welcome_message, 
            parse_mode="Markdown",
            reply_markup=reply_markup
        )
        
        # Track user
        self.user_stats[user.id] = self.user_stats.get(user.id, {
            "joined": datetime.now().isoformat(),
            "quizzes_taken": 0,
            "correct_answers": 0,
            "streak": 0
        })
    
    async def today(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Send today's lesson"""
        self.load_data()
        
        meta = self.data.get("meta", {})
        phase1 = self.data.get("phase1", {})
        phase3 = self.data.get("phase3", {})
        
        topic = meta.get("topic_title_vi", "TOPIK Daily")
        
        # Get vocab
        vocab_quiz = phase3.get("video_3_vocab_quiz", {})
        target_word = vocab_quiz.get("target_word", "")
        explanation = vocab_quiz.get("explanation_vi", "")[:300]
        
        # Get grammar
        grammar_quiz = phase3.get("video_4_grammar_quiz", {})
        target_grammar = grammar_quiz.get("target_grammar", "")
        
        message = f"""
📅 **TOPIK Daily - {datetime.now().strftime('%d/%m/%Y')}**

📚 **Chủ đề:** {topic}

━━━━━━━━━━━━━━━━

📖 **Từ Vựng Hôm Nay:**
🔤 `{target_word}`

{explanation}

━━━━━━━━━━━━━━━━

📝 **Ngữ Pháp Hôm Nay:**
✏️ `{target_grammar}`

━━━━━━━━━━━━━━━━

Nhấn nút bên dưới để làm quiz! 👇
"""
        
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
        
        if update.callback_query:
            await update.callback_query.message.reply_text(
                message, 
                parse_mode="Markdown",
                reply_markup=reply_markup
            )
        else:
            await update.message.reply_text(
                message, 
                parse_mode="Markdown",
                reply_markup=reply_markup
            )
    
    async def send_vocab(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Send random vocabulary"""
        self.load_data()
        
        phase2 = self.data.get("phase2", {})
        analysis_list = phase2.get("analysis_list", [])
        
        if not analysis_list:
            await update.message.reply_text("❌ Không có từ vựng hôm nay.")
            return
        
        import random
        vocab = random.choice(analysis_list)
        
        word = vocab.get("item", "")
        explanation = vocab.get("professor_explanation", "")
        
        message = f"""
📚 **Từ Vựng TOPIK**

🔤 **{word}**

{explanation}

━━━━━━━━━━━━━━━━

💡 Muốn học thêm? Dùng /vocab để xem từ khác!
"""
        
        keyboard = [
            [InlineKeyboardButton("🔄 Từ Khác", callback_data="vocab")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        if update.callback_query:
            await update.callback_query.message.reply_text(
                message, 
                parse_mode="Markdown",
                reply_markup=reply_markup
            )
        else:
            await update.message.reply_text(
                message, 
                parse_mode="Markdown",
                reply_markup=reply_markup
            )
    
    async def send_quiz(self, update: Update, context: ContextTypes.DEFAULT_TYPE, quiz_type: str = "vocab"):
        """Send interactive quiz"""
        self.load_data()
        
        phase3 = self.data.get("phase3", {})
        
        if quiz_type == "vocab":
            quiz_data = phase3.get("video_3_vocab_quiz", {})
        else:
            quiz_data = phase3.get("video_4_grammar_quiz", {})
        
        if not quiz_data:
            await update.message.reply_text("❌ Không có quiz hôm nay.")
            return
        
        question = quiz_data.get("question_vi", quiz_data.get("question_ko", ""))
        options = quiz_data.get("options_vi", quiz_data.get("options_ko", []))
        correct = quiz_data.get("correct_answer", "A")
        
        # Convert answer to index (A=0, B=1, C=2, D=3)
        correct_index = ord(correct.upper()) - ord('A')
        
        # Clean options (remove A., B., etc.)
        clean_options = []
        for opt in options:
            clean_opt = opt.strip()
            if clean_opt.startswith(("A.", "B.", "C.", "D.")):
                clean_opt = clean_opt[2:].strip()
            clean_options.append(clean_opt)
        
        # Send as Telegram Poll
        chat_id = update.effective_chat.id
        user_id = update.effective_user.id
        
        poll_message = await context.bot.send_poll(
            chat_id=chat_id,
            question=question[:300],  # Telegram limit
            options=clean_options[:4],  # Max 4 options
            type=Poll.QUIZ,
            correct_option_id=correct_index,
            explanation=quiz_data.get("explanation_vi", "")[:200],
            is_anonymous=False
        )
        
        # Store quiz data for tracking
        self.quiz_answers[poll_message.poll.id] = {
            "correct_index": correct_index,
            "user_id": user_id,
            "type": quiz_type
        }
    
    async def handle_poll_answer(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle quiz answer"""
        answer = update.poll_answer
        poll_id = answer.poll_id
        user_id = answer.user.id
        selected = answer.option_ids[0] if answer.option_ids else -1
        
        quiz_info = self.quiz_answers.get(poll_id, {})
        correct_index = quiz_info.get("correct_index", -1)
        
        # Update user stats
        if user_id not in self.user_stats:
            self.user_stats[user_id] = {
                "quizzes_taken": 0,
                "correct_answers": 0,
                "streak": 0
            }
        
        self.user_stats[user_id]["quizzes_taken"] += 1
        
        if selected == correct_index:
            self.user_stats[user_id]["correct_answers"] += 1
            self.user_stats[user_id]["streak"] += 1
        else:
            self.user_stats[user_id]["streak"] = 0
    
    async def send_news(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Send today's news"""
        self.load_data()
        
        phase1 = self.data.get("phase1", {})
        news_kr = phase1.get("news_summary_easy_kr", "")
        
        message = f"""
📰 **Tin Tức Hàn Quốc Hôm Nay**

🇰🇷 **Tiếng Hàn (쉬운 한국어):**

{news_kr}

━━━━━━━━━━━━━━━━

💡 Đọc chậm và tìm từ mới bạn chưa biết!
"""
        
        if update.callback_query:
            await update.callback_query.message.reply_text(message, parse_mode="Markdown")
        else:
            await update.message.reply_text(message, parse_mode="Markdown")
    
    async def send_essay(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Send model essay"""
        self.load_data()
        
        phase2 = self.data.get("phase2", {})
        essay = phase2.get("essay", "")[:2000]  # Telegram limit
        
        message = f"""
✍️ **Bài Văn Mẫu TOPIK 54**

{essay}

━━━━━━━━━━━━━━━━

📊 Xem phân tích chi tiết trên YouTube!
"""
        
        if update.callback_query:
            await update.callback_query.message.reply_text(message, parse_mode="Markdown")
        else:
            await update.message.reply_text(message, parse_mode="Markdown")
    
    async def send_stats(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Send user statistics"""
        user_id = update.effective_user.id
        stats = self.user_stats.get(user_id, {
            "quizzes_taken": 0,
            "correct_answers": 0,
            "streak": 0
        })
        
        quizzes = stats.get("quizzes_taken", 0)
        correct = stats.get("correct_answers", 0)
        streak = stats.get("streak", 0)
        accuracy = (correct / quizzes * 100) if quizzes > 0 else 0
        
        message = f"""
📊 **Thống Kê Của Bạn**

🎯 Quiz đã làm: {quizzes}
✅ Đúng: {correct}
📈 Tỷ lệ đúng: {accuracy:.1f}%
🔥 Streak hiện tại: {streak}

━━━━━━━━━━━━━━━━

Tiếp tục cố gắng nhé! 화이팅! 💪
"""
        
        await update.message.reply_text(message, parse_mode="Markdown")
    
    async def send_premium_info(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Send premium subscription info"""
        message = f"""
⭐ **TOPIK Daily Premium**

Nâng cấp để nhận:

✅ Từ vựng mở rộng (50+ từ/ngày)
✅ Bài tập thực hành
✅ Đáp án chi tiết
✅ PDF tải về
✅ Anki flashcards
✅ Không quảng cáo
✅ Hỗ trợ 1-1

💰 **Giá:** ${PREMIUM_PRICE}/tháng

━━━━━━━━━━━━━━━━

Liên hệ @topikdaily để đăng ký!
"""
        
        keyboard = [
            [InlineKeyboardButton("💳 Đăng Ký Premium", url="https://patreon.com/topikdaily")],
            [InlineKeyboardButton("☕ Mua Cà Phê", url="https://ko-fi.com/topikdaily")]
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
        
        data = query.data
        
        if data == "vocab":
            await self.send_vocab(update, context)
        elif data == "quiz" or data == "quiz_vocab":
            await self.send_quiz(update, context, "vocab")
        elif data == "quiz_grammar":
            await self.send_quiz(update, context, "grammar")
        elif data == "today":
            await self.today(update, context)
        elif data == "news":
            await self.send_news(update, context)
        elif data == "essay":
            await self.send_essay(update, context)
    
    def run(self):
        """Start the bot"""
        if not TELEGRAM_BOT_AVAILABLE:
            logging.error("❌ python-telegram-bot not installed")
            return
        
        if not self.token:
            logging.error("❌ TELEGRAM_BOT_TOKEN not set")
            return
        
        logging.info("🤖 Starting TOPIK Daily Bot...")
        
        # Create application
        app = Application.builder().token(self.token).build()
        
        # Add handlers
        app.add_handler(CommandHandler("start", self.start))
        app.add_handler(CommandHandler("today", self.today))
        app.add_handler(CommandHandler("vocab", self.send_vocab))
        app.add_handler(CommandHandler("quiz", lambda u, c: self.send_quiz(u, c, "vocab")))
        app.add_handler(CommandHandler("grammar", lambda u, c: self.send_quiz(u, c, "grammar")))
        app.add_handler(CommandHandler("news", self.send_news))
        app.add_handler(CommandHandler("stats", self.send_stats))
        app.add_handler(CommandHandler("premium", self.send_premium_info))
        
        app.add_handler(CallbackQueryHandler(self.handle_callback))
        app.add_handler(PollAnswerHandler(self.handle_poll_answer))
        
        # Start polling
        app.run_polling(allowed_updates=Update.ALL_TYPES)


# ==================== SCHEDULED PUSH ====================

async def send_daily_push(bot_token: str, channel_id: str, data_file: str):
    """Send daily lesson to channel (called from cron)"""
    if not TELEGRAM_BOT_AVAILABLE:
        return
    
    from telegram import Bot
    
    bot = Bot(token=bot_token)
    
    # Load data
    with open(data_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    meta = data.get("meta", {})
    phase1 = data.get("phase1", {})
    phase3 = data.get("phase3", {})
    
    topic = meta.get("topic_title_vi", "TOPIK Daily")
    
    vocab_quiz = phase3.get("video_3_vocab_quiz", {})
    target_word = vocab_quiz.get("target_word", "")
    explanation = vocab_quiz.get("explanation_vi", "")[:300]
    
    message = f"""
🌅 **Chào Buổi Sáng! - {datetime.now().strftime('%d/%m/%Y')}**

📚 **Từ vựng hôm nay:** `{target_word}`

{explanation}

━━━━━━━━━━━━━━━━

🎯 Chat với @TOPIKDailyBot để làm quiz!

#TOPIK #Korean #한국어
"""
    
    await bot.send_message(
        chat_id=channel_id,
        text=message,
        parse_mode="Markdown"
    )


# ==================== CLI ====================
if __name__ == "__main__":
    import argparse
    
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s"
    )
    
    parser = argparse.ArgumentParser(description="TOPIK Daily Telegram Bot")
    parser.add_argument("--run", action="store_true", help="Run the bot")
    parser.add_argument("--push", action="store_true", help="Send daily push to channel")
    
    args = parser.parse_args()
    
    if args.run:
        bot = TOPIKBot()
        bot.run()
    elif args.push:
        channel_id = os.getenv("TELEGRAM_CHANNEL_ID", "")
        if channel_id:
            asyncio.run(send_daily_push(BOT_TOKEN, channel_id, DATA_FILE))
        else:
            print("❌ TELEGRAM_CHANNEL_ID not set")
    else:
        print("Use --run to start bot or --push to send daily message")
