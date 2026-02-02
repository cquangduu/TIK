# 🚀 DAILY KOREAN - Hướng Dẫn Setup Tất Cả Platform

> Hướng dẫn chi tiết để setup và kết nối tất cả các module trong hệ thống DAILY KOREAN

---

## 📋 Tổng Quan Các Module

| Module | Chức năng | API cần thiết | Revenue tiềm năng |
|--------|-----------|---------------|-------------------|
| **youtube_uploader.py** | Upload video YouTube | Google Cloud OAuth | AdSense |
| **social_publisher.py** | Đăng lên Twitter/Telegram/Discord | Twitter API, Telegram Bot | - |
| **telegram_bot.py** | Bot Telegram tương tác | Telegram Bot Token | Premium/Tips |
| **blog_generator.py** | Tạo blog tự động | - | SEO Traffic |
| **podcast_generator.py** | Tạo podcast Spotify | - | Sponsorship |
| **email_marketing.py** | Email list & Newsletter | ConvertKit/Mailchimp | Upsell |
| **github_deployer.py** | Deploy blog lên GitHub Pages | GitHub Token | - |
| **monetization.py** | Gumroad/Patreon tích hợp | Gumroad/Patreon API | $200-1000/mo |
| **affiliate_manager.py** | Quản lý affiliate links | Amazon/Coupang | $100-1000/mo |
| **anki_generator.py** | Tạo Anki deck bán | - | $200-1000/mo |
| **course_generator.py** | Tạo khóa học online | Udemy/Teachable | $500-5000/mo |
| **premium_gatekeeper.py** | Paywall & subscription | Stripe/Ko-fi | $200-2000/mo |
| **seo_optimizer.py** | Tối ưu SEO blog | - | 2-5x traffic |
| **community_manager.py** | Quản lý Discord/Telegram | Discord Webhook | $100-500/mo |
| **analytics_dashboard.py** | Theo dõi metrics & revenue | Các platform API | - |

---

## 🔧 PHASE 1: Chuẩn Bị File `.env`

Tạo file `.env` trong thư mục `TIK/`:

```env
# ========================================
# GOOGLE / YOUTUBE
# ========================================
# Tạo tại: https://console.cloud.google.com/
# Enable: YouTube Data API v3
YOUTUBE_CREDENTIALS_JSON={"installed":{"client_id":"...","client_secret":"..."}}

# ========================================
# TWITTER / X
# ========================================
# Tạo tại: https://developer.twitter.com/
TWITTER_API_KEY=your_api_key
TWITTER_API_SECRET=your_api_secret
TWITTER_ACCESS_TOKEN=your_access_token
TWITTER_ACCESS_SECRET=your_access_secret
TWITTER_BEARER_TOKEN=your_bearer_token

# ========================================
# TELEGRAM
# ========================================
# Tạo bot: Chat với @BotFather trên Telegram
# Gõ /newbot → đặt tên → nhận token
TELEGRAM_BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrsTUVwxyz
TELEGRAM_CHANNEL_ID=@dailykorean
TELEGRAM_ADMIN_ID=cquangdu

# ========================================
# DISCORD
# ========================================
# Tạo tại: Discord Server Settings → Integrations → Webhooks
DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/...

# ========================================
# EMAIL NEWSLETTER
# ========================================
# Option 1: Gmail SMTP
EMAIL_SMTP_SERVER=smtp.gmail.com
EMAIL_SMTP_PORT=587
EMAIL_ADDRESS=dailykoreanluyenviettopik@gmail.com
EMAIL_PASSWORD=tnts swiz twxx kohb  # Gmail App Password

# Option 2: ConvertKit
CONVERTKIT_API_KEY=your_convertkit_api_key
CONVERTKIT_API_SECRET=your_convertkit_api_secret

# Option 3: Mailchimp
MAILCHIMP_API_KEY=your_mailchimp_api_key
MAILCHIMP_LIST_ID=your_list_id

# ========================================
# GITHUB PAGES (Blog Deployment)
# ========================================
# Tạo tại: https://github.com/settings/tokens → Generate new token
GH_TOKEN=ghp_xxxxxxxxxxxx
GH_BLOG_REPO=username/dailykorean-blog
GH_BLOG_BRANCH=gh-pages
GH_USER_NAME=DAILY KOREAN Bot
GH_USER_EMAIL=bot@dailykorean.me

# ========================================
# MONETIZATION - GUMROAD
# ========================================
# Tạo tại: https://gumroad.com/settings/advanced
GUMROAD_ACCESS_TOKEN=your_gumroad_token
GUMROAD_PRODUCT_ID=your_product_id

# ========================================
# MONETIZATION - PATREON
# ========================================
# Tạo tại: https://www.patreon.com/portal/registration/register-clients
PATREON_ACCESS_TOKEN=your_patreon_token
PATREON_CAMPAIGN_ID=your_campaign_id

# ========================================
# PAYMENT - STRIPE
# ========================================
# Tạo tại: https://dashboard.stripe.com/apikeys
STRIPE_SECRET_KEY=sk_live_xxx
STRIPE_PUBLISHABLE_KEY=pk_live_xxx
STRIPE_WEBHOOK_SECRET=whsec_xxx

# ========================================
# AFFILIATE LINKS
# ========================================
AFFILIATE_TOPIK_BOOK_1=https://amzn.to/xxx
AFFILIATE_TOPIK_BOOK_2=https://amzn.to/yyy
AFFILIATE_TTMIK=https://talktomeinkorean.com/?ref=xxx

# ========================================
# TTS - AZURE
# ========================================
AZURE_TTS_KEY=your_azure_key
AZURE_TTS_REGION=koreacentral
```

