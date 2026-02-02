# 🚀 DAILY KOREAN — Hướng Dẫn Triển Khai Tự Động

## 📋 Tổng Quan

Hướng dẫn này giúp bạn triển khai hệ thống DAILY KOREAN tự động hoàn toàn trên máy ảo (VPS/Cloud).

### Kiến trúc hệ thống:
```
┌─────────────────────────────────────────────────────────────────────┐
│                        DAILY KOREAN SYSTEM                          │
├─────────────────────────────────────────────────────────────────────┤
│  [Cron/Timer]                                                       │
│       ↓                                                             │
│  [main.py] → Fetch news → Generate content → TTS audio              │
│       ↓                                                             │
│  [Remotion] → Render 4 TikTok + 1 YouTube video                     │
│       ↓                                                             │
│  [youtube_uploader.py] → Upload YouTube                             │
│  [social_publisher.py] → Upload TikTok/Facebook/Instagram           │
│  [blog_generator.py] → Generate blog post                           │
│  [telegram_bot.py] → Send to Telegram channel                       │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 📝 BƯỚC 1: Chuẩn Bị API Keys

### 1.1 Tạo file `.env`

```bash
# Copy từ file mẫu
cp .env.example .env
```

### 1.2 Điền các API keys:

| API | Cách lấy | Link |
|-----|----------|------|
| **GEMINI_API_KEY** | Google AI Studio | https://aistudio.google.com/app/apikey |
| **AZURE_SPEECH_KEY** | Azure Portal → Cognitive Services → Speech | https://portal.azure.com |
| **PEXELS_API_KEY** | Pexels → API | https://www.pexels.com/api/ |
| **TELEGRAM_BOT_TOKEN** | @BotFather trên Telegram | https://t.me/BotFather |

### 1.3 Nội dung file `.env`:

```env
# ══════════════════════════════════════════════════════════════════
# DAILY KOREAN — Environment Variables
# ══════════════════════════════════════════════════════════════════

# === AI Content Generation ===
GEMINI_API_KEY=AIza...your_key_here...

# === Text-to-Speech (Azure) ===
AZURE_SPEECH_KEY=your_azure_key
AZURE_SPEECH_REGION=koreacentral

# === Video Background (Pexels) ===
PEXELS_API_KEY=your_pexels_key

# === YouTube Upload ===
ENABLE_YOUTUBE_UPLOAD=true
YOUTUBE_PRIVACY=unlisted
# YOUTUBE_PLAYLIST_ID=PLxxxxx

# === Telegram ===
TELEGRAM_BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrsTUVwxyz
TELEGRAM_CHANNEL_ID=@dailykorean_channel

# === GitHub (for blog deployment) ===
GH_TOKEN=ghp_xxxxxxxxxxxx
GH_BLOG_REPO=username/dailykorean-blog
```

---

## 📝 BƯỚC 2: Chuẩn Bị Credentials Files

### 2.1 Google OAuth (YouTube Upload)

#### Bước 2.1.1: Tạo OAuth Client ID
1. Vào [Google Cloud Console](https://console.cloud.google.com)
2. Tạo project mới hoặc chọn project có sẵn
3. Bật **YouTube Data API v3** tại API Library
4. Vào **Credentials** → **Create Credentials** → **OAuth client ID**
5. Chọn **Desktop App**
6. Download file JSON → đổi tên thành `client_secrets.json`

#### Bước 2.1.2: Tạo token.json (trên máy local)
```bash
# Chạy trên máy local có trình duyệt
cd C:\Users\ThinkPad\TIK
python -c "from youtube_uploader import YouTubeUploader; YouTubeUploader().authenticate()"
```
→ Trình duyệt mở ra → Đăng nhập Google → Cho phép quyền
→ File `token.json` được tạo

### 2.2 Files cần upload lên server:

```
.env                  # API keys
client_secrets.json   # Google OAuth client
token.json           # Google OAuth token (đã authenticate)
```

---

## 📝 BƯỚC 3: Tạo VPS/Droplet

### 3.1 Chọn nhà cung cấp:

| Provider | Plan đề xuất | Giá/tháng |
|----------|--------------|-----------|
| **DigitalOcean** | Basic Droplet 2GB RAM | $12 |
| **Vultr** | Cloud Compute 2GB | $12 |
| **Linode** | Shared 2GB | $12 |
| **Contabo** | VPS S (4GB) | €4.99 |

### 3.2 Cấu hình tối thiểu:
- **OS**: Ubuntu 22.04 LTS
- **RAM**: 2GB (4GB recommended cho render video)
- **CPU**: 1-2 vCPU
- **Storage**: 50GB SSD
- **Region**: Singapore/Korea (gần Việt Nam)

### 3.3 Tạo Droplet (DigitalOcean):
1. Đăng nhập DigitalOcean
2. Create → Droplets
3. Chọn Ubuntu 22.04 LTS
4. Basic → Regular (2GB/1CPU) 
5. Chọn datacenter: Singapore
6. Authentication: SSH Key (recommended)
7. Create Droplet

---

## 📝 BƯỚC 4: Kết Nối SSH

### 4.1 Từ Windows (PowerShell):
```powershell
# Kết nối SSH
ssh root@<droplet-ip>

