# 🎓 Giải Pháp Miễn Phí Cho Sinh Viên - DAILY KOREAN

## 📊 So Sánh Các Nền Tảng

| Platform | Credit/Free | RAM | CPU | Thời hạn | Phù hợp |
|----------|-------------|-----|-----|----------|---------|
| **GitHub Actions** | 2000 phút/tháng | 7GB | 2 vCPU | Vĩnh viễn | ⭐ Render video |
| **Oracle Cloud** | Always Free | 24GB | 4 OCPU | Vĩnh viễn | ⭐ VPS mạnh |
| **Azure for Students** | $100 | Tùy chọn | Tùy chọn | 12 tháng | API server |
| **Google Cloud** | $300 | Tùy chọn | Tùy chọn | 90 ngày | Test nhanh |
| **GitHub Codespaces** | 60h/tháng | 4-8GB | 2-4 vCPU | Vĩnh viễn | Development |

---

# ⭐ PHƯƠNG ÁN 1: GitHub Actions (KHUYÊN DÙNG NHẤT)

## Ưu điểm:
- ✅ **Miễn phí** 2000 phút/tháng (đủ render ~30 ngày)
- ✅ **Không cần VPS** - chạy trên server của GitHub
- ✅ **Tự động** - chạy theo schedule
- ✅ **7GB RAM** - đủ mạnh để render Remotion

## Cách Setup:

### Bước 1: Push code lên GitHub

```powershell
cd C:\Users\ThinkPad\TIK

# Khởi tạo git nếu chưa có
git init
git add .
git commit -m "Initial commit"

# Tạo repo trên GitHub và push
git remote add origin https://github.com/YOUR_USERNAME/TIK.git
git branch -M main
git push -u origin main
```

### Bước 2: Thêm Secrets

1. Vào repo → **Settings** → **Secrets and variables** → **Actions**
2. Click **New repository secret**
3. Thêm các secrets:

| Name | Value |
|------|-------|
| `GEMINI_API_KEY` | Your Gemini API key |
| `AZURE_SPEECH_KEY` | Your Azure TTS key |
| `AZURE_SPEECH_REGION` | eastasia |
| `PEXELS_API_KEY` | Your Pexels key |
| `TELEGRAM_BOT_TOKEN` | Bot token (tùy chọn) |
| `TELEGRAM_CHANNEL_ID` | @channel_id (tùy chọn) |

### Bước 3: Chạy Workflow

1. Vào tab **Actions**
2. Chọn **DAILY KOREAN - Auto Render Videos**
3. Click **Run workflow**

### Bước 4: Download Videos

1. Sau khi workflow hoàn thành
2. Click vào run → **Artifacts**
3. Download `rendered-videos`

---

# ⭐ PHƯƠNG ÁN 2: Oracle Cloud Always Free

## Ưu điểm:
- ✅ **Miễn phí vĩnh viễn** (không cần credit card)
- ✅ **4 OCPU + 24GB RAM** - siêu mạnh!
- ✅ 200GB storage
- ✅ Có thể chạy 24/7

## Cách Đăng Ký:

### Bước 1: Tạo tài khoản