---

## 📺 PHASE 2: Setup YouTube Upload

### Bước 1: Tạo Google Cloud Project

1. Truy cập [Google Cloud Console](https://console.cloud.google.com/)
2. Tạo Project mới: `daily-korean`
3. Enable **YouTube Data API v3**
4. Tạo OAuth 2.0 Credentials:
   - Application type: **Desktop app**
   - Download JSON → đổi tên thành `client_secrets.json`
   - Đặt vào thư mục `TIK/`

### Bước 2: Xác thực lần đầu

```powershell
cd C:\Users\ThinkPad\TIK
python -c "from youtube_uploader import YouTubeUploader; u = YouTubeUploader(); u.authenticate()"
```

→ Browser mở lên, đăng nhập Google, cho phép quyền
→ File `youtube_token.json` được tạo (lưu giữ cẩn thận!)

### Bước 3: Test upload

```python
from youtube_uploader import YouTubeUploader

uploader = YouTubeUploader()
uploader.authenticate()

# Upload video
video_id = uploader.upload_video(
    video_path="topik-video/out/youtube.mp4",
    title="TOPIK Daily - 02/02/2026",
    description="Học tiếng Hàn mỗi ngày...",
    tags=["TOPIK", "Korean", "한국어"],
    privacy="unlisted"  # Bắt đầu với unlisted để test
)
```

---

## 🐦 PHASE 3: Setup Twitter/X

### Bước 1: Tạo Developer Account

1. Truy cập [Twitter Developer Portal](https://developer.twitter.com/)
2. Apply for **Elevated Access** (miễn phí)
3. Tạo Project & App mới

### Bước 2: Lấy API Keys

Trong App Settings → Keys and Tokens:
- API Key & Secret
- Access Token & Secret
- Bearer Token

### Bước 3: Test post

```python
from social_publisher import SocialPublisher

publisher = SocialPublisher()

# Post tweet đơn
publisher.post_to_twitter("🇰🇷 Test post từ DAILY KOREAN! #TOPIK #Korean")

# Hoặc post thread
tweets = [
    "🇰🇷 TOPIK Daily - 02/02/2026\n\n📚 Chủ đề: Cô lập xã hội\n\n#TOPIK #Korean",
    "📖 Từ vựng: 사회적 고립\n고립 = cô lập, isolation",
    "🎬 Xem video: https://youtube.com/..."
]
publisher.post_twitter_thread(tweets)
```

---

## 🤖 PHASE 4: Setup Telegram Bot

### Bước 1: Tạo Bot với BotFather

1. Mở Telegram, tìm **@BotFather**
2. Gửi `/newbot`
3. Đặt tên: `DAILY KOREAN Bot`
4. Đặt username: `dailykorean_bot`
5. Nhận token: `123456789:ABCdefGHI...`

### Bước 2: Tạo Channel

1. Tạo Telegram Channel: `@dailykorean`
2. Add bot vào channel làm Admin
3. Cho bot quyền post

### Bước 3: Chạy bot

```powershell
pip install python-telegram-bot

# Chạy bot
python telegram_bot.py
```

Bot sẽ:
- Tự động gửi bài học hàng ngày
- Trả lời `/today`, `/vocab`, `/quiz`
- Chấp nhận Premium subscription

---

## 📝 PHASE 5: Setup Blog & GitHub Pages

### Bước 1: Tạo GitHub Repository

1. Tạo repo mới: `dailykorean-blog`
2. Enable GitHub Pages (Settings → Pages → Source: `gh-pages`)

### Bước 2: Tạo GitHub Token

1. [Settings → Developer settings → Personal access tokens](https://github.com/settings/tokens)
2. Generate new token với scope: `repo`, `workflow`
3. Copy token vào `.env`

### Bước 3: Generate & Deploy blog

```python
from blog_generator import BlogGenerator
from github_deployer import GitHubDeployer

# Generate blog từ final_data.json
generator = BlogGenerator()
generator.generate_from_data("topik-video/public/final_data.json")

# Deploy lên GitHub Pages
deployer = GitHubDeployer()
deployer.deploy("blog_output", commit_message="Daily update 02/02/2026")
```

Blog sẽ live tại: `https://username.github.io/dailykorean-blog`

---

## 🎙️ PHASE 6: Setup Podcast

### Bước 1: Cài đặt dependencies

```powershell
pip install pydub

# Windows cần FFmpeg
winget install ffmpeg
# Hoặc download từ https://ffmpeg.org/
```

### Bước 2: Generate podcast episode

```python
from podcast_generator import PodcastGenerator

generator = PodcastGenerator()

# Load data
with open("topik-video/public/final_data.json", "r", encoding="utf-8") as f:
    data = json.load(f)

# Generate episode
episode = generator.generate_episode(
    data=data,
    assets_dir="topik-video/public/assets",
    episode_number=1
)

# Generate RSS feed
generator.generate_rss_feed()
```

### Bước 3: Đăng ký Spotify for Podcasters

1. Truy cập [Spotify for Podcasters](https://podcasters.spotify.com/)
2. Submit RSS feed URL: `https://dailykorean.me/podcast/rss.xml`
3. Đợi duyệt (1-3 ngày)

---

## 📧 PHASE 7: Setup Email Marketing

### Option A: Gmail SMTP (Đơn giản)

1. Bật 2FA cho Gmail
2. Tạo [App Password](https://myaccount.google.com/apppasswords)
3. Dùng password này trong `.env`

### Option B: ConvertKit (Professional)

1. Đăng ký [ConvertKit](https://convertkit.com/) (Free đến 1000 subscribers)
2. Tạo Form để thu email
3. Lấy API Key từ Settings → Advanced

```python
from email_marketing import EmailMarketing

mailer = EmailMarketing()

# Gửi welcome email
mailer.send_welcome_email(
    email="subscriber@example.com",
    name="Minh",
    download_link="https://dailykorean.me/download/vocab-500.pdf"
)

# Gửi daily digest
mailer.send_daily_digest(data)
```

---

## 💰 PHASE 8: Setup Monetization

### A. Gumroad (Bán Digital Products)

1. Đăng ký [Gumroad](https://gumroad.com/)
2. Tạo product: "TOPIK Vocabulary 500 PDF + Anki"
3. Lấy Access Token từ Settings → Advanced → Create Application

```python
from monetization import GumroadManager

gumroad = GumroadManager()

# List products
products = gumroad.get_products()

# Check sales
sales = gumroad.get_sales()
```

### B. Patreon (Subscription)

1. Đăng ký [Patreon](https://www.patreon.com/)
2. Tạo tiers:
   - **Free**: Daily vocab
   - **$5/mo**: Anki decks + PDF
   - **$15/mo**: Video lessons + 1-on-1 review

### C. Stripe (Payment)

1. Đăng ký [Stripe](https://stripe.com/)
2. Tạo Products & Prices
3. Integrate với `premium_gatekeeper.py`

---

## 🔗 PHASE 9: Setup Affiliate

### Amazon Associates

1. Đăng ký [Amazon Associates](https://affiliate-program.amazon.com/)
2. Tạo link cho sách TOPIK:
   - TOPIK Essential Grammar
   - Korean Vocabulary 5000
3. Thêm vào `.env`

### Coupang Partners (Cho thị trường Hàn Quốc)

1. Đăng ký [Coupang Partners](https://partners.coupang.com/)
2. Tạo affiliate links

```python
from affiliate_manager import AffiliateManager

affiliate = AffiliateManager()

# Chèn affiliate links vào content
content_with_links = affiliate.insert_links(blog_content)

# Track clicks
affiliate.track_click("topik_book_1", user_ip="...")
```

---

## 📊 PHASE 10: Setup Analytics

```python
from analytics_dashboard import AnalyticsDashboard

dashboard = AnalyticsDashboard()

# Record metrics
dashboard.record_platform_metrics("youtube", {
    "views": 1500,
    "subscribers": 250,
    "revenue": 15.50
})

# Generate report
report = dashboard.generate_daily_report()
print(report)
```

---

## 🎯 Quick Start Checklist

### Ngày 1: Core Setup
- [ ] Tạo file `.env` với các API keys
- [ ] Setup YouTube OAuth (`client_secrets.json`)
- [ ] Test upload 1 video unlisted

### Ngày 2: Social Media
- [ ] Tạo Telegram Bot
- [ ] Tạo Telegram Channel
- [ ] Setup Twitter Developer Account

### Ngày 3: Blog & SEO
- [ ] Tạo GitHub repo cho blog
- [ ] Deploy blog đầu tiên
- [ ] Submit sitemap lên Google Search Console

### Ngày 4: Email & Monetization
- [ ] Setup ConvertKit/Mailchimp
- [ ] Tạo Lead Magnet (PDF miễn phí)
- [ ] Tạo Gumroad account

### Ngày 5: Podcast
- [ ] Install FFmpeg
- [ ] Generate podcast episode đầu tiên
- [ ] Submit lên Spotify

---

## 🔄 Automation Flow

```
main.py chạy hàng ngày
    ├── Phase 1-4: Tạo content
    ├── Phase 5: Render video (Remotion)
    └── Phase 6: Distribution
            ├── youtube_uploader.py → Upload 5 videos
            ├── social_publisher.py → Twitter thread + Telegram
            ├── blog_generator.py → Generate blog post
            ├── github_deployer.py → Deploy blog
            ├── podcast_generator.py → Generate podcast
            └── email_marketing.py → Send newsletter
```

---

## 🆘 Troubleshooting

### YouTube "quotaExceeded"
- YouTube API có quota 10,000 units/ngày
- Upload 1 video = 1600 units
- Giải pháp: Request quota increase hoặc upload ít video hơn

### Telegram "Forbidden: bot is not a member"
- Add bot vào channel làm Admin
- Đảm bảo bot có quyền "Post Messages"

### GitHub Pages 404
- Kiểm tra branch `gh-pages` đã được tạo
- Đợi 1-2 phút để GitHub build

### Gmail "Less secure app blocked"
- Dùng App Password thay vì password thường
- Bật 2FA trước

---

## 📞 Support

- Email: dailykoreanluyenviettopik@gmail.com
- Telegram: @dailykorean
- Discord: discord.gg/dailykorean

---

*Được tạo bởi DAILY KOREAN Automation System*
