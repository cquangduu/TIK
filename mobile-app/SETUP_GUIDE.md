# 📱 DAILY KOREAN Mobile App - Complete Setup Guide

## 🎯 Tổng Quan

App React Native/Expo để học tiếng Hàn với:
- 📚 Vocabulary Flashcards
- 🎯 Daily Quiz  
- 📰 News Reader
- ✍️ Writing Practice

---

## 📋 Checklist Setup

- [ ] Cài đặt Node.js 18+
- [ ] Cài đặt Expo CLI
- [ ] Tạo assets (icon, splash)
- [ ] Cấu hình .env
- [ ] Chạy Backend API
- [ ] Test trên Expo Go
- [ ] Build APK/IPA

---

## 🔧 Bước 1: Cài đặt Tools

### Windows:
```powershell
# Kiểm tra Node.js
node --version  # Cần >= 18.0

# Cài Expo CLI global
npm install -g expo-cli eas-cli

# Đăng nhập Expo
npx expo login
```

---

## 📦 Bước 2: Cài đặt Dependencies

```powershell
cd C:\Users\ThinkPad\TIK\mobile-app

# Cài packages
npm install

# Nếu có lỗi peer deps
npm install --legacy-peer-deps
```

---

## 🔑 Bước 3: Cấu hình Environment

```powershell
# Tạo file .env
copy .env.example .env
```

Mở `.env` và điền:

```env
# API URL (local development)
EXPO_PUBLIC_API_URL=http://192.168.1.xxx:8000

# Cho production (thay bằng URL VPS của bạn)
# EXPO_PUBLIC_API_URL=https://api.dailykorean.app

# AdMob (đăng ký tại https://admob.google.com)
EXPO_PUBLIC_ADMOB_BANNER_ID_IOS=ca-app-pub-xxxxx/yyyyy
EXPO_PUBLIC_ADMOB_BANNER_ID_ANDROID=ca-app-pub-xxxxx/zzzzz

# EAS Project (từ Expo dashboard)
EAS_PROJECT_ID=your-project-id
```

---

## 🖼️ Bước 4: Tạo App Assets

Cần tạo các file hình ảnh trong `assets/images/`:

| File | Kích thước | Mô tả |
|------|-----------|-------|
| `icon.png` | 1024×1024 | App icon |
| `adaptive-icon.png` | 1024×1024 | Android adaptive icon |
| `splash.png` | 1284×2778 | Splash screen |
| `favicon.png` | 48×48 | Web favicon |
| `notification-icon.png` | 96×96 | Notification icon |