1. Vào [Oracle Cloud Free Tier](https://www.oracle.com/cloud/free/)
2. Click **Start for free**
3. Đăng ký với email trường (ưu tiên) hoặc email cá nhân
4. **Chọn Home Region**: Singapore (gần VN nhất)
5. Không cần credit card cho Always Free

### Bước 2: Tạo VM Always Free

1. Vào **Compute** → **Instances** → **Create Instance**
2. Chọn:
   - **Image**: Ubuntu 22.04
   - **Shape**: VM.Standard.A1.Flex (ARM) - **Miễn phí**
   - **OCPU**: 4 (miễn phí tối đa)
   - **RAM**: 24GB (miễn phí tối đa)
   - **Boot volume**: 100GB
3. Download SSH key
4. Create

### Bước 3: SSH vào VPS

```bash
ssh -i ~/oracle_key.pem ubuntu@YOUR_VM_IP
```

### Bước 4: Setup như hướng dẫn VPS

```bash
# Update
sudo apt update && sudo apt upgrade -y

# Install dependencies
sudo apt install -y python3.11 python3.11-venv python3-pip nodejs npm ffmpeg chromium-browser

# Clone project
git clone https://github.com/YOUR_USERNAME/TIK.git
cd TIK

# Setup Python
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Setup Node
cd topik-video
npm install --legacy-peer-deps
```

---

# ⭐ PHƯƠNG ÁN 3: Azure for Students

## Ưu điểm:
- ✅ **$100 credit miễn phí**
- ✅ Không cần credit card
- ✅ Xác thực bằng email .edu

## Cách Đăng Ký:

1. Vào [Azure for Students](https://azure.microsoft.com/en-us/free/students/)
2. Click **Start free**
3. Đăng nhập bằng email trường (.edu.vn, .ac.kr, etc.)
4. Xác thực sinh viên
5. Nhận $100 credit

## Tạo VM:

1. Portal → **Create a resource** → **Virtual Machine**
2. Chọn:
   - **Size**: Standard_B2s (2 vCPU, 4GB RAM) - ~$30/tháng từ credit
   - **Image**: Ubuntu 22.04
   - **Region**: Southeast Asia
3. Setup SSH key
4. Create

---

# ⭐ PHƯƠNG ÁN 4: Google Cloud $300 Credit

## Ưu điểm:
- ✅ **$300 credit** cho 90 ngày
- ✅ Có thể tạo VM mạnh

## Cách Đăng Ký:

1. Vào [Google Cloud Free Trial](https://cloud.google.com/free)
2. Đăng ký (cần credit card nhưng không bị charge)
3. Tạo VM:
   - **Machine type**: e2-medium (2 vCPU, 4GB)
   - **Region**: asia-southeast1 (Singapore)
   - **OS**: Ubuntu 22.04

---

# 🔧 PHƯƠNG ÁN 5: Kết Hợp (Tối Ưu Nhất)

## Kiến trúc miễn phí 100%:

```
┌─────────────────────────────────────────────────────────────┐
│                    GITHUB ACTIONS                           │
│         (Content Generation + Video Rendering)              │
│                   2000 phút/tháng miễn phí                  │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                  GITHUB PAGES                               │
│              (Blog Hosting - Miễn phí)                      │
│           https://username.github.io/blog                   │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│            ORACLE CLOUD ALWAYS FREE (Optional)              │
│               (API Server + Telegram Bot)                   │
│                 4 OCPU, 24GB RAM - Miễn phí                 │
└─────────────────────────────────────────────────────────────┘
```

## Workflow:

1. **GitHub Actions** chạy mỗi ngày:
   - Generate content (Phase 1-5)
   - Render 5 videos
   - Deploy blog lên GitHub Pages
   - Upload videos lên Google Drive

2. **Oracle Cloud** (tùy chọn):
   - Chạy API server cho mobile app
   - Chạy Telegram bot

---

# 📋 Quick Start - GitHub Actions

## 1. Fork/Clone repo

```powershell
git clone https://github.com/YOUR_USERNAME/TIK.git
```

## 2. Thêm workflow file

File đã có tại: `.github/workflows/daily-pipeline.yml`

## 3. Push lên GitHub

```powershell
git add .
git commit -m "Add GitHub Actions workflow"
git push
```

## 4. Thêm Secrets

Vào repo → Settings → Secrets → Actions → New secret

## 5. Trigger workflow

Vào Actions → Run workflow

---

# 💡 Tips Tiết Kiệm

1. **GitHub Actions**: Render video ~20-30 phút/ngày = 600-900 phút/tháng (đủ trong 2000 phút)

2. **Cache dependencies**: Đã config trong workflow để không cần install lại mỗi lần

3. **Artifacts**: Videos được lưu 7 ngày, download về máy nếu cần

4. **Blog free hosting**: GitHub Pages không giới hạn bandwidth

---

# ❓ FAQ

**Q: GitHub Actions có đủ mạnh để render video không?**
A: Có! 7GB RAM + 2 vCPU đủ cho Remotion. Mỗi video ~5-10 phút render.

**Q: Oracle Cloud thực sự miễn phí vĩnh viễn?**
A: Có! "Always Free" tier không bao giờ hết hạn.

**Q: Cần credit card không?**
A: GitHub Actions + Oracle Cloud: Không cần
   Azure for Students: Không cần (dùng email .edu)
   Google Cloud: Cần nhưng không charge

---

# 🎯 Kết Luận

| Nhu cầu | Giải pháp |
|---------|-----------|
| Chỉ cần render video | **GitHub Actions** |
| Cần VPS mạnh miễn phí | **Oracle Cloud** |
| Có email .edu | **Azure for Students** |
| Cần nhanh, không setup | **GitHub Actions** |

**Khuyên dùng**: Bắt đầu với **GitHub Actions** - không cần VPS, không cần setup phức tạp!
