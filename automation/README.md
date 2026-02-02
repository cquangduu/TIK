# 🚀 TOPIK Daily - Hệ Thống Tự Động Hoàn Toàn

> Tạo & phân phối nội dung học tiếng Hàn TOPIK tự động 24/7, tối ưu cho máy ảo 1vCPU/2GB RAM.
> **🔗 TÍCH HỢP HOÀN TOÀN** với các module hiện có trong project.

## 📋 Mục Lục

- [Tổng Quan](#-tổng-quan)
- [Kiến Trúc Tích Hợp](#-kiến-trúc-tích-hợp)
- [Cài Đặt](#-cài-đặt)
- [Cấu Hình](#-cấu-hình)
- [Vận Hành](#-vận-hành)
- [Kiếm Tiền](#-kiếm-tiền)
- [Chi Phí](#-chi-phí)

---

## 🎯 Tổng Quan

TOPIK Daily là hệ thống tự động hóa **SỬ DỤNG LẠI** các module bạn đã có:

### 🔧 Core Modules (Pipeline cơ bản)
- ✅ **main.py** - Pipeline tạo nội dung chính (Phase 1-4)
- ✅ **youtube_uploader.py** - Upload YouTube với OAuth2
- ✅ **blog_generator.py** - Tạo blog với SEO
- ✅ **podcast_generator.py** - Tạo podcast
- ✅ **social_publisher.py** - Đăng TikTok, Facebook
- ✅ **telegram_bot.py** - Bot Telegram tương tác
- ✅ **monetization.py** - Gumroad, Patreon, Affiliate

### 💰 Professional Revenue Modules (Kiếm tiền chuyên nghiệp)
- ✅ **email_marketing.py** - Email list, newsletters, ConvertKit/Mailchimp
- ✅ **anki_generator.py** - Tạo Anki deck để bán (Gumroad)
- ✅ **seo_optimizer.py** - SEO meta tags, Schema.org, sitemap
- ✅ **analytics_dashboard.py** - Unified analytics, revenue tracking
- ✅ **course_generator.py** - Tạo khóa học Udemy/Teachable
- ✅ **affiliate_manager.py** - Quản lý affiliate links (Amazon, Coupang)
- ✅ **community_manager.py** - Discord/Telegram community automation
- ✅ **premium_gatekeeper.py** - Paywall, Stripe integration, access control

### 📦 Cấu Trúc Tích Hợp

```
TIK/                              # Project root
├── main.py                       # ✅ Pipeline chính (2949 lines)
├── youtube_uploader.py           # ✅ YouTube OAuth2 upload
├── blog_generator.py             # ✅ Blog generator
├── podcast_generator.py          # ✅ Podcast generator
├── social_publisher.py           # ✅ Social media publisher
├── github_deployer.py            # ✅ GitHub Pages deployer
├── telegram_bot.py               # ✅ Telegram bot
├── monetization.py               # ✅ Monetization manager
│
├── # 💰 PROFESSIONAL REVENUE MODULES
├── email_marketing.py            # ✅ Email newsletters
├── anki_generator.py             # ✅ Sellable Anki decks
├── seo_optimizer.py              # ✅ Blog SEO optimization
├── analytics_dashboard.py        # ✅ Unified analytics
├── course_generator.py           # ✅ Udemy/Teachable courses
├── affiliate_manager.py          # ✅ Affiliate link management
├── community_manager.py          # ✅ Community automation
├── premium_gatekeeper.py         # ✅ Paywall & Stripe
│
├── automation/
│   ├── scheduler.py              # 🔄 Scheduler (import các module trên)
│   ├── scripts/setup.sh          # Setup VPS script
│   ├── requirements.txt          # Dependencies bổ sung
│   └── README.md                 # File này
│
├── topik-video/                  # Remotion project
│   ├── src/components/           # Video components
│   └── public/final_data.json    # Data từ main.py
│
└── .github/workflows/
    └── render-videos.yml         # GitHub Actions render
```

---

## 🔗 Cách Scheduler Tích Hợp

`scheduler.py` **KHÔNG duplicate code** mà **IMPORT trực tiếp** các module:

| Task Scheduler | Module Gốc | Function |
|----------------|------------|----------|
| `task_generate_content()` | `main.py` | `run_full_pipeline()` |
| `task_upload_youtube()` | `youtube_uploader.py` | `YouTubeUploader.upload_video()` |
| `task_generate_blog()` | `blog_generator.py` | `generate_blog_from_data()` |
| `task_generate_podcast()` | `podcast_generator.py` | `generate_podcast_from_data()` |
| `task_post_telegram()` | `telegram_bot.py` | `send_daily_push()` |
| `task_upload_tiktok()` | `social_publisher.py` | `SocialMediaPublisher` |
| `task_collect_analytics()` | `monetization.py` | `MonetizationManager` |
| **💰 PROFESSIONAL REVENUE TASKS** | | |
| `task_send_daily_email()` | `email_marketing.py` | `EmailMarketingManager` |
| `task_generate_anki_deck()` | `anki_generator.py` | `AnkiDeckGenerator` |
| `task_optimize_seo()` | `seo_optimizer.py` | `SEOOptimizer` |
| `task_collect_platform_analytics()` | `analytics_dashboard.py` | `PlatformCollector` |
| `task_update_affiliate_links()` | `affiliate_manager.py` | `AffiliateManager` |
| `task_post_community_daily()` | `community_manager.py` | `CommunityBot` |
| `task_generate_weekly_anki()` | `anki_generator.py` | `AnkiDeckGenerator.premium` |

---

## 🏗️ Kiến Trúc Hệ Thống

```
┌─────────────────────────────────────────────────────────────────┐
│                 DIGITALOCEAN DROPLET ($6/tháng)                  │
│                     1vCPU / 2GB RAM / 50GB                       │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                 Python Scheduler (scheduler.py)           │   │
│  │                                                           │   │
│  │  IMPORTS:                                                 │   │
│  │  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐      │   │
│  │  │   main.py    │ │youtube_upload│ │blog_generator│      │   │
│  │  │(full pipeline)│ │   er.py     │ │     .py      │      │   │
│  │  └──────────────┘ └──────────────┘ └──────────────┘      │   │
│  │  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐      │   │
│  │  │social_publish│ │telegram_bot  │ │monetization  │      │   │
│  │  │   er.py      │ │    .py       │ │    .py       │      │   │
│  │  └──────────────┘ └──────────────┘ └──────────────┘      │   │
│  └──────────────────────────────────────────────────────────┘   │
│          │           │           │           │                   │
│          ▼           ▼           ▼           ▼                   │
│      SQLite DB    APIs       APIs       SQLite DB               │
└──────────┬───────────────────────────────────────────────────────┘
           │
           ▼ Trigger via API
┌──────────────────────────────────────────────────────────────────┐
│                    GITHUB ACTIONS (FREE)                          │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │              Remotion Video Rendering                        │ │
│  │   video_1  video_2  video_3  video_4  video_5               │ │
│  │     ▼        ▼        ▼        ▼        ▼                   │ │
│  │    MP4      MP4      MP4      MP4      MP4                  │ │
│  └─────────────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────────┘
           │
           ▼ Upload
┌──────────────────────────────────────────────────────────────────┐
│                     DISTRIBUTION PLATFORMS                        │
│   TikTok    YouTube    Facebook    Telegram    Blog              │
│     💰        💰          💰         💰         💰                │
└──────────────────────────────────────────────────────────────────┘
```

---

## 🔧 Cài Đặt

### Bước 1: Tạo DigitalOcean Droplet

1. Truy cập [DigitalOcean](https://digitalocean.com)
2. Create Droplet:
   - **Image**: Ubuntu 22.04 LTS
   - **Plan**: Premium Intel - $6/month (1vCPU, 2GB RAM)
   - **Region**: Singapore (gần Việt Nam)
   - **Authentication**: SSH Key

### Bước 2: Chạy Setup Script

```bash
# SSH vào server
ssh root@your-droplet-ip

# Download và chạy setup script
curl -sSL https://raw.githubusercontent.com/your-repo/main/automation/scripts/setup.sh | bash
```

### Bước 3: Cấu Hình API Keys

```bash
# Copy template
cp /opt/topik-daily/config/.env.template /opt/topik-daily/config/.env

# Edit với API keys của bạn
nano /opt/topik-daily/config/.env
```

### Bước 4: Khởi Động Service

```bash
# Start scheduler
systemctl start topik-scheduler

# Enable auto-start on boot
systemctl enable topik-scheduler

# Check status
topik-status
```

---

## ⚙️ Cấu Hình

### API Keys Cần Thiết

| Service | Mục đích | Cách lấy |
|---------|----------|----------|
| **OpenAI** | Content generation | [platform.openai.com](https://platform.openai.com) |
| **Azure TTS** | Text-to-speech | [portal.azure.com](https://portal.azure.com) |
| **GitHub Token** | Trigger Actions | Settings → Developer settings → Tokens |
| **TikTok** | Upload videos | [developers.tiktok.com](https://developers.tiktok.com) |
| **YouTube** | Upload videos | [console.cloud.google.com](https://console.cloud.google.com) |
| **Telegram** | Bot posting | [@BotFather](https://t.me/BotFather) |

### Lịch Trình Mặc Định

| Thời gian | Task | Module |
|-----------|------|--------|
| 04:00 | Fetch news + Generate content | main.py |
| 05:00 | Generate TTS audio | main.py |
| 05:30 | Trigger cloud rendering | GitHub Actions |
| 07:30 | Upload to TikTok | social_publisher.py |
| 08:00 | Upload to YouTube | youtube_uploader.py |
| 09:00 | Generate blog + Post Telegram | blog_generator.py |
| **💰 PROFESSIONAL REVENUE TASKS** | | |
| 10:30 | Send daily email | email_marketing.py |
| 11:00 | Generate Anki deck | anki_generator.py |
| 11:30 | Optimize SEO | seo_optimizer.py |
| 12:00 | Update affiliate links | affiliate_manager.py |
| 12:30 | Post to community | community_manager.py |
| 14:00 (Sun) | Weekly premium Anki | anki_generator.py |
| 21:00 | Collect platform analytics | analytics_dashboard.py |
| 22:00 | Collect monetization data | monetization.py |
| 23:00 | Generate daily report | monetization.py |
| 23:30 | Generate revenue report | analytics_dashboard.py |

---

## 🖥️ Vận Hành

### Kiểm Tra Status

```bash
# Quick status
topik-status

# View logs
tail -f /opt/topik-daily/logs/scheduler.log

# Check service
systemctl status topik-scheduler
```

### Chạy Task Thủ Công

```bash
cd /opt/topik-daily
source venv/bin/activate

# Chạy một task cụ thể
python automation/scheduler.py --run generate_content

# Chạy full pipeline
python automation/scheduler.py --run all

# Xem today's tasks
python automation/scheduler.py --status
```

### Troubleshooting

```bash
# Restart service
systemctl restart topik-scheduler

# Check errors
journalctl -u topik-scheduler -n 50

# Check resource usage
htop
```

---

## 💰 Kiếm Tiền

### Tổng Quan Thu Nhập

| Tier | Nguồn | Thu nhập/tháng | Module |
|------|-------|----------------|--------|
| 🟢 Passive | TikTok Creator Fund | $50-200 | social_publisher.py |
| 🟢 Passive | YouTube AdSense | $100-500 | youtube_uploader.py |
| 🟢 Passive | Affiliate links | $100-500 | affiliate_manager.py |
| 🟢 Passive | Anki deck sales | $200-1000 | anki_generator.py |
| 🟡 Semi-Passive | Email newsletter | $500-2000 | email_marketing.py |
| 🟡 Semi-Passive | Premium subscription | $200-1000 | premium_gatekeeper.py |
| 🟡 Semi-Passive | Udemy course | $100-1000 | course_generator.py |
| 🟡 Semi-Passive | Telegram Premium | $200-500 | telegram_bot.py |
| 🔴 Active | Community premium | $100-500 | community_manager.py |
| 🔴 Active | 1-on-1 Tutoring | $500-2000 | manual |

### 📊 Revenue Potential Summary

| Stage | Monthly Revenue | Automation Level |
|-------|-----------------|------------------|
| Month 1-3 | $0-300 | 100% automated |
| Month 4-6 | $300-1000 | 95% automated |
| Month 7-12 | $1000-3000 | 90% automated |
| Year 2+ | $3000-10000+ | 85% automated |

**Xem chi tiết**: [MONETIZATION_GUIDE.md](MONETIZATION_GUIDE.md)

### Track Revenue

```bash
# Dashboard
python automation/monetization.py

# Add revenue
python automation/monetization.py add-revenue youtube_adsense 150.00 "March payout"

# Monthly report
python automation/monetization.py monthly 2026 2
```

---

## 💵 Chi Phí Vận Hành

### Hàng Tháng

| Dịch vụ | Chi phí | Ghi chú |
|---------|---------|---------|
| DigitalOcean | $6 | 1vCPU/2GB RAM |
| OpenAI | $5-20 | ~500K tokens |
| Azure TTS | $0-15 | Free tier 500K chars |
| Domain | $1 | ~$12/year |
| **Tổng** | **$12-42** | |

### Chi Phí Một Lần

| Item | Chi phí |
|------|---------|
| Domain đăng ký | $12/năm |
| SSL Certificate | $0 (Let's Encrypt) |

### ROI Projection

| Tháng | Chi phí | Thu nhập | Lợi nhuận |
|-------|---------|----------|-----------|
| 1-3 | $36-126 | $0-100 | -$126 to +$64 |
| 4-6 | $36-126 | $100-500 | +$0 to +$374 |
| 7-12 | $72-252 | $500-2000 | +$248 to +$1748 |
| Year 2+ | $144-504 | $2000-5000+ | +$1500-4500+ |

---

## 📊 Commands Cheat Sheet

```bash
# === SERVICE MANAGEMENT ===
systemctl start topik-scheduler      # Start
systemctl stop topik-scheduler       # Stop
systemctl restart topik-scheduler    # Restart
systemctl status topik-scheduler     # Status

# === MONITORING ===
topik-status                         # Quick dashboard
htop                                 # Resource usage
tail -f /opt/topik-daily/logs/*.log  # Live logs

# === SCHEDULER ===
cd /opt/topik-daily && source venv/bin/activate
python automation/scheduler.py --status         # Today's tasks
python automation/scheduler.py --run all        # Run all tasks
python automation/scheduler.py --run upload_tiktok  # Single task

# === ANALYTICS ===
python automation/analytics.py collect          # Collect now
python automation/analytics.py report           # Today's report
python automation/analytics.py monthly 2026 2   # Monthly report

# === MONETIZATION ===
python automation/monetization.py               # Dashboard
python automation/monetization.py monthly       # Monthly revenue

# === BACKUP ===
sqlite3 /opt/topik-daily/data/analytics.db ".backup backup.db"

# === LOGS ===
tail -100 /opt/topik-daily/logs/scheduler.log
grep "ERROR" /opt/topik-daily/logs/*.log
```

---

## 🔐 Security Checklist

- [x] SSH key authentication (no password)
- [x] Firewall (UFW) configured
- [x] Fail2ban active
- [x] API keys in .env (not in code)
- [x] Regular log rotation
- [x] Swap configured for stability
- [ ] SSL certificate (run: `certbot --nginx -d yourdomain.com`)
- [ ] Regular backups to external storage

---

## 📞 Support

- **Issues**: GitHub Issues
- **Documentation**: This README + ARCHITECTURE.md + MONETIZATION_GUIDE.md
- **Logs**: `/opt/topik-daily/logs/`

---

**Made with ❤️ for Korean learners worldwide**
