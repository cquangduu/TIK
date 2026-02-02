# 🚀 DAILY KOREAN - Hướng Dẫn Bật Tất Cả Module & Tự Động Hóa

> Hướng dẫn chi tiết để bật tất cả các module và chạy pipeline tự động hoàn toàn

---

## 📋 Tổng Quan Pipeline

```
main.py
    │
    ├── Phase 1: Thu thập tin tức RSS
    ├── Phase 2: Tạo bài văn mẫu TOPIK
    ├── Phase 3: Tạo script 4 video TikTok
    ├── Phase 4: Tạo script Deep Dive YouTube
    ├── Phase 5: Tạo audio Azure TTS
    ├── Phase 6: Render 5 video (Remotion)
    │
    └── Phase 7: Distribution (Tự động upload)
            ├── ☁️ Google Drive Upload
            ├── 📺 YouTube Upload
            ├── 📝 Blog Generation
            ├── 🚀 GitHub Pages Deploy
            ├── 🎙️ Podcast Generation
            ├── 📱 Social Media (Twitter/Telegram/Discord)
            ├── 💰 Monetization (Anki/PDF/Premium)
            └── 🤖 Telegram Bot Push
```

---

## 🔧 Bước 1: Cài Đặt Dependencies

```powershell
cd C:\Users\ThinkPad\TIK

# Core dependencies
pip install python-dotenv requests feedparser google-auth google-auth-oauthlib google-api-python-client python-docx markdown mutagen azure-cognitiveservices-speech

# Podcast
pip install pydub

# Monetization
pip install genanki reportlab

# Telegram Bot
pip install python-telegram-bot

# Social Media
pip install tweepy

# FFmpeg (cho Podcast & Video)
winget install ffmpeg
```

---

## 🔧 Bước 2: Cấu Hình File `.env`

Mở hoặc tạo file `.env` trong thư mục `C:\Users\ThinkPad\TIK\`:

```env
# ==============================================================================
# DAILY KOREAN - FULL AUTOMATION CONFIG
# ==============================================================================

# ========================================
# 🔑 CORE API KEYS (BẮT BUỘC)
# ========================================

# Gemini AI (Tạo nội dung)
GEMINI_API_KEY=your_gemini_api_key

# Azure TTS (Text-to-Speech)
AZURE_SPEECH_KEY=your_azure_speech_key
AZURE_SPEECH_REGION=eastasia

# Pexels (Video background)
PEXELS_API_KEY=your_pexels_api_key

# ========================================
# ☁️ GOOGLE DRIVE UPLOAD
# ========================================

# Folder ID trên Drive để upload
DRIVE_FOLDER_ID=1qNOY6YztD2CV0GqsrFhqmp5SOc6OLI4f

# ========================================
# 📺 YOUTUBE UPLOAD
# ========================================

# Bật/tắt YouTube upload
ENABLE_YOUTUBE_UPLOAD=true

# Privacy: public, unlisted, private
YOUTUBE_PRIVACY=unlisted

# Playlist ID (tùy chọn - để trống nếu không dùng)
YOUTUBE_PLAYLIST_ID=

# ========================================
# 📝 BLOG GENERATION
# ========================================

# Bật/tắt tạo blog (mặc định: true)
ENABLE_BLOG=true

# ========================================
# 🎙️ PODCAST GENERATION
# ========================================

# Bật/tắt tạo podcast (mặc định: true)
ENABLE_PODCAST=true

# ========================================
# 🚀 GITHUB PAGES DEPLOYMENT
# ========================================

# Bật/tắt deploy lên GitHub Pages
ENABLE_GITHUB_DEPLOY=true

# GitHub Personal Access Token (scope: repo)
GH_TOKEN=ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# Repository format: username/repo-name
GH_BLOG_REPO=yourusername/dailykorean-blog

# Branch cho GitHub Pages
GH_BLOG_BRANCH=gh-pages

# Git user info
GH_USER_NAME=cquangduu
GH_USER_EMAIL=cquangdu@knu.ac.kr

# ========================================
# 📱 SOCIAL MEDIA PUBLISHING
# ========================================

# Bật/tắt đăng lên mạng xã hội
ENABLE_SOCIAL_MEDIA=true

# --- Twitter/X ---
TWITTER_API_KEY=your_twitter_api_key
TWITTER_API_SECRET=your_twitter_api_secret
TWITTER_ACCESS_TOKEN=your_access_token
TWITTER_ACCESS_SECRET=your_access_secret
TWITTER_BEARER_TOKEN=your_bearer_token

