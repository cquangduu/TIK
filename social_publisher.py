"""
================================================================================
SOCIAL MEDIA PUBLISHER — Auto Post to Multiple Platforms
================================================================================
Features:
    - Twitter/X: Post threads with Korean learning content
    - Telegram: Send to channel with formatted messages
    - Email Newsletter: Send daily digest via SMTP
    - Discord: Webhook integration
================================================================================
"""

import os
import json
import logging
import requests
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from typing import Dict, List, Optional
from dotenv import load_dotenv

load_dotenv()

# ==================== CONFIGURATION ====================

# Twitter/X
TWITTER_API_KEY = os.getenv("TWITTER_API_KEY", "")
TWITTER_API_SECRET = os.getenv("TWITTER_API_SECRET", "")
TWITTER_ACCESS_TOKEN = os.getenv("TWITTER_ACCESS_TOKEN", "")
TWITTER_ACCESS_SECRET = os.getenv("TWITTER_ACCESS_SECRET", "")
TWITTER_BEARER_TOKEN = os.getenv("TWITTER_BEARER_TOKEN", "")

# Telegram
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHANNEL_ID = os.getenv("TELEGRAM_CHANNEL_ID", "")  # e.g., @topikdaily

# Discord
DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL", "")

# Email
EMAIL_SMTP_SERVER = os.getenv("EMAIL_SMTP_SERVER", "smtp.gmail.com")
EMAIL_SMTP_PORT = int(os.getenv("EMAIL_SMTP_PORT", "587"))
EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS", "")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD", "")
EMAIL_SUBSCRIBER_LIST = os.getenv("EMAIL_SUBSCRIBER_LIST", "")  # comma-separated


# ==================== TWITTER/X ====================

class TwitterPublisher:
    """Publish to Twitter/X using v2 API"""
    
    def __init__(self):
        self.bearer_token = TWITTER_BEARER_TOKEN
        self.api_url = "https://api.twitter.com/2/tweets"
        
    def is_available(self) -> bool:
        return bool(self.bearer_token)
    
    def post_tweet(self, text: str, reply_to: str = None) -> Optional[str]:
        """Post a single tweet"""
        if not self.is_available():
            logging.warning("⚠️ Twitter not configured")
            return None
        
        headers = {
            "Authorization": f"Bearer {self.bearer_token}",
            "Content-Type": "application/json"
        }
        
        payload = {"text": text[:280]}  # Twitter limit
        
        if reply_to:
            payload["reply"] = {"in_reply_to_tweet_id": reply_to}
        
        try:
            response = requests.post(self.api_url, headers=headers, json=payload)
            if response.status_code == 201:
                tweet_id = response.json()["data"]["id"]
                logging.info(f"✅ Tweet posted: {tweet_id}")
                return tweet_id
            else:
                logging.error(f"❌ Twitter error: {response.status_code} - {response.text}")
                return None
        except Exception as e:
            logging.error(f"❌ Twitter error: {e}")
            return None
    
    def post_thread(self, tweets: List[str]) -> List[str]:
        """Post a thread of tweets"""
        tweet_ids = []
        reply_to = None
        
        for tweet in tweets:
            tweet_id = self.post_tweet(tweet, reply_to)
            if tweet_id:
                tweet_ids.append(tweet_id)
                reply_to = tweet_id
            else:
                break
        
        return tweet_ids
    
    def create_topik_thread(self, data: Dict) -> List[str]:
        """Create a TOPIK learning thread from data"""
        meta = data.get("meta", {})
        phase1 = data.get("phase1", {})
        phase2 = data.get("phase2", {})
        phase3 = data.get("phase3", {})
        
        topic = meta.get("topic_title_vi", "TOPIK Daily")
        
        tweets = []
        
        # Tweet 1: Introduction
        tweets.append(f"""🇰🇷 TOPIK Daily - {datetime.now().strftime('%d/%m/%Y')}

📚 Chủ đề: {topic}

Hôm nay học gì nhé? 👇

#TOPIK #LearnKorean #한국어 #Korean""")
        
        # Tweet 2: Vocabulary
        vocab_quiz = phase3.get("video_3_vocab_quiz", {})
        target_word = vocab_quiz.get("target_word", "")
        explanation = vocab_quiz.get("explanation_vi", "")[:200]
        
        if target_word:
            tweets.append(f"""📖 Từ vựng hôm nay:

🔤 {target_word}

{explanation}

#TOPIK #Vocabulary""")
        
        # Tweet 3: Grammar
        grammar_quiz = phase3.get("video_4_grammar_quiz", {})
        target_grammar = grammar_quiz.get("target_grammar", "")
        grammar_exp = grammar_quiz.get("explanation_vi", "")[:200]
        
        if target_grammar:
            tweets.append(f"""📝 Ngữ pháp hôm nay:

✏️ {target_grammar}

{grammar_exp}

#TOPIK #Grammar""")
        
        # Tweet 4: CTA
        tweets.append(f"""🎬 Xem video đầy đủ:

📺 YouTube: youtube.com/@topikdaily
📱 TikTok: tiktok.com/@topikdaily
🎧 Podcast: Spotify

Theo dõi để học tiếng Hàn mỗi ngày! 🙌

#TOPIK #Korean #Learning""")
        
        return tweets


