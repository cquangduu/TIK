# 📺 Hướng Dẫn Cài Đặt YouTube Auto Upload

## Bước 1: Kích Hoạt YouTube Data API v3

1. Truy cập [Google Cloud Console](https://console.cloud.google.com/)
2. Chọn project **topik-auto** (hoặc project đang dùng cho Drive)
3. Vào **APIs & Services** > **Library**
4. Tìm kiếm **YouTube Data API v3**
5. Click **Enable**

## Bước 2: Cấu Hình OAuth Consent Screen

1. Vào **APIs & Services** > **OAuth consent screen**
2. Chọn **External** (hoặc Internal nếu dùng Google Workspace)
3. Điền thông tin:
   - App name: `TOPIK Auto Upload`
   - User support email: (email của bạn)
   - Developer contact: (email của bạn)
4. Click **Save and Continue**
5. Ở phần **Scopes**, click **Add or Remove Scopes**
6. Thêm các scopes sau:
   - `https://www.googleapis.com/auth/youtube.upload`
   - `https://www.googleapis.com/auth/youtube`
7. Click **Save and Continue**
8. Ở phần **Test users**, thêm email YouTube của bạn
9. Click **Save and Continue**

## Bước 3: Cấu Hình Environment Variables

Trong file `.env`, cập nhật:

```env
# YouTube Upload Settings
ENABLE_YOUTUBE_UPLOAD=true
YOUTUBE_PRIVACY=unlisted    # public, unlisted, hoặc private
YOUTUBE_PLAYLIST_ID=        # (tùy chọn) ID playlist để thêm video
```

## Bước 4: Xác Thực Lần Đầu

Khi chạy lần đầu, sẽ mở trình duyệt yêu cầu đăng nhập Google:

1. Đăng nhập tài khoản YouTube của bạn
2. Cho phép các quyền được yêu cầu
3. Token sẽ được lưu vào `youtube_token.json`

**Lưu ý quan trọng:**
- Nếu app đang ở chế độ "Testing", chỉ các email trong **Test users** mới có thể xác thực
- Token sẽ hết hạn sau 7 ngày nếu app chưa được verify
- Để publish app, bạn cần submit để Google review

## Bước 5: Chạy Test

```bash
# Test module riêng lẻ
python youtube_uploader.py --video video.mp4 --title "Test Video"

# Hoặc chạy full pipeline
python main.py
```

## Các Giá Trị Privacy

| Giá trị | Mô tả |
|---------|-------|
| `public` | Công khai - ai cũng xem được |
| `unlisted` | Không công khai - chỉ ai có link mới xem được |
| `private` | Riêng tư - chỉ bạn xem được |

**Khuyến nghị:** Bắt đầu với `unlisted` để kiểm tra, sau đó đổi sang `public` khi đã ổn định.

## Troubleshooting

### Lỗi "Access blocked: App not verified"
- Thêm email của bạn vào **Test users** trong OAuth consent screen

### Lỗi "quotaExceeded"
- YouTube API có giới hạn quota hàng ngày (10,000 units)
- 1 video upload = ~1,600 units
- Tức là khoảng 6 video/ngày với quota mặc định

### Lỗi "Invalid credentials"
- Xóa file `youtube_token.json` và chạy lại để xác thực mới

---

**Sử dụng cùng credentials với Google Drive:**
Project hiện tại đã có `GDRIVE_CREDENTIALS_JSON` trong `.env`. Module YouTube uploader sẽ tự động sử dụng credentials này (cùng Google project), chỉ cần thêm scope YouTube Data API.
