# 📱 DAILY KOREAN Mobile App

Ứng dụng học tiếng Hàn TOPIK với dữ liệu được tạo tự động hàng ngày.

## ✨ Tính năng

- 📚 **Từ vựng Flashcards** - Học từ vựng với swipe gestures
- ✅ **Quiz tương tác** - Quiz từ vựng và ngữ pháp
- 📰 **Đọc tin tức** - Tin tức tiếng Hàn hàng ngày
- ✍️ **Bài văn mẫu** - Học viết theo format TOPIK
- 🔥 **Streak tracking** - Theo dõi streak học tập
- 💎 **Premium** - Gói nâng cao không quảng cáo

## 🚀 Quick Start

### 1. Khởi chạy Backend API

```bash
# Từ thư mục gốc TIK
cd c:\Users\ThinkPad\TIK

# Cài đặt dependencies
pip install fastapi uvicorn

# Chạy API server
python api_server.py
# hoặc
uvicorn api_server:app --reload --host 0.0.0.0 --port 8000
```

API sẽ chạy tại: http://localhost:8000

### 2. Khởi tạo React Native App

```bash
# Vào thư mục mobile-app
cd mobile-app

# Copy environment file
cp .env.example .env

# Cài đặt dependencies
npm install

# Chạy app
npx expo start
```

### 3. Chạy trên máy ảo

```bash
# Android Emulator
npx expo start --android

# iOS Simulator (macOS only)
npx expo start --ios

# Web (for testing)
npx expo start --web
```

## 📁 Cấu Trúc Dự Án

```
mobile-app/
├── app/                    # Screens (Expo Router)
│   ├── (tabs)/            # Tab navigation
│   │   ├── _layout.tsx    # Tab config
│   │   ├── index.tsx      # Home screen
│   │   ├── vocabulary.tsx # Flashcards
│   │   ├── quiz.tsx       # Quiz screen
│   │   ├── essay.tsx      # Essay/Writing screen
│   │   ├── news.tsx       # News reader
│   │   └── profile.tsx    # Profile/Settings
│   ├── premium.tsx        # Premium subscription
│   └── _layout.tsx        # Root layout
│
├── src/
│   ├── components/        # Reusable components
│   │   ├── AdBanner.tsx
│   │   ├── VocabCard.tsx
│   │   ├── QuizQuestion.tsx
│   │   ├── LoadingSpinner.tsx
│   │   ├── ErrorView.tsx
│   │   ├── StreakBadge.tsx
│   │   ├── ProgressRing.tsx
│   │   └── ConfirmDialog.tsx
│   ├── hooks/             # Custom hooks
│   │   ├── usePremium.ts
│   │   ├── useNetwork.ts
│   │   └── useToast.ts
│   ├── services/          # API services
│   │   └── api.ts
│   ├── store/             # Zustand stores
│   │   ├── userStore.ts
│   │   └── lessonStore.ts
│   ├── constants/         # App constants
│   │   └── index.ts
│   └── utils/             # Helper functions
│       └── helpers.ts
│
├── .env.example           # Environment template
├── app.json               # Expo config
├── eas.json               # EAS Build config
├── package.json           # Dependencies
└── tsconfig.json          # TypeScript config
```
├── src/
│   ├── components/        # UI Components
│   │   ├── VocabCard.tsx  # Flashcard
│   │   ├── QuizQuestion.tsx # Quiz UI
│   │   └── AdBanner.tsx   # AdMob
│   │
│   ├── services/
│   │   └── api.ts         # API client
│   │
│   ├── hooks/
│   │   └── usePremium.ts  # IAP hook
│   │
│   └── store/
│       ├── lessonStore.ts # Lesson state
│       └── userStore.ts   # User state
│
├── app.json               # Expo config
├── eas.json              # EAS Build config
└── package.json
```

## 🔧 Cấu Hình

### API URL

Chỉnh sửa trong `src/services/api.ts`:

```typescript
const API_BASE_URL = 'https://your-api-domain.com';
// Dev: 'http://localhost:8000'
```

### AdMob

Thay thế ID trong:
- `app.json` → `googleMobileAdsAppId`
- `src/components/AdBanner.tsx` → `BANNER_AD_UNIT_ID`

### In-App Purchases

Cấu hình product IDs trong:
- `src/hooks/usePremium.ts` → `PRODUCT_IDS`

## 📦 Build & Deploy

### Development Build

```bash
# Build APK để test
eas build --platform android --profile preview
```

### Production Build

```bash
# Android (AAB cho Google Play)
eas build --platform android --profile production

# iOS (IPA cho App Store)
eas build --platform ios --profile production
```

### Submit to Stores

```bash
# Google Play
eas submit --platform android

# App Store
eas submit --platform ios
```

## 💰 Monetization

### Revenue Streams

| Loại | Dự kiến | Cách thực hiện |
|------|---------|----------------|
| AdMob Banner | $1-3 CPM | Footer mỗi màn hình |
| AdMob Interstitial | $5-15 CPM | Sau quiz |
| Premium Monthly | $2.99/tháng | Không ads + features |
| Premium Lifetime | $49.99 | One-time purchase |

### Premium Features
- ✨ Không quảng cáo
- 📚 Archive 30+ ngày
- 🎯 Unlimited Quiz
- 📊 Analytics chi tiết
- 🔊 Offline audio

## 📊 Backend API Endpoints

| Endpoint | Method | Mô tả |
|----------|--------|-------|
| `/api/today` | GET | Bài học hôm nay |
| `/api/vocabulary` | GET | Danh sách từ vựng |
| `/api/vocabulary/random` | GET | Từ vựng ngẫu nhiên |
| `/api/quiz/vocab` | GET | Quiz từ vựng |
| `/api/quiz/grammar` | GET | Quiz ngữ pháp |
| `/api/news` | GET | Tin tức |
| `/api/essay` | GET | Bài văn mẫu |
| `/api/archive/{date}` | GET | Bài học theo ngày |
| `/api/progress` | POST | Cập nhật tiến độ |
| `/api/user/{id}/stats` | GET | Thống kê user |

## 🎯 Features

- [x] Home screen với tiến độ hàng ngày
- [x] Flashcard từ vựng (swipe)
- [x] Quiz từ vựng & ngữ pháp
- [x] Đọc tin tức tiếng Hàn
- [x] Streak tracking
- [x] AdMob integration
- [x] In-App Purchase
- [x] Push notifications
- [x] Offline storage (Zustand + AsyncStorage)

## 📝 License

MIT License