# Ví dụ:
ssh root@167.99.123.45
```

### 4.2 Từ Windows (PuTTY):
1. Download PuTTY
2. Host: `<droplet-ip>`
3. Port: 22
4. Connection → SSH → Auth → Private key file
5. Open

---

## 📝 BƯỚC 5: Cài Đặt Trên Server

### 5.1 Upload và chạy script setup:

```bash
# Trên máy local, upload script setup
scp C:\Users\ThinkPad\TIK\setup_digitalocean.sh root@<droplet-ip>:/root/

# SSH vào server
ssh root@<droplet-ip>

# Chạy script
chmod +x /root/setup_digitalocean.sh
bash /root/setup_digitalocean.sh
```

### 5.2 Hoặc cài đặt thủ công:

```bash
# === 1. Update system ===
apt update && apt upgrade -y

# === 2. Install dependencies ===
apt install -y python3 python3-pip python3-venv ffmpeg git curl wget htop screen

# === 3. Install Node.js 20 ===
curl -fsSL https://deb.nodesource.com/setup_20.x | bash -
apt install -y nodejs

# === 4. Tạo user ===
useradd -m -s /bin/bash dailykorean
usermod -aG sudo dailykorean

# === 5. Setup thư mục ===
mkdir -p /home/dailykorean/app
cd /home/dailykorean/app

# === 6. Clone repository ===
git clone https://github.com/your-username/daily-korean.git .
# Hoặc upload files thủ công

# === 7. Python virtual environment ===
python3 -m venv venv
source venv/bin/activate

# === 8. Install Python packages ===
pip install --upgrade pip
pip install -r requirements.txt

# === 9. Install Remotion ===
cd topik-video
npm install
cd ..

# === 10. Set permissions ===
chown -R dailykorean:dailykorean /home/dailykorean
```

---

## 📝 BƯỚC 6: Upload Files Credentials

### 6.1 Từ máy local (PowerShell):

```powershell
# Upload tất cả files cần thiết
$SERVER = "root@<droplet-ip>"
$REMOTE_DIR = "/home/dailykorean/app"

# Upload .env
scp C:\Users\ThinkPad\TIK\.env ${SERVER}:${REMOTE_DIR}/

# Upload Google credentials
scp C:\Users\ThinkPad\TIK\client_secrets.json ${SERVER}:${REMOTE_DIR}/
scp C:\Users\ThinkPad\TIK\token.json ${SERVER}:${REMOTE_DIR}/

# Upload source code (nếu không dùng git)
scp -r C:\Users\ThinkPad\TIK\*.py ${SERVER}:${REMOTE_DIR}/
scp -r C:\Users\ThinkPad\TIK\topik-video ${SERVER}:${REMOTE_DIR}/
```

### 6.2 Hoặc dùng rsync (nhanh hơn cho nhiều files):

```powershell
# Cài rsync trên Windows (qua Git Bash hoặc WSL)
rsync -avz --exclude='node_modules' --exclude='__pycache__' --exclude='.git' \
  C:\Users\ThinkPad\TIK/ root@68.183.1878:/home/dailykorean/app/
```

---

## 📝 BƯỚC 7: Test Thủ Công

### 7.1 SSH vào server và test:

```bash
# Đăng nhập
ssh root@<droplet-ip>

# Chuyển sang user dailykorean
su - dailykorean
cd /home/dailykorean/app

# Activate virtual environment
source venv/bin/activate

# Test từng bước
python -c "from dotenv import load_dotenv; load_dotenv(); import os; print('GEMINI:', os.getenv('GEMINI_API_KEY')[:10] + '...')"

# Chạy pipeline đầy đủ
python main.py
```

### 7.2 Kiểm tra output:

```bash
# Kiểm tra files được tạo
ls -la topik-video/public/
cat topik-video/public/final_data.json | head -50

