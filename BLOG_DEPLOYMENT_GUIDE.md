# 🌐 DAILY KOREAN Blog - Hướng Dẫn Tạo Blog Thực Sự

## 🎯 Tổng Quan

Hướng dẫn này sẽ giúp bạn deploy blog lên internet với:
- **GitHub Pages** (Miễn phí, dễ nhất)
- **Netlify** (Miễn phí, nhiều tính năng)
- **Vercel** (Miễn phí, nhanh nhất)
- **VPS tự host** (Kiểm soát hoàn toàn)

---

## 📁 Cấu Trúc Blog Hiện Tại

```
blog_output/
├── index.html          # Trang chủ
├── style.css           # CSS styles
├── assets/             # Hình ảnh, fonts
└── posts/              # Các bài viết
    ├── 2026-02-02-topic-name.html
    ├── 2026-02-02-topic-name.md
    └── ...
```

---

# 🚀 PHƯƠNG PHÁP 1: GitHub Pages (Khuyên Dùng)

## Bước 1: Tạo GitHub Repository

1. Đăng nhập [GitHub](https://github.com)
2. Click **New Repository**
3. Đặt tên: `dailykorean-blog` hoặc `topik-blog`
4. Chọn **Public**
5. **KHÔNG** check "Add README"
6. Click **Create Repository**

## Bước 2: Cấu hình Git Local

```powershell
cd C:\Users\ThinkPad\TIK\blog_output

# Khởi tạo git
git init

# Cấu hình user
git config user.name "Your Name"
git config user.email "your-email@gmail.com"

# Thêm tất cả files
git add .

# Commit
git commit -m "Initial blog deploy"

# Thêm remote (thay YOUR_USERNAME)
git remote add origin https://github.com/YOUR_USERNAME/dailykorean-blog.git

# Push lên GitHub
git branch -M main
git push -u origin main
```

## Bước 3: Bật GitHub Pages

1. Vào repo trên GitHub
2. Click **Settings** → **Pages**
3. Source: chọn **Deploy from a branch**
4. Branch: chọn **main** / **root**
5. Click **Save**

## Bước 4: Truy Cập Blog

Sau 1-2 phút, blog sẽ live tại:
```
https://YOUR_USERNAME.github.io/dailykorean-blog/
```

## Bước 5: Custom Domain (Tùy chọn)

### 5.1 Mua Domain

Các nhà cung cấp domain:
- [Namecheap](https://namecheap.com) - Rẻ, $8-12/năm
- [Google Domains](https://domains.google) - $12/năm
- [Cloudflare](https://cloudflare.com) - Giá gốc

Ví dụ mua: `dailykorean.com` hoặc `topikdaily.com`

### 5.2 Cấu hình DNS

Vào DNS Settings của domain, thêm:

**Option A: Apex domain (dailykorean.com)**
```
Type: A
Name: @
Value: 185.199.108.153
       185.199.109.153
       185.199.110.153
       185.199.111.153
```

**Option B: Subdomain (blog.dailykorean.com)**
```
Type: CNAME
Name: blog
Value: YOUR_USERNAME.github.io
```

### 5.3 Cấu hình GitHub

1. Tạo file `CNAME` trong blog_output:
```powershell
echo "dailykorean.com" > C:\Users\ThinkPad\TIK\blog_output\CNAME
```

2. Push lên GitHub:
```powershell
cd C:\Users\ThinkPad\TIK\blog_output
git add CNAME
git commit -m "Add custom domain"
git push
```

3. Vào Settings → Pages → Custom domain → Nhập domain → Save

4. Check **Enforce HTTPS** ✅

---

# 🚀 PHƯƠNG PHÁP 2: Netlify

## Bước 1: Đăng ký Netlify

1. Vào [netlify.com](https://netlify.com)
2. Sign up với GitHub

## Bước 2: Deploy

### Cách A: Kéo thả

1. Vào [app.netlify.com/drop](https://app.netlify.com/drop)
2. Kéo thả folder `blog_output` vào
3. Done! Netlify sẽ cho bạn URL ngẫu nhiên

### Cách B: Connect GitHub

1. Click **New site from Git**
2. Chọn GitHub → Authorize
3. Chọn repo `dailykorean-blog`
4. Build settings:
   - Build command: (để trống)
   - Publish directory: `.` hoặc `/`
5. Click **Deploy site**

## Bước 3: Custom Domain

1. Site settings → Domain management
2. Add custom domain → `dailykorean.com`
3. Cập nhật DNS:
```
Type: CNAME
Name: @
Value: your-site-name.netlify.app
```

---

# 🚀 PHƯƠNG PHÁP 3: Vercel

## Bước 1: Đăng ký Vercel

1. Vào [vercel.com](https://vercel.com)
2. Sign up với GitHub

## Bước 2: Deploy

```powershell
# Cài Vercel CLI
npm install -g vercel

# Deploy
cd C:\Users\ThinkPad\TIK\blog_output
vercel

# Trả lời các câu hỏi
# ? Set up and deploy? Y
# ? Which scope? (chọn tài khoản)
# ? Link to existing project? N
# ? Project name? dailykorean-blog
# ? In which directory is your code located? ./
```

## Bước 3: Custom Domain

1. Vào Dashboard → Project → Settings → Domains
2. Add domain: `dailykorean.com`
3. Cập nhật DNS theo hướng dẫn

---

# 🚀 PHƯƠNG PHÁP 4: VPS Self-Host

## Bước 1: Setup Nginx trên VPS

```bash
# SSH vào VPS
ssh root@68.183.187.8

# Cài Nginx
apt update
apt install nginx -y

# Tạo thư mục cho blog
mkdir -p /var/www/dailykorean-blog
chown -R $USER:$USER /var/www/dailykorean-blog
```

## Bước 2: Cấu hình Nginx

```bash
nano /etc/nginx/sites-available/dailykorean-blog
```

Nội dung:

```nginx
server {
    listen 80;
    server_name dailykorean.com www.dailykorean.com;
    
    root /var/www/dailykorean-blog;
    index index.html;
    
    location / {
        try_files $uri $uri/ =404;
    }
    
    # Cache static files
    location ~* \.(css|js|jpg|jpeg|png|gif|ico|svg|woff|woff2)$ {
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
    
    # Gzip compression
    gzip on;
    gzip_types text/plain text/css application/json application/javascript;
}
```

## Bước 3: Enable site

```bash
ln -s /etc/nginx/sites-available/dailykorean-blog /etc/nginx/sites-enabled/
nginx -t
systemctl reload nginx
```

## Bước 4: Upload Blog Files

```powershell
# Từ Windows
scp -r C:\Users\ThinkPad\TIK\blog_output\* root@68.183.187.8:/var/www/dailykorean-blog/
```

## Bước 5: SSL với Certbot (HTTPS)

```bash
apt install certbot python3-certbot-nginx -y
certbot --nginx -d dailykorean.com -d www.dailykorean.com
```

---

# 🔄 AUTO DEPLOY: Tự Động Cập Nhật Blog

## Setup trong main.py

Blog đã được tích hợp trong pipeline. Cấu hình `.env`:

```env
ENABLE_BLOG=true
ENABLE_GITHUB_DEPLOY=true
GH_TOKEN=ghp_xxxxxxxxxxxxxxxxxxxx
GH_BLOG_REPO=yourusername/dailykorean-blog
GH_BLOG_BRANCH=main
```

## Script Deploy Thủ Công

```powershell
# deploy_blog.ps1
cd C:\Users\ThinkPad\TIK\blog_output

git add .
git commit -m "Update: $(Get-Date -Format 'yyyy-MM-dd')"
git push origin main

Write-Host "✅ Blog deployed!"
```

## Cron Job trên VPS

```bash
# Thêm vào crontab
crontab -e
```

```cron
# Sync blog mỗi ngày lúc 7:00 AM (sau khi pipeline chạy)
0 7 * * * rsync -avz /home/dailykorean/TIK/blog_output/ /var/www/dailykorean-blog/
```

---

# 🎨 NÂNG CẤP BLOG

## 1. Thêm Google Analytics

Thêm vào `index.html` trước `</head>`:

```html
<!-- Google Analytics -->
<script async src="https://www.googletagmanager.com/gtag/js?id=G-XXXXXXXXXX"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());
  gtag('config', 'G-XXXXXXXXXX');
</script>
```

## 2. Thêm Comments (Giscus)

1. Vào [giscus.app](https://giscus.app)
2. Cấu hình repo
3. Copy script vào cuối mỗi bài post

## 3. Thêm Search

Dùng [Pagefind](https://pagefind.app):

```bash
npm install pagefind
npx pagefind --source blog_output
```

## 4. Thêm RSS Feed

Tạo file `feed.xml`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
  <channel>
    <title>DAILY KOREAN Blog</title>
    <link>https://dailykorean.com</link>
    <description>Học TOPIK mỗi ngày</description>
    <!-- Items sẽ được generate tự động -->
  </channel>
</rss>
```

## 5. Thêm SEO Meta Tags

Đã có trong template, nhưng có thể thêm:

```html
<meta property="og:title" content="DAILY KOREAN - Học TOPIK">
<meta property="og:description" content="Học tiếng Hàn mỗi ngày">
<meta property="og:image" content="https://dailykorean.com/og-image.png">
<meta property="og:url" content="https://dailykorean.com">
<meta name="twitter:card" content="summary_large_image">
```

---

# 📊 CHECKLIST DEPLOY BLOG

## GitHub Pages:
- [ ] Tạo GitHub repo
- [ ] Push blog_output lên repo
- [ ] Bật GitHub Pages
- [ ] (Tùy chọn) Mua domain
- [ ] (Tùy chọn) Cấu hình DNS
- [ ] (Tùy chọn) Bật HTTPS

## Tự động hóa:
- [ ] Cấu hình GH_TOKEN trong .env
- [ ] Test chạy main.py
- [ ] Kiểm tra blog được cập nhật

---

# 🔗 URLs Khi Hoàn Thành

| Platform | URL |
|----------|-----|
| GitHub Pages | `https://username.github.io/dailykorean-blog/` |
| Custom Domain | `https://dailykorean.com` |
| Netlify | `https://dailykorean.netlify.app` |
| Vercel | `https://dailykorean.vercel.app` |
| VPS | `http://68.183.187.8` hoặc domain |

---

# 💡 Tips

1. **SEO**: Đặt title và description khác nhau cho mỗi bài
2. **Performance**: Nén hình ảnh trước khi upload
3. **Analytics**: Theo dõi traffic để biết content nào được quan tâm
4. **Social**: Share link bài mới lên Twitter/Telegram
5. **Backlinks**: Liên kết giữa các bài viết liên quan

---

*DAILY KOREAN Blog Deployment Guide v1.0*