### Tạo nhanh với Canva/Figma:
1. Vào [Canva](https://canva.com)
2. Tạo design 1024×1024
3. Thêm logo "TOPIK Daily" + Korean flag icon
4. Export PNG

---

## 🌐 Bước 5: Chạy Backend API

### Local Development:

```powershell
cd C:\Users\ThinkPad\TIK

# Cài FastAPI nếu chưa có
pip install fastapi uvicorn

# Chạy API server
uvicorn api_server:app --reload --host 0.0.0.0 --port 8000
```

### Kiểm tra API:
- Mở browser: http://localhost:8000/docs
- Test endpoint: http://localhost:8000/api/today

### Lấy IP local cho mobile:
```powershell
ipconfig | findstr "IPv4"
# Ví dụ: 192.168.1.100
```

Cập nhật `.env`:
```env
EXPO_PUBLIC_API_URL=http://192.168.1.100:8000
```

---

## 📱 Bước 6: Chạy App Development

### Cách 1: Expo Go (Nhanh nhất)

```powershell
cd C:\Users\ThinkPad\TIK\mobile-app

# Start development server
npx expo start
```

1. Quét QR code bằng app **Expo Go** (Android/iOS)
2. App sẽ load trên điện thoại

### Cách 2: Android Emulator

```powershell
# Cần cài Android Studio trước
npx expo start --android
```

### Cách 3: iOS Simulator (Mac only)

```powershell
npx expo start --ios
```

---

## 🏗️ Bước 7: Build APK/IPA Production

### 7.1 Đăng ký EAS Build

```powershell
# Đăng nhập Expo
npx expo login

# Cấu hình EAS
npx eas build:configure
```

### 7.2 Cập nhật app.json

Mở `app.json` và thay đổi:

```json
{
  "expo": {
    "name": "TOPIK Daily",
    "ios": {
      "bundleIdentifier": "com.yourname.topikdaily"
    },
    "android": {
      "package": "com.yourname.topikdaily"
    }
  }
}
```

### 7.3 Build Android APK

```powershell
# Build APK (free, nhưng chậm ~15-30 phút)
npx eas build --platform android --profile preview

# Build AAB cho Google Play
npx eas build --platform android --profile production
```

### 7.4 Build iOS IPA

```powershell
# Cần Apple Developer Account ($99/năm)
npx eas build --platform ios --profile production
```

---

## 🚀 Bước 8: Publish lên Stores

### Google Play Store:

1. Đăng ký [Google Play Console](https://play.google.com/console) ($25 one-time)
2. Tạo app mới
3. Upload AAB file
4. Điền thông tin app
5. Submit for review

### Apple App Store:

1. Đăng ký [Apple Developer](https://developer.apple.com) ($99/năm)
2. Tạo app trong App Store Connect
3. Upload IPA qua EAS Submit:
```powershell
npx eas submit --platform ios
```

---

## 💰 Bước 9: Setup Monetization

### 9.1 Google AdMob

1. Đăng ký [AdMob](https://admob.google.com)
2. Tạo App → Chọn Android/iOS
3. Tạo Ad Units:
   - Banner Ad
   - Interstitial Ad
   - Rewarded Ad
4. Copy Ad Unit IDs vào `.env`

### 9.2 In-App Purchases

1. Setup trong Google Play Console / App Store Connect
2. Tạo subscription products:
   - `premium_monthly` — $2.99/tháng
   - `premium_yearly` — $24.99/năm
   - `premium_lifetime` — $49.99

---

## 🔄 Bước 10: Kết nối với Pipeline

Để app nhận data mới mỗi ngày:

### Trên VPS:

```bash
# Sau khi main.py chạy xong, copy data cho API
cp topik-video/public/final_data.json /var/www/api/data/

# Hoặc chạy API server
cd ~/TIK
uvicorn api_server:app --host 0.0.0.0 --port 8000
```

### Dùng systemd:

```bash
sudo nano /etc/systemd/system/dailykorean-api.service
```

```ini
[Unit]
Description=DAILY KOREAN API Server
After=network.target

[Service]
User=dailykorean
WorkingDirectory=/home/dailykorean/TIK
ExecStart=/home/dailykorean/TIK/venv/bin/uvicorn api_server:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl enable dailykorean-api
sudo systemctl start dailykorean-api
```

---

## 📊 Cấu trúc App

```
mobile-app/
├── app/                    # Expo Router screens
│   ├── (tabs)/            # Tab navigation
│   │   ├── index.tsx      # Home
│   │   ├── vocabulary.tsx # Vocabulary
│   │   ├── quiz.tsx       # Quiz
│   │   └── news.tsx       # News
│   ├── premium.tsx        # Premium upgrade
│   └── _layout.tsx        # Root layout
├── src/
│   ├── components/        # Reusable components
│   ├── services/          # API calls
│   ├── store/             # Zustand state
│   ├── hooks/             # Custom hooks
│   └── utils/             # Helpers
├── assets/                # Images, fonts
├── app.json               # Expo config
├── package.json
└── .env                   # Environment vars
```

---

## 🐛 Troubleshooting

### Lỗi "Network Error" khi gọi API
- Kiểm tra API đang chạy: `curl http://localhost:8000/api/today`
- Đảm bảo IP trong .env đúng
- Tắt firewall tạm thời để test

### Lỗi "Metro bundler failed"
```powershell
# Clear cache
npx expo start --clear
```

### Lỗi build EAS
```powershell
# Check logs
npx eas build:view
```

### App crash khi mở
- Kiểm tra assets tồn tại
- Check console logs trong Expo Go

---

## ✅ Summary

1. ✅ `npm install`
2. ✅ Tạo `.env` với API URL
3. ✅ Tạo assets (icon, splash)
4. ✅ Chạy Backend API
5. ✅ `npx expo start`
6. ✅ Test trên Expo Go
7. ✅ Build APK: `npx eas build --platform android`
8. ✅ Publish lên stores

---

*DAILY KOREAN Mobile App v1.0*
