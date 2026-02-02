# 🇰🇷 DAILY KOREAN (데일리 코리안) — Hệ Thống Tự Động Hoàn Toàn

Hệ thống tự động tạo nội dung học tiếng Hàn TOPIK hàng ngày và phân phối đa kênh.

## 🎯 Tính Năng

| Tính Năng | Mô Tả |
|-----------|-------|
| 📰 **Crawl Tin Tức** | Lấy tin tức Hàn Quốc mới nhất |
| 📝 **Ra Đề TOPIK 54** | Tự động tạo đề thi viết TOPIK |
| ✍️ **Viết Văn Mẫu** | AI viết bài văn mẫu chuẩn |
| 📚 **Phân Tích Từ Vựng** | Giải thích 35+ từ/ngữ pháp mỗi ngày |
| 🎬 **Render 5 Video** | 4 TikTok Shorts + 1 YouTube Deep Dive |
| ☁️ **Upload Drive** | Tự động upload Word + Video |
| 📺 **Upload YouTube** | Auto upload với title, tags, playlist |
| 📝 **Generate Blog** | Tạo blog post SEO-friendly |
| 🎙️ **Generate Podcast** | Tạo episode + RSS feed |
| 📱 **Social Media** | Post Twitter, Telegram, Discord |
| 📧 **Newsletter** | Gửi email cho subscribers |
| 🚀 **Deploy** | Auto deploy blog lên GitHub Pages |

## 📁 Cấu Trúc Dự Án

```
TIK/
├── main.py                 # Pipeline chính
├── youtube_uploader.py     # Upload YouTube
├── blog_generator.py       # Tạo blog posts
├── podcast_generator.py    # Tạo podcast episodes
├── social_publisher.py     # Post social media
├── github_deployer.py      # Deploy GitHub Pages
├── setup_digitalocean.sh   # Setup script cho VPS
├── requirements.txt        # Python dependencies
├── .env.example           # Mẫu cấu hình
├── topik-video/           # Remotion project
│   ├── src/
│   │   ├── components/
│   │   │   ├── NewsHealing.tsx    # Video 1
│   │   │   ├── WritingCoach.tsx   # Video 2
│   │   │   ├── QuizGame.tsx       # Video 3-4
│   │   │   └── DeepDive.tsx       # Video 5
│   │   └── Composition.tsx
│   └── public/
│       ├── final_data.json
│       └── assets/
├── blog_output/           # Generated blog
├── podcast_output/        # Generated podcast
└── temp_processing/       # Temporary files
```

## 🚀 Cài Đặt

### 1. Clone Repository

```bash
git clone https://github.com/yourusername/topik-daily.git
cd topik-daily
```

### 2. Cài Đặt Dependencies

```bash
# Python
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

pip install -r requirements.txt

# Node.js (cho Remotion)
cd topik-video
npm install
cd ..
```

### 3. Cấu Hình

```bash
cp .env.example .env
nano .env  # Điền API keys
```

### 4. Chạy Thử

```bash
python main.py
```

---

## 🔑 Hướng Dẫn Lấy API Keys

### 1. Gemini API Key (BẮT BUỘC)

Gemini AI được dùng để tạo nội dung, đề thi, văn mẫu.