# --- Telegram Channel ---
TELEGRAM_CHANNEL_ID=@dailykorean

# --- Discord Webhook ---
DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/xxxxx/xxxxx

# --- Email Newsletter ---
EMAIL_SMTP_SERVER=smtp.gmail.com
EMAIL_SMTP_PORT=587
EMAIL_ADDRESS=your_email@gmail.com
EMAIL_PASSWORD=your_app_password

# ========================================
# 💰 MONETIZATION
# ========================================

# Bật/tắt tạo sản phẩm số (mặc định: true)
ENABLE_MONETIZATION=true

# Gumroad (bán sản phẩm số)
GUMROAD_ACCESS_TOKEN=CKKn4klCpmhh_CZjurxvuL1V14XhPVlsS2lRtDzIqJ4
GUMROAD_PRODUCT_ID=aXogzNbLnlABb_L2-6WmqWNUyxRdRt0t3crdI0edig3c

# Patreon (subscription)
PATREON_ACCESS_TOKEN=your_patreon_token
PATREON_CAMPAIGN_ID=your_campaign_id

# ========================================
# 🤖 TELEGRAM BOT PUSH
# ========================================

# Bật/tắt gửi thông báo Telegram
ENABLE_TELEGRAM_PUSH=true

# Bot Token (từ @BotFather)
TELEGRAM_BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrsTUVwxyz

# Admin ID (để nhận thông báo lỗi)
TELEGRAM_ADMIN_ID=your_telegram_user_id
```

---

## 📺 Bước 3: Setup YouTube Upload

### 3.1 Tạo Google Cloud Project

1. Truy cập [Google Cloud Console](https://console.cloud.google.com/)
2. Tạo Project mới: `daily-korean`
3. Vào **APIs & Services** → **Library**
4. Bật **YouTube Data API v3**
5. Bật **Google Drive API**

### 3.2 Tạo OAuth Credentials

1. Vào **APIs & Services** → **Credentials**
2. Click **Create Credentials** → **OAuth client ID**
3. Application type: **Desktop app**
4. Download JSON → đổi tên thành `client_secrets.json`
5. Đặt file vào thư mục `C:\Users\ThinkPad\TIK\`

### 3.3 Xác Thực Lần Đầu

```powershell
cd C:\Users\ThinkPad\TIK
python main.py
```

Khi chạy lần đầu:
- Browser mở lên → Đăng nhập Google
- Cho phép quyền YouTube + Drive
- File `youtube_token.json` và `drive_token.json` được tạo

---

## 🚀 Bước 4: Setup GitHub Pages

### 4.1 Tạo Repository

1. Đăng nhập [GitHub](https://github.com)
2. Tạo repo mới: `dailykorean-blog`
3. Để repo **Public** (cần cho GitHub Pages miễn phí)

### 4.2 Bật GitHub Pages

1. Vào repo → **Settings** → **Pages**
2. Source: **Deploy from a branch**
3. Branch: `gh-pages` / `root`
4. Save

### 4.3 Tạo Personal Access Token

1. Vào [GitHub Settings → Developer settings → Personal access tokens](https://github.com/settings/tokens)
2. **Generate new token (classic)**
3. Chọn scope: `repo` (full control)
4. Copy token → thêm vào `.env`:

```env
GH_TOKEN=ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
GH_BLOG_REPO=yourusername/dailykorean-blog
```

---

## 📱 Bước 5: Setup Twitter/X

### 5.1 Đăng Ký Developer Account

1. Truy cập [Twitter Developer Portal](https://developer.twitter.com/)
2. Apply for **Elevated Access** (miễn phí, cần chờ duyệt)

### 5.2 Tạo Project & App

1. Tạo Project mới
2. Tạo App trong Project
3. Vào **Keys and tokens** → Generate:
   - API Key & Secret
   - Access Token & Secret
   - Bearer Token

### 5.3 Thêm Vào .env

```env
TWITTER_API_KEY=xxxxxxxxxxxxxxxxxxxxxxxx
TWITTER_API_SECRET=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWITTER_ACCESS_TOKEN=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWITTER_ACCESS_SECRET=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWITTER_BEARER_TOKEN=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

---

## 🤖 Bước 6: Setup Telegram Bot