# ==================== TELEGRAM ====================

class TelegramPublisher:
    """Publish to Telegram channel"""
    
    def __init__(self):
        self.bot_token = TELEGRAM_BOT_TOKEN
        self.channel_id = TELEGRAM_CHANNEL_ID
        self.api_url = f"https://api.telegram.org/bot{self.bot_token}"
    
    def is_available(self) -> bool:
        return bool(self.bot_token and self.channel_id)
    
    def send_message(self, text: str, parse_mode: str = "HTML") -> bool:
        """Send message to Telegram channel"""
        if not self.is_available():
            logging.warning("⚠️ Telegram not configured")
            return False
        
        url = f"{self.api_url}/sendMessage"
        payload = {
            "chat_id": self.channel_id,
            "text": text,
            "parse_mode": parse_mode,
            "disable_web_page_preview": False
        }
        
        try:
            response = requests.post(url, json=payload)
            if response.status_code == 200:
                logging.info("✅ Telegram message sent")
                return True
            else:
                logging.error(f"❌ Telegram error: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            logging.error(f"❌ Telegram error: {e}")
            return False
    
    def send_photo(self, photo_url: str, caption: str = "") -> bool:
        """Send photo to Telegram channel"""
        if not self.is_available():
            return False
        
        url = f"{self.api_url}/sendPhoto"
        payload = {
            "chat_id": self.channel_id,
            "photo": photo_url,
            "caption": caption[:1024],
            "parse_mode": "HTML"
        }
        
        try:
            response = requests.post(url, json=payload)
            return response.status_code == 200
        except Exception as e:
            logging.error(f"❌ Telegram photo error: {e}")
            return False
    
    def create_topik_message(self, data: Dict) -> str:
        """Create formatted Telegram message from TOPIK data"""
        meta = data.get("meta", {})
        phase1 = data.get("phase1", {})
        phase2 = data.get("phase2", {})
        phase3 = data.get("phase3", {})
        
        topic = meta.get("topic_title_vi", "TOPIK Daily")
        news_kr = phase1.get("news_summary_easy_kr", "")[:500]
        
        # Get quiz info
        vocab_quiz = phase3.get("video_3_vocab_quiz", {})
        target_word = vocab_quiz.get("target_word", "")
        word_meaning = vocab_quiz.get("explanation_vi", "")[:300]
        
        grammar_quiz = phase3.get("video_4_grammar_quiz", {})
        target_grammar = grammar_quiz.get("target_grammar", "")
        
        message = f"""🇰🇷 <b>TOPIK Daily - {datetime.now().strftime('%d/%m/%Y')}</b>

📚 <b>Chủ đề:</b> {topic}

━━━━━━━━━━━━━━━━

📰 <b>Tin Tức Hàn Quốc:</b>
<i>{news_kr}</i>

━━━━━━━━━━━━━━━━

📖 <b>Từ Vựng Hôm Nay:</b>
🔤 <code>{target_word}</code>
{word_meaning}

━━━━━━━━━━━━━━━━

📝 <b>Ngữ Pháp Hôm Nay:</b>
✏️ <code>{target_grammar}</code>

━━━━━━━━━━━━━━━━

🎬 <b>Xem Video:</b>
📺 <a href="https://youtube.com/@topikdaily">YouTube</a>
📱 <a href="https://tiktok.com/@topikdaily">TikTok</a>
🎧 <a href="https://spotify.com">Podcast</a>
🌐 <a href="https://topikdaily.com">Blog</a>

#TOPIK #Korean #한국어 #Learning"""
        
        return message


# ==================== DISCORD ====================

class DiscordPublisher:
    """Publish to Discord via webhook"""
    
    def __init__(self):
        self.webhook_url = DISCORD_WEBHOOK_URL
    
    def is_available(self) -> bool:
        return bool(self.webhook_url)
    
    def send_embed(self, title: str, description: str, color: int = 0x1a73e8, fields: List[Dict] = None) -> bool:
        """Send embed message to Discord"""
        if not self.is_available():
            logging.warning("⚠️ Discord not configured")
            return False
        
        embed = {
            "title": title,
            "description": description,
            "color": color,
            "timestamp": datetime.utcnow().isoformat(),
            "footer": {"text": "TOPIK Daily"}
        }
        
        if fields:
            embed["fields"] = fields
        
        payload = {"embeds": [embed]}
        
        try:
            response = requests.post(self.webhook_url, json=payload)
            if response.status_code in [200, 204]:
                logging.info("✅ Discord message sent")
                return True
            else:
                logging.error(f"❌ Discord error: {response.status_code}")
                return False
        except Exception as e:
            logging.error(f"❌ Discord error: {e}")
            return False
    
    def create_topik_embed(self, data: Dict) -> bool:
        """Create and send TOPIK embed to Discord"""
        meta = data.get("meta", {})
        phase1 = data.get("phase1", {})
        phase3 = data.get("phase3", {})
        
        topic = meta.get("topic_title_vi", "TOPIK Daily")
        
        vocab_quiz = phase3.get("video_3_vocab_quiz", {})
        target_word = vocab_quiz.get("target_word", "")
        
        grammar_quiz = phase3.get("video_4_grammar_quiz", {})
        target_grammar = grammar_quiz.get("target_grammar", "")
        
        fields = [
            {"name": "📖 Từ Vựng", "value": f"`{target_word}`", "inline": True},
            {"name": "📝 Ngữ Pháp", "value": f"`{target_grammar}`", "inline": True},
            {"name": "🔗 Links", "value": "[YouTube](https://youtube.com/@topikdaily) | [TikTok](https://tiktok.com/@topikdaily) | [Blog](https://topikdaily.com)", "inline": False}
        ]
        
        return self.send_embed(
            title=f"🇰🇷 TOPIK Daily - {datetime.now().strftime('%d/%m/%Y')}",
            description=f"**Chủ đề:** {topic}",
            fields=fields
        )


# ==================== EMAIL NEWSLETTER ====================

class EmailPublisher:
    """Send email newsletter"""
    
    def __init__(self):
        self.smtp_server = EMAIL_SMTP_SERVER
        self.smtp_port = EMAIL_SMTP_PORT
        self.email = EMAIL_ADDRESS
        self.password = EMAIL_PASSWORD
        self.subscribers = [s.strip() for s in EMAIL_SUBSCRIBER_LIST.split(",") if s.strip()]
    
    def is_available(self) -> bool:
        return bool(self.email and self.password and self.subscribers)
    
    def send_newsletter(self, subject: str, html_content: str) -> int:
        """Send newsletter to all subscribers"""
        if not self.is_available():
            logging.warning("⚠️ Email not configured")
            return 0
        
        sent_count = 0
        
        for subscriber in self.subscribers:
            try:
                msg = MIMEMultipart("alternative")
                msg["Subject"] = subject
                msg["From"] = f"TOPIK Daily <{self.email}>"
                msg["To"] = subscriber
                
                html_part = MIMEText(html_content, "html")
                msg.attach(html_part)
                
                with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                    server.starttls()
                    server.login(self.email, self.password)
                    server.sendmail(self.email, subscriber, msg.as_string())
                
                sent_count += 1
                logging.info(f"✅ Email sent to: {subscriber}")
                
            except Exception as e:
                logging.error(f"❌ Email error for {subscriber}: {e}")
        
        return sent_count
    
    def create_topik_newsletter(self, data: Dict) -> str:
        """Create HTML newsletter from TOPIK data"""
        meta = data.get("meta", {})
        phase1 = data.get("phase1", {})
        phase2 = data.get("phase2", {})
        phase3 = data.get("phase3", {})
        
        topic = meta.get("topic_title_vi", "TOPIK Daily")
        news_kr = phase1.get("news_summary_easy_kr", "")
        essay = phase2.get("essay", "")[:500]
        
        vocab_quiz = phase3.get("video_3_vocab_quiz", {})
        target_word = vocab_quiz.get("target_word", "")
        word_exp = vocab_quiz.get("explanation_vi", "")
        
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: 'Noto Sans KR', Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; }}
        .header {{ background: linear-gradient(135deg, #1a73e8, #4285f4); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
        .content {{ background: #f8f9fa; padding: 20px; }}
        .section {{ background: white; padding: 20px; margin: 10px 0; border-radius: 8px; }}
        .korean {{ font-size: 18px; color: #1a73e8; }}
        .cta {{ background: #1a73e8; color: white; padding: 15px 30px; text-decoration: none; border-radius: 25px; display: inline-block; }}
        .footer {{ text-align: center; padding: 20px; color: #666; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🇰🇷 TOPIK Daily</h1>
        <p>{datetime.now().strftime('%d/%m/%Y')}</p>
    </div>
    
    <div class="content">
        <div class="section">
            <h2>📚 Chủ đề hôm nay</h2>
            <p><strong>{topic}</strong></p>
        </div>
        
        <div class="section">
            <h2>📰 Tin Tức</h2>
            <p class="korean">{news_kr[:300]}...</p>
        </div>
        
        <div class="section">
            <h2>📖 Từ Vựng: <span class="korean">{target_word}</span></h2>
            <p>{word_exp}</p>
        </div>
        
        <div class="section">
            <h2>✍️ Trích đoạn bài văn mẫu</h2>
            <p class="korean">{essay}...</p>
        </div>
        
        <div class="section" style="text-align: center;">
            <h2>🎬 Xem đầy đủ</h2>
            <p>
                <a href="https://youtube.com/@topikdaily" class="cta">YouTube</a>
                <a href="https://tiktok.com/@topikdaily" class="cta" style="background: #000;">TikTok</a>
            </p>
        </div>
    </div>
    
    <div class="footer">
        <p>TOPIK Daily - Học tiếng Hàn mỗi ngày</p>
        <p><small>Để hủy đăng ký, reply email này với nội dung "Unsubscribe"</small></p>
    </div>
</body>
</html>
"""
        return html


# ==================== MAIN PUBLISHER ====================

class SocialMediaPublisher:
    """Unified publisher for all social media platforms"""
    
    def __init__(self):
        self.twitter = TwitterPublisher()
        self.telegram = TelegramPublisher()
        self.discord = DiscordPublisher()
        self.email = EmailPublisher()
    
    def publish_all(self, data: Dict) -> Dict:
        """Publish to all available platforms"""
        results = {
            "twitter": False,
            "telegram": False,
            "discord": False,
            "email": 0
        }
        
        # Twitter
        if self.twitter.is_available():
            tweets = self.twitter.create_topik_thread(data)
            tweet_ids = self.twitter.post_thread(tweets)
            results["twitter"] = len(tweet_ids) > 0
            logging.info(f"📱 Twitter: {len(tweet_ids)} tweets posted")
        
        # Telegram
        if self.telegram.is_available():
            message = self.telegram.create_topik_message(data)
            results["telegram"] = self.telegram.send_message(message)
            logging.info(f"📱 Telegram: {'✅' if results['telegram'] else '❌'}")
        
        # Discord
        if self.discord.is_available():
            results["discord"] = self.discord.create_topik_embed(data)
            logging.info(f"📱 Discord: {'✅' if results['discord'] else '❌'}")
        
        # Email
        if self.email.is_available():
            meta = data.get("meta", {})
            topic = meta.get("topic_title_vi", "TOPIK Daily")
            subject = f"🇰🇷 TOPIK Daily - {topic}"
            html = self.email.create_topik_newsletter(data)
            results["email"] = self.email.send_newsletter(subject, html)
            logging.info(f"📧 Email: {results['email']} sent")
        
        return results


def publish_to_social_media(json_path: str) -> Dict:
    """
    Main function to publish TOPIK content to social media
    
    Args:
        json_path: Path to final_data.json
        
    Returns:
        Results dict
    """
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    publisher = SocialMediaPublisher()
    return publisher.publish_all(data)


# ==================== CLI ====================
if __name__ == "__main__":
    import argparse
    
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s"
    )
    
    parser = argparse.ArgumentParser(description="Publish TOPIK content to social media")
    parser.add_argument("--json", default="topik-video/public/final_data.json", help="Path to final_data.json")
    parser.add_argument("--platform", choices=["all", "twitter", "telegram", "discord", "email"], default="all")
    
    args = parser.parse_args()
    
    if os.path.exists(args.json):
        results = publish_to_social_media(args.json)
        print(f"✅ Published: {results}")
    else:
        print(f"❌ File not found: {args.json}")