1. Truy cập [Google AI Studio](https://aistudio.google.com/app/apikey)
2. Đăng nhập bằng tài khoản Google
3. Click **"Create API Key"**
4. Chọn project hoặc tạo mới
5. Copy API key (dạng `AIzaSy...`)

```env
GEMINI_API_KEY=AIzaSyCxxxxxxxxxxxxxxxxxxxxx
```

> ⚠️ **Giới hạn miễn phí**: 15 requests/phút, 1,500 requests/ngày

---

### 2. Azure Speech API (BẮT BUỘC - TTS)

Azure TTS được dùng để tạo audio tiếng Hàn chất lượng cao.

1. Truy cập [Azure Portal](https://portal.azure.com/)
2. Tạo tài khoản (có free tier $200 credit)
3. Tìm kiếm **"Speech Services"** → Create
4. Điền thông tin:
   - **Subscription**: Free Trial hoặc Pay-as-you-go
   - **Resource group**: Tạo mới (ví dụ: `topik-resources`)
   - **Region**: `koreacentral` (khuyến nghị) hoặc `eastasia`
   - **Pricing tier**: `F0` (Free - 500,000 ký tự/tháng)
   - **Name**: `topik-speech`
5. Sau khi tạo, vào **Keys and Endpoint**
6. Copy **Key 1** và **Region**

```env
AZURE_SPEECH_KEY=4eVOKBQFxxxxxxxxxxxxxxxxxxxxxx
AZURE_SPEECH_REGION=koreacentral
TTS_VOICE=ko-KR-InJoonNeural
```

> 💡 **Voices khả dụng**:
> - `ko-KR-InJoonNeural` - Giọng nam trẻ (khuyến nghị cho giảng dạy)
> - `ko-KR-SunHiNeural` - Giọng nữ trẻ (khuyến nghị cho tin tức)
> - `ko-KR-JiMinNeural` - Giọng nữ phân tích

---

### 3. Google Drive & YouTube API

#### Bước 1: Tạo Google Cloud Project

1. Truy cập [Google Cloud Console](https://console.cloud.google.com/)
2. Click **"Select a project"** → **"New Project"**
3. Đặt tên: `topik-auto` → Create
4. Chọn project vừa tạo

#### Bước 2: Enable APIs

1. Vào **APIs & Services** → **Library**
2. Tìm và Enable:
   - **Google Drive API**
   - **YouTube Data API v3**

#### Bước 3: Tạo OAuth 2.0 Credentials

1. Vào **APIs & Services** → **Credentials**
2. Click **"Create Credentials"** → **"OAuth client ID"**
3. Nếu chưa có, cấu hình **OAuth consent screen**:
   - User Type: **External**
   - App name: `TOPIK Daily`
   - User support email: Email của bạn
   - Developer contact: Email của bạn
   - Click **"Save and Continue"** qua tất cả bước
   - Ở **Test users**, thêm email Google của bạn
4. Quay lại **Credentials** → **Create Credentials** → **OAuth client ID**
5. Application type: **Desktop app**
6. Name: `TOPIK Daily Desktop`
7. Click **Create** → **Download JSON**
8. Đổi tên file thành `client_secrets.json` và đặt vào thư mục project

```env
DRIVE_FOLDER_ID=1wjinD_gJNBLLHxxxxxxxxxx
ENABLE_YOUTUBE_UPLOAD=true
YOUTUBE_PRIVACY=unlisted
```

#### Bước 4: Lấy Drive Folder ID

1. Vào [Google Drive](https://drive.google.com/)
2. Tạo folder mới: `TOPIK Daily Output`
3. Mở folder, copy ID từ URL:
   ```
   https://drive.google.com/drive/folders/1wjinD_gJNBLLHg5e0b683eSGs63iT5
                                          ↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑
                                          Đây là DRIVE_FOLDER_ID
   ```

#### Bước 5: Xác thực lần đầu

```bash
python main.py
# Trình duyệt sẽ mở để bạn đăng nhập Google
# Chọn tài khoản → Cho phép → Copy code (nếu có)
# token.json sẽ được tạo tự động
```

---

### 4. GitHub Token (cho Blog Deploy)

1. Truy cập [GitHub Settings → Developer Settings → Personal Access Tokens](https://github.com/settings/tokens)
2. Click **"Generate new token (classic)"**
3. Note: `TOPIK Blog Deploy`
4. Chọn scopes:
   - ✅ `repo` (Full control of private repositories)
   - ✅ `workflow` (nếu dùng GitHub Actions)
5. Click **"Generate token"**
6. Copy token (chỉ hiển thị 1 lần!)

```env
GH_TOKEN=ghp_jzpEbsi894xxxxxxxxxxxxxxxxxxxxxx
GH_REPO=username/topik-daily-blog
```

---

### 5. Telegram Bot (Tùy chọn)

1. Mở Telegram, tìm [@BotFather](https://t.me/BotFather)
2. Gửi `/newbot`
3. Đặt tên bot: `TOPIK Daily Bot`
4. Đặt username: `topik_daily_bot`
5. Copy **bot token**
6. Tạo channel/group, thêm bot làm admin
7. Lấy Chat ID:
   - Thêm bot [@userinfobot](https://t.me/userinfobot) vào channel
   - Hoặc gửi tin nhắn, rồi truy cập: `https://api.telegram.org/bot<TOKEN>/getUpdates`

```env
TELEGRAM_BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrsTUVwxyz
TELEGRAM_CHANNEL_ID=-1001234567890
```

---

### 6. Discord Webhook (Tùy chọn)

1. Mở Discord server của bạn
2. Vào **Server Settings** → **Integrations** → **Webhooks**
3. Click **"New Webhook"**
4. Đặt tên: `TOPIK Daily`
5. Chọn channel để post
6. Copy **Webhook URL**

```env
DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/1234567890/abcdefghijklmnop
```

---

### 7. Pexels API (Video Background)

Pexels cung cấp video stock miễn phí cho background.

1. Truy cập [Pexels API](https://www.pexels.com/api/)
2. Click **"Get Started"** → Đăng ký/Đăng nhập
3. Vào **"Your API Key"**
4. Copy API key

```env
PEXELS_API_KEY=j7VZt806erlXTb0Kxxxxxxxxxxxxxxxxxx
```

---

### 8. Naver API (Tùy chọn - Từ điển)

1. Truy cập [Naver Developers](https://developers.naver.com/apps/)
2. Đăng nhập bằng tài khoản Naver
3. Click **"Application 등록"**
4. Điền thông tin:
   - 애플리케이션 이름: `TOPIK Daily`
   - 사용 API: **Papago 번역** hoặc **검색**
5. Copy **Client ID** và **Client Secret**

```env
NAVER_CLIENT_ID=dq1t1csBxxxxxx
NAVER_CLIENT_SECRET=pmGdPMxxxx
```

---

## 📋 File .env Mẫu Hoàn Chỉnh

```env
# ========== BẮT BUỘC ==========
GEMINI_API_KEY=AIzaSyCxxxxxxxxxxxxxxxxxxxxx
AZURE_SPEECH_KEY=4eVOKBQFxxxxxxxxxxxxxxxxxxxxxx
AZURE_SPEECH_REGION=koreacentral
TTS_VOICE=ko-KR-InJoonNeural
DRIVE_FOLDER_ID=1wjinD_xxxxxxxxxxxxxxx

# ========== YOUTUBE ==========
ENABLE_YOUTUBE_UPLOAD=false
YOUTUBE_PRIVACY=unlisted
YOUTUBE_PLAYLIST_ID=

# ========== BLOG & PODCAST ==========
ENABLE_BLOG=true
ENABLE_PODCAST=true
GH_TOKEN=ghp_xxxxxxxxxxxxxxxxxxxxxx
GH_REPO=username/topik-daily-blog

# ========== SOCIAL MEDIA (Tùy chọn) ==========
TELEGRAM_BOT_TOKEN=
TELEGRAM_CHANNEL_ID=
DISCORD_WEBHOOK_URL=

# ========== VIDEO ASSETS ==========
PEXELS_API_KEY=xxxxxxxxxxxxxxxxxxxxxxx

# ========== OPTIONAL ==========
NAVER_CLIENT_ID=
NAVER_CLIENT_SECRET=
EMAIL_ENABLED=false
EMAIL_ADDRESS=
EMAIL_PASSWORD=
```

---

## ⚙️ Cấu Hình Chi Tiết

> 💡 Xem phần **🔑 Hướng Dẫn Lấy API Keys** ở trên để biết cách lấy từng key.

### Google APIs

1. Vào [Google Cloud Console](https://console.cloud.google.com/)
2. Tạo project mới hoặc chọn project có sẵn
3. Enable các APIs:
   - Google Drive API
   - YouTube Data API v3
4. Tạo OAuth 2.0 Client ID (Desktop app)
5. Download credentials.json
6. Chạy lần đầu để xác thực:
   ```bash
   python youtube_uploader.py --auth
   ```

### YouTube Upload

```env
ENABLE_YOUTUBE_UPLOAD=true
YOUTUBE_PRIVACY=unlisted  # public, unlisted, private
YOUTUBE_PLAYLIST_ID=PLxxxxxx  # Optional
```

### Blog & Podcast

```env
ENABLE_BLOG=true
ENABLE_PODCAST=true
```

### Social Media

```env
ENABLE_SOCIAL_MEDIA=true

# Telegram
TELEGRAM_BOT_TOKEN=123456:ABC-DEF...
TELEGRAM_CHANNEL_ID=@topikdaily

# Discord Webhook
DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/xxx/yyy

# Twitter (OAuth 2.0)
TWITTER_BEARER_TOKEN=xxx
```

### GitHub Pages

```env
ENABLE_GITHUB_DEPLOY=true
GH_TOKEN=ghp_xxxx
GH_BLOG_REPO=username/topik-blog
GH_CUSTOM_DOMAIN=topikdaily.com
```

## 🖥️ Deploy lên DigitalOcean

### 1. Tạo Droplet

- **Image**: Ubuntu 22.04 LTS
- **Size**: 2GB RAM / 1 CPU minimum
- **Region**: Singapore (gần Hàn Quốc)

### 2. Chạy Setup Script

```bash
ssh root@<droplet-ip>
curl -O https://raw.githubusercontent.com/yourusername/topik-daily/main/setup_digitalocean.sh
bash setup_digitalocean.sh
```

### 3. Cấu Hình

```bash
nano /home/topikbot/topik-daily/.env
```

### 4. Upload Credentials

```bash
scp token.json root@<droplet-ip>:/home/topikbot/topik-daily/
scp youtube_token.json root@<droplet-ip>:/home/topikbot/topik-daily/
```

### 5. Test Run

```bash
sudo -u topikbot /home/topikbot/run_topik_daily.sh
```

## ⏰ Cron Schedule

Pipeline chạy tự động lúc **6:00 AM KST** mỗi ngày:

```
0 21 * * * /home/topikbot/run_topik_daily.sh  # 21:00 UTC = 6:00 KST
```

## 📊 Pipeline Flow

```
┌─────────────┐
│  Crawl News │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  Ra Đề TOPIK│
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ Viết Văn Mẫu│
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ Phân Tích   │
│ Từ Vựng     │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ Generate    │
│ Audio (TTS) │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ Render 5    │
│ Videos      │
└──────┬──────┘
       │
       ├──────────────┬──────────────┬──────────────┐
       ▼              ▼              ▼              ▼
┌───────────┐  ┌───────────┐  ┌───────────┐  ┌───────────┐
│  Google   │  │  YouTube  │  │   Blog    │  │  Podcast  │
│  Drive    │  │  Upload   │  │ Generate  │  │ Generate  │
└───────────┘  └───────────┘  └─────┬─────┘  └───────────┘
                                    │
                                    ▼
                             ┌───────────┐
                             │  GitHub   │
                             │  Pages    │
                             └───────────┘
                                    │
       ┌────────────────────────────┼────────────────────────────┐
       ▼                            ▼                            ▼
┌───────────┐              ┌───────────┐              ┌───────────┐
│  Twitter  │              │  Telegram │              │  Discord  │
└───────────┘              └───────────┘              └───────────┘
```

## 🎙️ Podcast Distribution

Podcast RSS feed sẽ có tại:
- `http://your-server/feed.xml`

Submit feed này đến:
- **Spotify**: Qua [Spotify for Podcasters](https://podcasters.spotify.com/)
- **Apple Podcasts**: Qua [Apple Podcasts Connect](https://podcastsconnect.apple.com/)
- **Google Podcasts**: Tự động index từ RSS

## 📝 Output Mỗi Ngày

| Output | Mô Tả |
|--------|-------|
| `TOPIK_YYYY-MM-DD.docx` | Document Word với nội dung đầy đủ |
| `V1_NewsHealing_*.mp4` | TikTok Short - Tin tức |
| `V2_WritingCoach_*.mp4` | TikTok Short - Bài văn mẫu |
| `V3_VocabQuiz_*.mp4` | TikTok Short - Quiz từ vựng |
| `V4_GrammarQuiz_*.mp4` | TikTok Short - Quiz ngữ pháp |
| `V5_DeepDive_*.mp4` | YouTube Long - Phân tích chi tiết |
| `blog_output/` | Static blog HTML |
| `podcast_output/epXXX_*.mp3` | Podcast episode |
| `podcast_output/feed.xml` | Podcast RSS feed |

## 🔧 Troubleshooting

### YouTube "quotaExceeded"
- YouTube API có giới hạn 10,000 units/ngày
- 1 video upload ≈ 1,600 units
- Giải pháp: Xin tăng quota hoặc giảm số video

### Remotion render lỗi
```bash
cd topik-video
npx remotion render --log=verbose
```

### Audio không có tiếng
- Kiểm tra Azure Speech Key
- Fallback sang edge-tts nếu Azure fail

### Blog không deploy
- Kiểm tra GH_TOKEN có quyền `repo`
- Kiểm tra GH_BLOG_REPO đúng format `username/repo`

## 📄 License

MIT License

## 🙏 Credits

- [Remotion](https://remotion.dev/) - Video rendering
- [Azure Cognitive Services](https://azure.microsoft.com/services/cognitive-services/text-to-speech/) - TTS
- [Google APIs](https://developers.google.com/) - Drive & YouTube
- [Gemini AI](https://ai.google.dev/) - Content Generation
- [Pexels](https://www.pexels.com/) - Stock Videos

---

## ❓ FAQ

### Q: Tôi cần bao nhiêu tiền để chạy hệ thống này?
**A:** Gần như miễn phí!
- **Gemini API**: Free tier 1,500 requests/ngày
- **Azure TTS**: Free tier 500,000 ký tự/tháng (đủ cho ~30 ngày)
- **YouTube API**: Free 10,000 units/ngày
- **GitHub Pages**: Miễn phí
- **VPS (tùy chọn)**: ~$5/tháng (DigitalOcean)

### Q: Làm sao để test từng phần riêng?
**A:**
```bash
# Test TTS
python -c "from main import generate_azure_tts; generate_azure_tts('안녕하세요', 'ko-KR-InJoonNeural', 'test.mp3')"

# Test render video
cd topik-video && npx remotion preview

# Test blog generation
python blog_generator.py
```

### Q: Azure TTS bị lỗi "InvalidSubscription"?
**A:** Kiểm tra:
1. `AZURE_SPEECH_KEY` đã đúng
2. `AZURE_SPEECH_REGION` khớp với region khi tạo resource
3. Resource chưa hết quota (check Azure Portal)

### Q: YouTube upload bị "quotaExceeded"?
**A:** 
- YouTube API giới hạn 10,000 units/ngày
- 1 upload = ~1,600 units = tối đa 6 videos/ngày
- Giải pháp: Đăng ký tăng quota hoặc dùng nhiều project

### Q: Làm sao để thêm video mới?
**A:**
1. Tạo component mới trong `topik-video/src/components/`
2. Thêm Composition trong `Root.tsx`
3. Update `VIDEO_MANIFEST` trong `main.py`
