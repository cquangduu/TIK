"""
================================================================================
EMAIL MARKETING MODULE — Build Email List & Nurture Subscribers
================================================================================
Features:
    1. Lead Magnet Generator - Free PDFs/Anki decks to collect emails
    2. ConvertKit/Mailchimp Integration - Newsletter automation
    3. Drip Campaign Manager - 7-day welcome series
    4. Email Template Generator - Beautiful Korean learning emails
    5. Subscriber Analytics - Track opens, clicks, conversions
================================================================================
Revenue Potential: $500-2000/month (1000+ subscribers)
================================================================================
"""

import os
import json
import logging
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from dotenv import load_dotenv

load_dotenv()

# ==================== CONFIGURATION ====================
CONVERTKIT_API_KEY = os.getenv("CONVERTKIT_API_KEY", "")
CONVERTKIT_API_SECRET = os.getenv("CONVERTKIT_API_SECRET", "")
MAILCHIMP_API_KEY = os.getenv("MAILCHIMP_API_KEY", "")
MAILCHIMP_LIST_ID = os.getenv("MAILCHIMP_LIST_ID", "")

# Email templates directory
TEMPLATES_DIR = "email_templates"
os.makedirs(TEMPLATES_DIR, exist_ok=True)


# ==================== EMAIL TEMPLATES ====================

WELCOME_EMAIL_TEMPLATE = """
Subject: 🇰🇷 Chào mừng đến với TOPIK Daily! Quà tặng cho bạn bên trong

---

안녕하세요 {name}! 👋

Cảm ơn bạn đã đăng ký nhận bài học TOPIK hàng ngày!

## 🎁 Quà tặng chào mừng

Tải ngay **500 từ vựng TOPIK II** (PDF + Anki):
👉 [Tải xuống tại đây]({download_link})

## 📅 Bạn sẽ nhận được gì?

Mỗi ngày, tôi sẽ gửi cho bạn:
- 📰 Tin tức Hàn Quốc (song ngữ)
- 📝 Bài văn mẫu TOPIK 54
- 🎯 Quiz từ vựng & ngữ pháp
- 🎬 Video TikTok học tiếng Hàn

## 🚀 Bắt đầu ngay

Xem bài học hôm nay:
- [TikTok]({tiktok_link})
- [YouTube]({youtube_link})
- [Blog]({blog_link})

---

Chúc bạn học tốt! 화이팅! 💪

P.S. Có câu hỏi? Chỉ cần reply email này!
"""

DAILY_EMAIL_TEMPLATE = """
Subject: 📚 Bài học TOPIK ngày {date} - {topic}

---

안녕하세요! 👋

## 📰 Tin tức hôm nay

**🇰🇷 Tiếng Hàn:**
{news_ko}

**🇻🇳 Tiếng Việt:**
{news_vi}

---

## 📝 Từ vựng mới

{vocabulary_list}

---

## 🎯 Quiz nhanh

{quiz_question}

A) {option_a}
B) {option_b}
C) {option_c}
D) {option_d}

👉 [Xem đáp án & giải thích]({answer_link})

---

## 🎬 Video hôm nay

- [TikTok: Tin tức]({video_1})
- [TikTok: Bài văn mẫu]({video_2})
- [YouTube: Deep Dive]({video_5})

---

수고하셨습니다! 화이팅! 💪
"""

WEEKLY_DIGEST_TEMPLATE = """
Subject: 📊 Tổng kết tuần {week_number} - {date_range}

---

## 🏆 Thành tích của bạn tuần này

- 📚 Từ vựng mới: **{vocab_count}** từ
- 📝 Ngữ pháp: **{grammar_count}** cấu trúc
- 🎯 Quiz: **{quiz_score}%** chính xác

---

## 📈 Bài học nổi bật

{weekly_highlights}

---

## 🎁 Tài liệu tuần này

[Tải PDF tổng hợp tuần {week_number}]({pdf_link})

---

## 💎 Nâng cấp Premium

Muốn học nhanh hơn? Premium bao gồm:
- ✅ Anki deck độc quyền
- ✅ Video bài giảng chi tiết
- ✅ 1-on-1 Q&A session
- ✅ Certificate hoàn thành

👉 [Nâng cấp ngay - Giảm 30%]({premium_link})

---

화이팅! 💪
"""


