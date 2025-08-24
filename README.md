# SoundCloud Music Player - Vinyl Mode

Ứng dụng phát nhạc SoundCloud với giao diện đĩa than độc đáo, được xây dựng bằng Python và Kivy.

## 📋 Tính năng chính

### 🎵 Phát nhạc
- Tìm kiếm và phát nhạc từ SoundCloud
- Hỗ trợ phát file nhạc local (MP3, WAV, OGG, M4A, FLAC, AAC)
- Điều khiển phát/tạm dừng, next/previous
- Điều chỉnh âm lượng và vị trí phát
- Chế độ lặp lại một bài (Repeat One)

### 🎨 Giao diện Vinyl Mode
- Đĩa than quay tự động với hiệu ứng đẹp mắt
- Audio visualizer thay thế artwork truyền thống
- Giao diện tối hiện đại với gradient buttons
- Layout responsive tự động chuyển đổi

### 🔍 Tìm kiếm và quản lý
- Tìm kiếm trực tiếp từ SoundCloud
- Thêm nhạc vào đĩa than với số thứ tự
- Download tự động khi thêm vào đĩa
- Quản lý playlist đơn giản

## 🛠️ Cài đặt

### Yêu cầu hệ thống
- Python 3.7+
- VLC Media Player (khuyến nghị) hoặc Pygame

### Cài đặt thư viện

```bash
# Cài đặt các thư viện cần thiết
pip install kivy python-vlc yt-dlp

# Nếu không có VLC, có thể sử dụng pygame
pip install pygame
```

### Cài đặt VLC Player
- **Windows**: Tải từ [videolan.org](https://www.videolan.org/vlc/)
- **MacOS**: `brew install vlc` hoặc tải từ website
- **Ubuntu/Debian**: `sudo apt install vlc`
- **CentOS/RHEL**: `sudo yum install vlc`

## 🚀 Sử dụng

### Chạy ứng dụng
```bash
python main.py
```

### Hướng dẫn sử dụng

1. **Tìm kiếm nhạc**: 
   - Nhập từ khóa vào ô tìm kiếm
   - Nhấn "TIM" hoặc Enter

2. **Thêm nhạc vào đĩa**:
   - Nhấn nút "+" bên cạnh bài hát
   - Chờ download hoàn tất

3. **Phát nhạc**:
   - Click vào số thứ tự trên đĩa than
   - Sử dụng các nút điều khiển

4. **File local**:
   - Nhấn "FILE" để chọn file từ máy
   - Hỗ trợ nhiều định dạng âm thanh

## 📁 Cấu trúc dự án

```
soundcloud-music-player/
├── main.py              # Entry point chính
├── music_player.py      # Logic chính của ứng dụng
├── audio_backend.py     # Xử lý phát nhạc (VLC/Pygame)
├── ui_search.py         # Giao diện tìm kiếm với vinyl disc
├── ui_player.py         # Giao diện phát nhạc
├── ui_base.py          # Components UI cơ bản
├── visualizer.py       # Audio visualizer
├── slider.py           # Custom slider components
└── utils.py            # Utilities và helper functions
```

---

⭐ **Nếu thấy dự án hữu ích, đừng quên cho một star nhé!** ⭐