# Kiểm tra audio
ls -la topik-video/public/assets/

# Test render video (1 video thử nghiệm)
cd topik-video
npx remotion render TikTok-NewsHealing --props="$(cat public/final_data.json)" out/test_news.mp4
```

---

## 📝 BƯỚC 8: Thiết Lập Tự Động (Cron)

### 8.1 Tạo script chạy hàng ngày:

```bash
cat > /home/dailykorean/run_daily.sh << 'EOF'
#!/bin/bash
# ═══════════════════════════════════════════════════════════════
# DAILY KOREAN — Daily Run Script
# Chạy lúc 6:00 AM KST mỗi ngày
# ═══════════════════════════════════════════════════════════════

set -e

LOG_DIR="/home/dailykorean/logs"
LOG_FILE="$LOG_DIR/daily_$(date +%Y%m%d_%H%M%S).log"
APP_DIR="/home/dailykorean/app"

mkdir -p $LOG_DIR

echo "════════════════════════════════════════════════════════════" >> $LOG_FILE
echo "🚀 DAILY KOREAN — Started at $(date)" >> $LOG_FILE
echo "════════════════════════════════════════════════════════════" >> $LOG_FILE

cd $APP_DIR
source venv/bin/activate

# ─── Phase 1: Generate Content ───
echo "[$(date +%H:%M:%S)] Phase 1: Generating content..." >> $LOG_FILE
python main.py >> $LOG_FILE 2>&1

# ─── Phase 2: Render Videos ───
echo "[$(date +%H:%M:%S)] Phase 2: Rendering videos..." >> $LOG_FILE
cd topik-video

# Render 4 TikTok videos
for comp in TikTok-NewsHealing TikTok-WritingCoach TikTok-VocabQuiz TikTok-GrammarQuiz; do
    echo "  Rendering $comp..." >> $LOG_FILE
    npx remotion render $comp --props="$(cat public/final_data.json)" "out/${comp}.mp4" >> $LOG_FILE 2>&1
done

# Render 1 YouTube video
echo "  Rendering YouTube-DeepDive..." >> $LOG_FILE
npx remotion render YouTube-DeepDive --props="$(cat public/final_data.json)" "out/YouTube-DeepDive.mp4" >> $LOG_FILE 2>&1

cd ..

# ─── Phase 3: Upload Videos ───
echo "[$(date +%H:%M:%S)] Phase 3: Uploading videos..." >> $LOG_FILE
python youtube_uploader.py >> $LOG_FILE 2>&1

# ─── Phase 4: Generate Blog ───
echo "[$(date +%H:%M:%S)] Phase 4: Generating blog..." >> $LOG_FILE
python blog_generator.py >> $LOG_FILE 2>&1

# ─── Phase 5: Send Telegram ───
echo "[$(date +%H:%M:%S)] Phase 5: Sending Telegram notification..." >> $LOG_FILE
python telegram_bot.py >> $LOG_FILE 2>&1

# ─── Cleanup old logs (keep 30 days) ───
find $LOG_DIR -name "daily_*.log" -mtime +30 -delete

echo "════════════════════════════════════════════════════════════" >> $LOG_FILE
echo "✅ DAILY KOREAN — Completed at $(date)" >> $LOG_FILE
echo "════════════════════════════════════════════════════════════" >> $LOG_FILE

exit 0
EOF

chmod +x /home/dailykorean/run_daily.sh
chown dailykorean:dailykorean /home/dailykorean/run_daily.sh
```

### 8.2 Thiết lập Cron:

```bash
# Mở crontab cho user dailykorean
crontab -u dailykorean -e

# Thêm dòng sau (chạy 6:00 AM KST = 21:00 UTC ngày trước):
0 21 * * * /home/dailykorean/run_daily.sh

# Hoặc dùng systemd timer (khuyến nghị):
```

### 8.3 Hoặc dùng Systemd Timer (tốt hơn cron):

```bash
# Tạo service file
cat > /etc/systemd/system/dailykorean.service << 'EOF'
[Unit]
Description=Daily Korean Content Generator
After=network.target

[Service]
Type=oneshot
User=dailykorean
WorkingDirectory=/home/dailykorean/app
ExecStart=/home/dailykorean/run_daily.sh
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

# Tạo timer file
cat > /etc/systemd/system/dailykorean.timer << 'EOF'
[Unit]
Description=Run Daily Korean at 6:00 AM KST