class EmailMarketingManager:
    """
    Quản lý email marketing tự động.
    Hỗ trợ ConvertKit và Mailchimp.
    """
    
    def __init__(self, provider: str = "convertkit"):
        self.provider = provider
        
        if provider == "convertkit":
            self.api_key = CONVERTKIT_API_KEY
            self.api_secret = CONVERTKIT_API_SECRET
            self.base_url = "https://api.convertkit.com/v3"
        elif provider == "mailchimp":
            self.api_key = MAILCHIMP_API_KEY
            self.list_id = MAILCHIMP_LIST_ID
            # Extract data center from API key
            dc = self.api_key.split("-")[-1] if self.api_key else "us1"
            self.base_url = f"https://{dc}.api.mailchimp.com/3.0"
    
    def is_available(self) -> bool:
        """Check if API is configured"""
        if self.provider == "convertkit":
            return bool(self.api_key)
        elif self.provider == "mailchimp":
            return bool(self.api_key and self.list_id)
        return False
    
    # ─── ConvertKit Methods ───────────────────────────────────────────────
    
    def ck_get_subscribers(self) -> List[Dict]:
        """Get all subscribers from ConvertKit"""
        if not self.is_available():
            return []
        
        response = requests.get(
            f"{self.base_url}/subscribers",
            params={"api_secret": self.api_secret}
        )
        
        if response.status_code == 200:
            return response.json().get("subscribers", [])
        return []
    
    def ck_add_subscriber(self, email: str, first_name: str = "", tags: List[int] = None) -> bool:
        """Add subscriber to ConvertKit"""
        if not self.is_available():
            return False
        
        data = {
            "api_secret": self.api_secret,
            "email": email,
            "first_name": first_name,
        }
        
        if tags:
            # Add to specific tags
            for tag_id in tags:
                requests.post(
                    f"{self.base_url}/tags/{tag_id}/subscribe",
                    json=data
                )
        
        return True
    
    def ck_send_broadcast(self, subject: str, content: str, segment_ids: List[int] = None) -> bool:
        """Send broadcast email via ConvertKit"""
        if not self.is_available():
            return False
        
        data = {
            "api_secret": self.api_secret,
            "subject": subject,
            "content": content,
            "published": True,
        }
        
        if segment_ids:
            data["segment_ids"] = segment_ids
        
        response = requests.post(
            f"{self.base_url}/broadcasts",
            json=data
        )
        
        return response.status_code == 201
    
    # ─── Mailchimp Methods ────────────────────────────────────────────────
    
    def mc_get_subscribers(self) -> List[Dict]:
        """Get subscribers from Mailchimp"""
        if not self.is_available():
            return []
        
        response = requests.get(
            f"{self.base_url}/lists/{self.list_id}/members",
            auth=("anystring", self.api_key)
        )
        
        if response.status_code == 200:
            return response.json().get("members", [])
        return []
    
    def mc_add_subscriber(self, email: str, first_name: str = "", tags: List[str] = None) -> bool:
        """Add subscriber to Mailchimp"""
        if not self.is_available():
            return False
        
        data = {
            "email_address": email,
            "status": "subscribed",
            "merge_fields": {
                "FNAME": first_name
            }
        }
        
        if tags:
            data["tags"] = tags
        
        response = requests.post(
            f"{self.base_url}/lists/{self.list_id}/members",
            json=data,
            auth=("anystring", self.api_key)
        )
        
        return response.status_code in [200, 201]
    
    def mc_send_campaign(self, subject: str, content: str) -> bool:
        """Create and send campaign via Mailchimp"""
        if not self.is_available():
            return False
        
        # Create campaign
        campaign_data = {
            "type": "regular",
            "recipients": {"list_id": self.list_id},
            "settings": {
                "subject_line": subject,
                "from_name": "TOPIK Daily",
                "reply_to": os.getenv("EMAIL_REPLY_TO", "hello@topikdaily.com"),
            }
        }
        
        response = requests.post(
            f"{self.base_url}/campaigns",
            json=campaign_data,
            auth=("anystring", self.api_key)
        )
        
        if response.status_code != 200:
            return False
        
        campaign_id = response.json().get("id")
        
        # Set content
        content_data = {
            "html": content
        }
        
        requests.put(
            f"{self.base_url}/campaigns/{campaign_id}/content",
            json=content_data,
            auth=("anystring", self.api_key)
        )
        
        # Send campaign
        response = requests.post(
            f"{self.base_url}/campaigns/{campaign_id}/actions/send",
            auth=("anystring", self.api_key)
        )
        
        return response.status_code == 204
    
    # ─── Unified Methods ──────────────────────────────────────────────────
    
    def get_subscriber_count(self) -> int:
        """Get total subscriber count"""
        if self.provider == "convertkit":
            return len(self.ck_get_subscribers())
        elif self.provider == "mailchimp":
            return len(self.mc_get_subscribers())
        return 0
    
    def add_subscriber(self, email: str, name: str = "", tags: List = None) -> bool:
        """Add subscriber (unified)"""
        if self.provider == "convertkit":
            return self.ck_add_subscriber(email, name, tags)
        elif self.provider == "mailchimp":
            return self.mc_add_subscriber(email, name, tags)
        return False
    
    def send_daily_email(self, data: Dict) -> bool:
        """Send daily learning email"""
        subject = f"📚 Bài học TOPIK ngày {data.get('date', 'hôm nay')} - {data.get('topic', 'Học tiếng Hàn')}"
        
        content = DAILY_EMAIL_TEMPLATE.format(
            date=data.get("date", datetime.now().strftime("%d/%m/%Y")),
            topic=data.get("topic", "TOPIK"),
            news_ko=data.get("news_ko", ""),
            news_vi=data.get("news_vi", ""),
            vocabulary_list=data.get("vocabulary_list", ""),
            quiz_question=data.get("quiz_question", ""),
            option_a=data.get("options", ["", "", "", ""])[0],
            option_b=data.get("options", ["", "", "", ""])[1],
            option_c=data.get("options", ["", "", "", ""])[2],
            option_d=data.get("options", ["", "", "", ""])[3],
            answer_link=data.get("answer_link", "#"),
            video_1=data.get("video_1", "#"),
            video_2=data.get("video_2", "#"),
            video_5=data.get("video_5", "#"),
        )
        
        if self.provider == "convertkit":
            return self.ck_send_broadcast(subject, content)
        elif self.provider == "mailchimp":
            return self.mc_send_campaign(subject, content)
        return False