### 6.1 Tạo Bot

1. Mở Telegram, tìm **@BotFather**
2. Gửi `/newbot`
3. Đặt tên: `DAILY KOREAN Bot`
4. Đặt username: `dailykorean_bot`
5. Nhận token

### 6.2 Tạo Channel

1. Tạo Telegram Channel mới
2. Đặt tên: `DAILY KOREAN`
3. Username: `@dailykorean`
4. Add bot vào channel làm **Admin**
5. Cho bot quyền **Post Messages**

### 6.3 Thêm Vào .env

```env
TELEGRAM_BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrsTUVwxyz
TELEGRAM_CHANNEL_ID=@dailykorean
ENABLE_TELEGRAM_PUSH=true
```

---

## 💬 Bước 7: Setup Discord Webhook

### 7.1 Tạo Webhook

1. Vào Discord Server của bạn
2. **Server Settings** → **Integrations** → **Webhooks**
3. Click **New Webhook**
4. Đặt tên: `DAILY KOREAN Bot`
5. Chọn channel để post
6. Copy **Webhook URL**

### 7.2 Thêm Vào .env

```env
DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/xxxxx/xxxxx
```

---

## 💰 Bước 8: Setup Monetization

### 8.1 Gumroad (Bán PDF/Anki)

1. Đăng ký [Gumroad](https://gumroad.com/)
2. Tạo sản phẩm: "TOPIK Vocabulary Pack"
3. Vào **Settings** → **Advanced** → **Create Application**
4. Copy Access Token

```env
GUMROAD_ACCESS_TOKEN=your_token
```

### 8.2 Patreon (Subscription)

1. Đăng ký [Patreon Creator](https://www.patreon.com/)
2. Tạo các tiers:
   - Free: Daily vocab
   - $5/mo: Anki + PDF
   - $15/mo: Video lessons
3. Vào **Settings** → **Developers** → Create API Client

```env
PATREON_ACCESS_TOKEN=your_token
PATREON_CAMPAIGN_ID=your_campaign_id
```

---

## 🎙️ Bước 9: Setup Podcast

### 9.1 Cài FFmpeg

```powershell
winget install ffmpeg
```

### 9.2 Đăng Ký Spotify for Podcasters

1. Truy cập [Spotify for Podcasters](https://podcasters.spotify.com/)
2. Tạo podcast mới: "DAILY KOREAN"
3. Submit RSS feed URL: `https://yourdomain.com/podcast/rss.xml`

---

## ⏰ Bước 10: Chạy Tự Động Hàng Ngày

### Windows Task Scheduler

1. Mở **Task Scheduler**
2. **Create Task**
3. Cấu hình:
   - Name: `DAILY KOREAN Pipeline`
   - Trigger: Daily at 6:00 AM
   - Action: Start a program
     - Program: `python`
     - Arguments: `C:\Users\ThinkPad\TIK\main.py`
     - Start in: `C:\Users\ThinkPad\TIK`

### PowerShell Script (Tùy chọn)

Tạo file `run_daily.ps1`:

```powershell
# DAILY KOREAN - Daily Run Script
$ErrorActionPreference = "Continue"

# Set working directory
Set-Location "C:\Users\ThinkPad\TIK"

# Log file
$logFile = "logs\daily_$(Get-Date -Format 'yyyy-MM-dd').log"

# Run pipeline
Write-Host "🚀 Starting DAILY KOREAN Pipeline..."
python main.py 2>&1 | Tee-Object -FilePath $logFile

Write-Host "✅ Pipeline completed! Log saved to $logFile"
```

---

## ✅ Bước 11: Kiểm Tra Cấu Hình

Chạy test để kiểm tra tất cả module:

```powershell
cd C:\Users\ThinkPad\TIK
python -c "
import os
from dotenv import load_dotenv
load_dotenv()

print('=' * 60)
print('DAILY KOREAN - Configuration Check')
print('=' * 60)

# Core
print(f'✓ GEMINI_API_KEY: {\"OK\" if os.getenv(\"GEMINI_API_KEY\") else \"❌ MISSING\"}')
print(f'✓ AZURE_SPEECH_KEY: {\"OK\" if os.getenv(\"AZURE_SPEECH_KEY\") else \"❌ MISSING\"}')
print(f'✓ PEXELS_API_KEY: {\"OK\" if os.getenv(\"PEXELS_API_KEY\") else \"❌ MISSING\"}')

# Google
print(f'✓ DRIVE_FOLDER_ID: {\"OK\" if os.getenv(\"DRIVE_FOLDER_ID\") else \"❌ MISSING\"}')
print(f'✓ client_secrets.json: {\"OK\" if os.path.exists(\"client_secrets.json\") else \"❌ MISSING\"}')

# YouTube
yt = os.getenv('ENABLE_YOUTUBE_UPLOAD', 'false').lower() == 'true'
print(f'✓ ENABLE_YOUTUBE_UPLOAD: {\"ON ✅\" if yt else \"OFF\"}')

# Blog
blog = os.getenv('ENABLE_BLOG', 'true').lower() == 'true'
print(f'✓ ENABLE_BLOG: {\"ON ✅\" if blog else \"OFF\"}')

# Podcast
podcast = os.getenv('ENABLE_PODCAST', 'true').lower() == 'true'
print(f'✓ ENABLE_PODCAST: {\"ON ✅\" if podcast else \"OFF\"}')

# GitHub
gh = os.getenv('ENABLE_GITHUB_DEPLOY', 'false').lower() == 'true'
print(f'✓ ENABLE_GITHUB_DEPLOY: {\"ON ✅\" if gh else \"OFF\"}')
if gh:
    print(f'  └─ GH_TOKEN: {\"OK\" if os.getenv(\"GH_TOKEN\") else \"❌ MISSING\"}')
    print(f'  └─ GH_BLOG_REPO: {os.getenv(\"GH_BLOG_REPO\", \"❌ MISSING\")}')

# Social Media
social = os.getenv('ENABLE_SOCIAL_MEDIA', 'false').lower() == 'true'
print(f'✓ ENABLE_SOCIAL_MEDIA: {\"ON ✅\" if social else \"OFF\"}')
if social:
    print(f'  └─ TWITTER: {\"OK\" if os.getenv(\"TWITTER_API_KEY\") else \"❌ MISSING\"}')
    print(f'  └─ DISCORD: {\"OK\" if os.getenv(\"DISCORD_WEBHOOK_URL\") else \"❌ MISSING\"}')

# Monetization
money = os.getenv('ENABLE_MONETIZATION', 'true').lower() == 'true'
print(f'✓ ENABLE_MONETIZATION: {\"ON ✅\" if money else \"OFF\"}')

# Telegram
tg = os.getenv('ENABLE_TELEGRAM_PUSH', 'false').lower() == 'true'
print(f'✓ ENABLE_TELEGRAM_PUSH: {\"ON ✅\" if tg else \"OFF\"}')
if tg:
    print(f'  └─ BOT_TOKEN: {\"OK\" if os.getenv(\"TELEGRAM_BOT_TOKEN\") else \"❌ MISSING\"}')
    print(f'  └─ CHANNEL_ID: {os.getenv(\"TELEGRAM_CHANNEL_ID\", \"❌ MISSING\")}')

print('=' * 60)
"
```

---

## 🏃 Bước 12: Chạy Pipeline

```powershell
cd C:\Users\ThinkPad\TIK
python main.py
```

### Output Mong Đợi:

```
============================================================
🚀 DAILY KOREAN CONTENT PIPELINE — 2026-02-02
============================================================
Phase 1: ✅ Tin tức đã thu thập
Phase 2: ✅ Bài văn mẫu đã tạo
Phase 3: ✅ 4 TikTok scripts đã tạo
Phase 4: ✅ Deep Dive script đã tạo
Phase 5: ✅ Audio TTS đã tạo
Phase 6: ✅ 5/5 videos rendered
------------------------------------------------------------
☁️ Google Drive: ✅ Uploaded
📺 YouTube: ✅ 5/5 uploaded
📝 Blog: ✅ Generated
🚀 GitHub: ✅ Deployed
🎙️ Podcast: ✅ Generated
📱 Social: ✅ Twitter, Telegram, Discord
💰 Products: ✅ Anki, PDF
🤖 Telegram: ✅ Push sent
============================================================
🏁 HOÀN THÀNH — Toàn bộ pipeline đã chạy xong.
============================================================
```

---

## 🔥 Quick Start - Bật Tất Cả Ngay

Copy và paste vào `.env`:

```env
# ===== QUICK START - ALL MODULES ENABLED =====

# Core (BẮT BUỘC - điền key của bạn)
GEMINI_API_KEY=your_key_here
AZURE_SPEECH_KEY=your_key_here
AZURE_SPEECH_REGION=eastasia
PEXELS_API_KEY=your_key_here

# Google Drive (BẮT BUỘC)
DRIVE_FOLDER_ID=your_folder_id

# YouTube (ON)
ENABLE_YOUTUBE_UPLOAD=true
YOUTUBE_PRIVACY=unlisted

# Blog (ON)
ENABLE_BLOG=true

# Podcast (ON)
ENABLE_PODCAST=true

# GitHub (OFF - bật sau khi setup)
ENABLE_GITHUB_DEPLOY=false
GH_TOKEN=
GH_BLOG_REPO=

# Social Media (OFF - bật sau khi setup)
ENABLE_SOCIAL_MEDIA=false
TWITTER_API_KEY=
DISCORD_WEBHOOK_URL=

# Monetization (ON)
ENABLE_MONETIZATION=true

# Telegram Push (OFF - bật sau khi setup)
ENABLE_TELEGRAM_PUSH=false
TELEGRAM_BOT_TOKEN=
TELEGRAM_CHANNEL_ID=
```

---

## 📞 Troubleshooting

### Lỗi `invalid_scope: Bad Request`
- Xóa file `drive_token.json` và chạy lại
- Browser sẽ mở để xác thực lại

### Lỗi `genanki not installed`
```powershell
pip install genanki
```

### Lỗi `No module named 'reportlab'`
```powershell
pip install reportlab
```

### Lỗi `No audio segments found` (Podcast)
- Đảm bảo Phase 5 (TTS) chạy thành công
- Kiểm tra thư mục `topik-video/public/assets/`

### Lỗi YouTube quota exceeded
- YouTube API có quota 10,000 units/ngày
- Upload 1 video = 1600 units
- Request quota increase tại Google Cloud Console

### Lỗi Twitter rate limit
- Twitter có giới hạn 50 tweets/15 phút
- Chờ 15 phút rồi thử lại

---

## �️ PHẦN 2: CHẠY TỰ ĐỘNG TRÊN MÁY ẢO (VPS)

> Hướng dẫn deploy lên VPS để chạy 24/7 tự động mỗi ngày

---

### 🌐 Bước 1: Chọn VPS Provider

| Provider | Giá/tháng | RAM | CPU | Ghi chú |
|----------|-----------|-----|-----|---------|
| **DigitalOcean** | $6-12 | 1-2GB | 1-2 vCPU | Khuyên dùng |
| **Vultr** | $5-10 | 1-2GB | 1 vCPU | Rẻ nhất |
| **Linode** | $5-10 | 1-2GB | 1 vCPU | Ổn định |
| **AWS Lightsail** | $5-10 | 1-2GB | 1 vCPU | Dễ scale |
| **Google Cloud** | $5-15 | 1-2GB | 1 vCPU | Free tier |
| **Contabo** | $6-8 | 4GB | 2 vCPU | Giá rẻ nhất |

**Yêu cầu tối thiểu:**
- **RAM**: 2GB (để render video)
- **Storage**: 20GB SSD
- **OS**: Ubuntu 22.04 LTS

---

### 🔧 Bước 2: Setup VPS (Ubuntu 22.04)

#### 2.1 SSH vào VPS

```bash
ssh root@your_vps_ip
```

#### 2.2 Cập nhật hệ thống

```bash
apt update && apt upgrade -y
```

#### 2.3 Cài đặt dependencies hệ thống

```bash
# Python 3.11
apt install -y python3.11 python3.11-venv python3-pip

# Node.js 20 (cho Remotion)
curl -fsSL https://deb.nodesource.com/setup_20.x | bash -
apt install -y nodejs

# FFmpeg (cho video/audio processing)
apt install -y ffmpeg

# Chrome/Chromium (cho Remotion headless render)
apt install -y chromium-browser

# Git
apt install -y git

# Các thư viện cần thiết khác
apt install -y build-essential libcairo2-dev libpango1.0-dev libjpeg-dev libgif-dev librsvg2-dev
```

#### 2.4 Tạo user riêng (không dùng root)

```bash
adduser dailykorean
usermod -aG sudo dailykorean
su - dailykorean
```

---

### 📁 Bước 3: Clone Project

```bash
cd ~
git clone https://github.com/yourusername/TIK.git
cd TIK
```

Hoặc upload từ máy local:

#### ⚡ Cách 1: Dùng Script Deploy (Khuyên dùng)

Script này tự động loại bỏ `node_modules`, `__pycache__`, `.git`, `build`... giúp upload nhanh hơn 10-20 lần!

```powershell
# Từ máy Windows:
cd C:\Users\ThinkPad\TIK
.\deploy_to_vps.ps1 -VpsIP "your_vps_ip" -VpsUser "dailykorean"
```

#### 🐌 Cách 2: SCP truyền thống (CHẬM - không khuyên dùng)

```bash
# ⚠️ CẢNH BÁO: Sẽ upload cả node_modules, rất chậm!
scp -r C:\Users\ThinkPad\TIK dailykorean@your_vps_ip:~/
```

#### 🚀 Cách 3: Rsync với exclude (Linux/WSL)

```bash
# Dùng rsync để loại trừ file rác
rsync -avz --progress \
    --exclude='node_modules' \
    --exclude='__pycache__' \
    --exclude='.git' \
    --exclude='build' \
    --exclude='venv' \
    --exclude='.venv' \
    --exclude='temp_processing' \
    --exclude='logs' \
    --exclude='*.pyc' \
    --exclude='*.log' \
    --exclude='*.mp4' \
    --exclude='*.mp3' \
    /mnt/c/Users/ThinkPad/TIK/ dailykorean@your_vps_ip:~/TIK/
```

#### 📦 Cách 4: Tạo archive sạch rồi upload

```powershell
# Bước 1: Tạo file .tar.gz loại bỏ rác (trong WSL hoặc Git Bash)
cd /mnt/c/Users/ThinkPad
tar --exclude='node_modules' \
    --exclude='__pycache__' \
    --exclude='.git' \
    --exclude='build' \
    --exclude='venv' \
    --exclude='temp_processing' \
    --exclude='logs' \
    --exclude='*.pyc' \
    --exclude='*.mp4' \
    -czvf TIK_clean.tar.gz TIK/

# Bước 2: Upload file nén
scp TIK_clean.tar.gz dailykorean@your_vps_ip:~/

# Bước 3: Giải nén trên VPS
ssh dailykorean@your_vps_ip "cd ~ && tar -xzvf TIK_clean.tar.gz"
```

---

### 🐍 Bước 4: Setup Python Environment

```bash
cd ~/TIK

# Tạo virtual environment
python3.11 -m venv venv
source venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Install thêm nếu chưa có
pip install python-dotenv requests feedparser google-auth google-auth-oauthlib google-api-python-client python-docx markdown mutagen azure-cognitiveservices-speech pydub genanki reportlab python-telegram-bot tweepy
```

---

### 📦 Bước 5: Setup Remotion (Node.js)

```bash
cd ~/TIK/topik-video

# Install npm packages (dùng --legacy-peer-deps để tránh lỗi React version)
npm install --legacy-peer-deps

# Hoặc tạo file .npmrc để fix vĩnh viễn
echo "legacy-peer-deps=true" > .npmrc
npm install

# Test Remotion
npx remotion --version
```

> ⚠️ **Lưu ý**: Nếu gặp lỗi `ERESOLVE could not resolve` do xung đột React 18/19, thêm flag `--legacy-peer-deps`

---

### 🔑 Bước 6: Upload Credentials & Config

#### 6.1 Upload file .env

```bash
# Từ máy Windows:
scp C:\Users\ThinkPad\TIK\.env dailykorean@your_vps_ip:~/TIK/
```

#### 6.2 Upload client_secrets.json

```bash
scp C:\Users\ThinkPad\TIK\client_secrets.json dailykorean@your_vps_ip:~/TIK/
```

#### 6.3 Upload tokens đã xác thực

```bash
# Nếu đã có token từ máy local
scp C:\Users\ThinkPad\TIK\youtube_token.json dailykorean@your_vps_ip:~/TIK/
scp C:\Users\ThinkPad\TIK\drive_token.json dailykorean@your_vps_ip:~/TIK/
```

> ⚠️ **Quan trọng**: Upload tokens đã xác thực từ máy local vì VPS không có browser để OAuth

---

### 🧪 Bước 7: Test Chạy Thủ Công

```bash
cd ~/TIK
source venv/bin/activate

# Test chạy pipeline
python main.py
```

Kiểm tra output:
- Videos được render trong `topik-video/public/`
- Upload lên Drive thành công
- Blog được tạo

---

### ⏰ Bước 8: Setup Cron Job (Chạy Tự Động)

#### 8.1 Tạo script wrapper

```bash
nano ~/TIK/run_daily.sh
```

Nội dung:

```bash
#!/bin/bash
# ============================================
# DAILY KOREAN - Daily Automation Script
# ============================================

# Set working directory
cd /home/dailykorean/TIK

# Activate virtual environment
source venv/bin/activate

# Set environment variables
export PATH=$PATH:/usr/bin:/usr/local/bin
export DISPLAY=:99

# Log file
LOG_FILE="/home/dailykorean/TIK/logs/daily_$(date +%Y-%m-%d).log"
mkdir -p /home/dailykorean/TIK/logs

# Run pipeline
echo "========================================" >> $LOG_FILE
echo "Starting DAILY KOREAN Pipeline at $(date)" >> $LOG_FILE
echo "========================================" >> $LOG_FILE

python main.py >> $LOG_FILE 2>&1

echo "========================================" >> $LOG_FILE
echo "Pipeline completed at $(date)" >> $LOG_FILE
echo "========================================" >> $LOG_FILE

# Optional: Send notification
# curl -s -X POST "https://api.telegram.org/bot$TELEGRAM_BOT_TOKEN/sendMessage" \
#     -d "chat_id=$TELEGRAM_ADMIN_ID" \
#     -d "text=✅ DAILY KOREAN Pipeline completed at $(date)"
```

Cấp quyền thực thi:

```bash
chmod +x ~/TIK/run_daily.sh
```

#### 8.2 Setup Cron

```bash
crontab -e
```

Thêm dòng sau (chạy lúc 6:00 AM mỗi ngày theo giờ VPS):

```cron
# DAILY KOREAN - Chạy mỗi ngày lúc 6:00 AM
0 6 * * * /home/dailykorean/TIK/run_daily.sh

# Hoặc chạy 2 lần/ngày (6:00 AM và 6:00 PM)
# 0 6,18 * * * /home/dailykorean/TIK/run_daily.sh

# Dọn dẹp logs cũ (giữ 7 ngày)
0 0 * * * find /home/dailykorean/TIK/logs -name "*.log" -mtime +7 -delete
```

#### 8.3 Kiểm tra cron

```bash
# Xem danh sách cron jobs
crontab -l

# Xem log cron
tail -f /var/log/syslog | grep CRON
```

---

### 🔄 Bước 9: Setup Systemd Service (Tùy Chọn)

Nếu muốn chạy như service thay vì cron:

```bash
sudo nano /etc/systemd/system/dailykorean.service
```

Nội dung:

```ini
[Unit]
Description=DAILY KOREAN Content Pipeline
After=network.target

[Service]
Type=oneshot
User=dailykorean
WorkingDirectory=/home/dailykorean/TIK
ExecStart=/home/dailykorean/TIK/run_daily.sh
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

Setup timer:

```bash
sudo nano /etc/systemd/system/dailykorean.timer
```

Nội dung:

```ini
[Unit]
Description=Run DAILY KOREAN Pipeline Daily

[Timer]
OnCalendar=*-*-* 06:00:00
Persistent=true

[Install]
WantedBy=timers.target
```

Kích hoạt:

```bash
sudo systemctl daemon-reload
sudo systemctl enable dailykorean.timer
sudo systemctl start dailykorean.timer

# Kiểm tra status
sudo systemctl status dailykorean.timer
sudo systemctl list-timers
```

---

### 📊 Bước 10: Monitoring & Logs

#### 10.1 Xem logs

```bash
# Log hôm nay
tail -f ~/TIK/logs/daily_$(date +%Y-%m-%d).log

# Log tất cả
ls -la ~/TIK/logs/
```

#### 10.2 Setup Telegram Notification

Thêm vào cuối `run_daily.sh`:

```bash
# Send completion notification
TELEGRAM_BOT_TOKEN="your_bot_token"
TELEGRAM_ADMIN_ID="your_admin_id"

curl -s -X POST "https://api.telegram.org/bot$TELEGRAM_BOT_TOKEN/sendMessage" \
    -d "chat_id=$TELEGRAM_ADMIN_ID" \
    -d "text=✅ DAILY KOREAN Pipeline hoàn thành lúc $(date '+%Y-%m-%d %H:%M:%S')"
```

#### 10.3 Setup Error Notification

Thêm error handling:

```bash
# Trong run_daily.sh
if python main.py >> $LOG_FILE 2>&1; then
    # Success notification
    curl -s -X POST "https://api.telegram.org/bot$TELEGRAM_BOT_TOKEN/sendMessage" \
        -d "chat_id=$TELEGRAM_ADMIN_ID" \
        -d "text=✅ Pipeline thành công!"
else
    # Error notification
    curl -s -X POST "https://api.telegram.org/bot$TELEGRAM_BOT_TOKEN/sendMessage" \
        -d "chat_id=$TELEGRAM_ADMIN_ID" \
        -d "text=❌ Pipeline thất bại! Kiểm tra logs."
fi
```

---

### 🔒 Bước 11: Bảo Mật VPS

```bash
# Đổi SSH port (tùy chọn)
sudo nano /etc/ssh/sshd_config
# Đổi Port 22 thành Port 2222

# Setup UFW Firewall
sudo ufw allow OpenSSH
sudo ufw allow 2222/tcp  # Nếu đổi port
sudo ufw enable

# Disable root login
sudo nano /etc/ssh/sshd_config
# PermitRootLogin no

sudo systemctl restart sshd
```

---

### 💾 Bước 12: Backup Tự Động

```bash
nano ~/backup_daily.sh
```

Nội dung:

```bash
#!/bin/bash
# Backup tokens và data quan trọng

BACKUP_DIR="/home/dailykorean/backups"
mkdir -p $BACKUP_DIR

# Backup tokens
cp ~/TIK/youtube_token.json $BACKUP_DIR/
cp ~/TIK/drive_token.json $BACKUP_DIR/
cp ~/TIK/.env $BACKUP_DIR/

# Backup final_data.json (7 ngày gần nhất)
cp ~/TIK/topik-video/public/final_data.json $BACKUP_DIR/final_data_$(date +%Y-%m-%d).json

# Xóa backup cũ hơn 30 ngày
find $BACKUP_DIR -name "final_data_*.json" -mtime +30 -delete

echo "Backup completed at $(date)"
```

Thêm vào cron:

```bash
# Backup hàng ngày lúc 23:00
0 23 * * * /home/dailykorean/backup_daily.sh
```

---

### 🚀 Quick Deploy Script

Tạo script deploy tự động từ đầu:

```bash
nano ~/deploy_dailykorean.sh
```

```bash
#!/bin/bash
# ============================================
# DAILY KOREAN - One-Click VPS Deploy
# ============================================

echo "🚀 Deploying DAILY KOREAN..."

# Update system
sudo apt update && sudo apt upgrade -y

# Install dependencies
sudo apt install -y python3.11 python3.11-venv python3-pip nodejs npm ffmpeg chromium-browser git

# Create user if not exists
if ! id "dailykorean" &>/dev/null; then
    sudo adduser --disabled-password --gecos "" dailykorean
fi

# Clone/Update repo
cd /home/dailykorean
if [ -d "TIK" ]; then
    cd TIK && git pull
else
    git clone https://github.com/yourusername/TIK.git
    cd TIK
fi

# Setup Python
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Setup Node.js
cd topik-video
npm install
cd ..

# Create logs directory
mkdir -p logs

# Setup cron
(crontab -l 2>/dev/null; echo "0 6 * * * /home/dailykorean/TIK/run_daily.sh") | crontab -

echo "✅ Deployment complete!"
echo "📝 Don't forget to:"
echo "   1. Upload .env file"
echo "   2. Upload client_secrets.json"
echo "   3. Upload youtube_token.json and drive_token.json"
```

---

### 📋 Checklist Deploy VPS

- [ ] Mua VPS (DigitalOcean/Vultr/Contabo)
- [ ] SSH vào VPS
- [ ] Cài đặt Python 3.11, Node.js 20, FFmpeg
- [ ] Clone project
- [ ] Setup virtual environment
- [ ] Upload .env và tokens
- [ ] Test chạy thủ công
- [ ] Setup cron job
- [ ] Test cron chạy
- [ ] Setup Telegram notification
- [ ] Setup backup

---

## �📧 Support

- Email: dailykoreanluyenviettopik@gmail.com
- Telegram: @dailykorean
- Discord: discord.gg/dailykorean

---

*Được tạo bởi DAILY KOREAN Automation System - v2.0*
*Cập nhật: 2026-02-02*