[Timer]
# 21:00 UTC = 06:00 KST (next day)
OnCalendar=*-*-* 21:00:00 UTC
Persistent=true

[Install]
WantedBy=timers.target
EOF

# Enable và start timer
systemctl daemon-reload
systemctl enable dailykorean.timer
systemctl start dailykorean.timer

# Kiểm tra status
systemctl status dailykorean.timer
systemctl list-timers --all
```

---

## 📝 BƯỚC 9: Monitoring & Logs

### 9.1 Xem logs:

```bash
# Xem log mới nhất
tail -f /home/dailykorean/logs/daily_*.log

# Xem log systemd
journalctl -u dailykorean.service -f

# Xem tất cả logs hôm nay
journalctl -u dailykorean.service --since today
```

### 9.2 Kiểm tra disk space:

```bash
# Kiểm tra dung lượng
df -h

# Dọn dẹp videos cũ (giữ 7 ngày)
find /home/dailykorean/app/topik-video/out -name "*.mp4" -mtime +7 -delete

# Dọn dẹp temp files
rm -rf /home/dailykorean/app/temp_processing/*
```

### 9.3 Thiết lập alerting (optional):

```bash
# Gửi email khi job fail
# Thêm vào cuối run_daily.sh:

if [ $? -ne 0 ]; then
    echo "Daily Korean job failed!" | mail -s "❌ Daily Korean Alert" your@email.com
fi
```

---

## 📝 BƯỚC 10: Bảo Mật

### 10.1 Firewall:

```bash
# Chỉ mở SSH và HTTP/HTTPS
ufw allow OpenSSH
ufw allow 80/tcp
ufw allow 443/tcp
ufw enable
```

### 10.2 Fail2ban (chống brute force):

```bash
apt install -y fail2ban
systemctl enable fail2ban
systemctl start fail2ban
```

### 10.3 Tắt root login:

```bash
# Tạo SSH key cho user dailykorean trước
su - dailykorean
ssh-keygen -t ed25519
# Copy public key từ máy local vào ~/.ssh/authorized_keys

# Disable root login
nano /etc/ssh/sshd_config
# Thêm: PermitRootLogin no
systemctl restart sshd
```

---

## 🔧 Troubleshooting

### Lỗi thường gặp:

| Lỗi | Nguyên nhân | Giải pháp |
|-----|-------------|-----------|
| `GEMINI_API_KEY not found` | Chưa load .env | `source venv/bin/activate` trước khi chạy |
| `ffprobe not found` | Chưa cài ffmpeg | `apt install ffmpeg` |
| `npm: command not found` | Chưa cài Node.js | Chạy lại bước cài Node.js |
| `Out of memory` | RAM không đủ render | Nâng cấp droplet lên 4GB hoặc dùng swap |
| `YouTube quota exceeded` | Hết quota API | Chờ 24h hoặc request quota increase |

### Thêm swap (nếu thiếu RAM):

```bash
# Tạo 2GB swap
fallocate -l 2G /swapfile
chmod 600 /swapfile
mkswap /swapfile
swapon /swapfile
echo '/swapfile none swap sw 0 0' >> /etc/fstab
```

---

## 📊 Chi Phí Ước Tính

| Hạng mục | Chi phí/tháng |
|----------|---------------|
| VPS 2GB RAM | $12 |
| Domain (optional) | ~$1 |
| Azure TTS (Free tier) | $0 |
| Gemini API (Free tier) | $0 |
| **Tổng** | **~$13/tháng** |

---

## ✅ Checklist Triển Khai

- [ ] Tạo VPS Ubuntu 22.04
- [ ] SSH vào server
- [ ] Chạy setup script
- [ ] Upload .env, client_secrets.json, token.json
- [ ] Test `python main.py`
- [ ] Test render video
- [ ] Thiết lập cron/systemd timer
- [ ] Kiểm tra logs sau 1 ngày
- [ ] Thiết lập firewall
- [ ] Backup credentials

---

## 🎉 Hoàn Thành!

Sau khi hoàn thành tất cả các bước, hệ thống sẽ tự động:

1. **6:00 AM KST** - Fetch tin tức mới nhất
2. **6:05 AM** - Generate nội dung với Gemini AI
3. **6:10 AM** - Tạo audio TTS với Azure
4. **6:15 AM** - Render 5 videos với Remotion
5. **7:00 AM** - Upload lên YouTube
6. **7:30 AM** - Đăng blog và gửi Telegram

Mỗi ngày, không cần bạn làm gì cả! 🚀