class LeadMagnetGenerator:
    """
    Tạo lead magnets để thu thập email:
    - PDF từ vựng/ngữ pháp
    - Anki decks
    - Cheat sheets
    """
    
    def __init__(self):
        self.output_dir = "lead_magnets"
        os.makedirs(self.output_dir, exist_ok=True)
    
    def generate_vocab_pdf(self, vocab_list: List[Dict], title: str = "500 Từ Vựng TOPIK II") -> str:
        """Generate vocabulary PDF for lead magnet"""
        try:
            from reportlab.lib.pagesizes import A4
            from reportlab.pdfgen import canvas
            from reportlab.pdfbase import pdfmetrics
            from reportlab.pdfbase.ttfonts import TTFont
            
            output_path = os.path.join(self.output_dir, f"{title.replace(' ', '_')}.pdf")
            
            c = canvas.Canvas(output_path, pagesize=A4)
            width, height = A4
            
            # Title page
            c.setFont("Helvetica-Bold", 24)
            c.drawCentredString(width/2, height - 100, title)
            c.setFont("Helvetica", 14)
            c.drawCentredString(width/2, height - 140, "TOPIK Daily - Học tiếng Hàn mỗi ngày")
            c.showPage()
            
            # Vocabulary pages
            y = height - 50
            for i, vocab in enumerate(vocab_list):
                if y < 100:
                    c.showPage()
                    y = height - 50
                
                c.setFont("Helvetica-Bold", 12)
                c.drawString(50, y, f"{i+1}. {vocab.get('korean', '')}")
                c.setFont("Helvetica", 11)
                c.drawString(200, y, vocab.get('meaning', ''))
                c.setFont("Helvetica-Oblique", 10)
                c.drawString(50, y - 15, vocab.get('example', ''))
                
                y -= 40
            
            c.save()
            logging.info(f"✅ Generated PDF: {output_path}")
            return output_path
            
        except ImportError:
            logging.warning("⚠️ reportlab not installed. pip install reportlab")
            return ""
    
    def generate_anki_deck(self, vocab_list: List[Dict], deck_name: str = "TOPIK_Daily") -> str:
        """Generate Anki deck for lead magnet"""
        try:
            import genanki
            
            # Create model
            model = genanki.Model(
                1607392319,
                'TOPIK Vocabulary',
                fields=[
                    {'name': 'Korean'},
                    {'name': 'Vietnamese'},
                    {'name': 'Example'},
                    {'name': 'Audio'},
                ],
                templates=[
                    {
                        'name': 'Card 1',
                        'qfmt': '<div class="korean">{{Korean}}</div>',
                        'afmt': '''{{FrontSide}}<hr id="answer">
                                   <div class="meaning">{{Vietnamese}}</div>
                                   <div class="example">{{Example}}</div>''',
                    },
                ],
                css='''
                    .korean { font-size: 32px; text-align: center; }
                    .meaning { font-size: 24px; text-align: center; color: #2196F3; }
                    .example { font-size: 18px; text-align: center; margin-top: 10px; }
                '''
            )
            
            # Create deck
            deck = genanki.Deck(
                2059400110,
                deck_name
            )
            
            # Add cards
            for vocab in vocab_list:
                note = genanki.Note(
                    model=model,
                    fields=[
                        vocab.get('korean', ''),
                        vocab.get('meaning', ''),
                        vocab.get('example', ''),
                        '',  # Audio placeholder
                    ]
                )
                deck.add_note(note)
            
            # Save
            output_path = os.path.join(self.output_dir, f"{deck_name}.apkg")
            genanki.Package(deck).write_to_file(output_path)
            
            logging.info(f"✅ Generated Anki deck: {output_path}")
            return output_path
            
        except ImportError:
            logging.warning("⚠️ genanki not installed. pip install genanki")
            return ""


class DripCampaignManager:
    """
    Quản lý drip campaigns (chuỗi email tự động).
    Ví dụ: Welcome series 7 ngày.
    """
    
    def __init__(self, email_manager: EmailMarketingManager):
        self.email_manager = email_manager
        self.campaigns_file = "drip_campaigns.json"
    
    def get_welcome_series(self) -> List[Dict]:
        """7-day welcome email series"""
        return [
            {
                "day": 0,
                "subject": "🎁 Quà chào mừng + Lộ trình học TOPIK",
                "template": "welcome_day0.html",
                "tag": "day0_sent"
            },
            {
                "day": 1,
                "subject": "📚 Ngày 1: 10 từ vựng TOPIK quan trọng nhất",
                "template": "welcome_day1.html",
                "tag": "day1_sent"
            },
            {
                "day": 2,
                "subject": "📝 Ngày 2: Cách viết bài văn TOPIK hoàn hảo",
                "template": "welcome_day2.html",
                "tag": "day2_sent"
            },
            {
                "day": 3,
                "subject": "🎧 Ngày 3: Bí quyết nghe hiểu tiếng Hàn",
                "template": "welcome_day3.html",
                "tag": "day3_sent"
            },
            {
                "day": 5,
                "subject": "🎯 Ngày 5: Làm quiz thử sức nào!",
                "template": "welcome_day5.html",
                "tag": "day5_sent"
            },
            {
                "day": 7,
                "subject": "💎 Đặc biệt: Giảm 50% khóa Premium (24h)",
                "template": "welcome_day7.html",
                "tag": "day7_sent"
            },
        ]


# ==================== UTILITY FUNCTIONS ====================

def send_daily_newsletter(data_file: str = "topik-video/public/final_data.json"):
    """Send daily newsletter from final_data.json"""
    if not os.path.exists(data_file):
        logging.error(f"❌ Data file not found: {data_file}")
        return False
    
    with open(data_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    email_manager = EmailMarketingManager()
    
    if not email_manager.is_available():
        logging.warning("⚠️ Email marketing not configured")
        return False
    
    # Prepare email data
    email_data = {
        "date": datetime.now().strftime("%d/%m/%Y"),
        "topic": data.get("topic", "TOPIK"),
        "news_ko": data.get("video_1", {}).get("script_ko", ""),
        "news_vi": data.get("video_1", {}).get("script_vi", ""),
        "vocabulary_list": format_vocabulary_for_email(data.get("vocabulary", [])),
        "quiz_question": data.get("video_3", {}).get("question", ""),
        "options": data.get("video_3", {}).get("options", ["", "", "", ""]),
    }
    
    return email_manager.send_daily_email(email_data)


def format_vocabulary_for_email(vocab_list: List[Dict]) -> str:
    """Format vocabulary list for email"""
    lines = []
    for v in vocab_list[:5]:  # Top 5
        lines.append(f"• **{v.get('korean', '')}** - {v.get('meaning', '')}")
    return "\n".join(lines)


# ==================== MAIN ====================

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    # Test
    manager = EmailMarketingManager()
    print(f"Email marketing available: {manager.is_available()}")
    print(f"Subscriber count: {manager.get_subscriber_count()}")
