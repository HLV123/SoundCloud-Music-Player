#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import threading
import tempfile
import os
import yt_dlp
from kivy.logger import Logger
from kivy.clock import Clock

try:
    import vlc
    VLC_AVAILABLE = True
except ImportError:
    VLC_AVAILABLE = False
    try:
        import pygame
        PYGAME_AVAILABLE = True
    except ImportError:
        PYGAME_AVAILABLE = False

class AudioBackend:
    def __init__(self):
        self.backend = None
        self.player = None
        self.current_file = None
        self.duration = 0
        self.position = 0
        self.volume = 0.7
        self.temp_files = []
        
        self.init_backend()
    
    def init_backend(self):
        """Khởi tạo backend âm thanh"""
        if VLC_AVAILABLE:
            try:
                self.vlc_instance = vlc.Instance('--intf=dummy')
                self.player = self.vlc_instance.media_player_new()
                self.backend = "vlc"
                Logger.info("AudioBackend: Sử dụng VLC backend")
                return
            except Exception as e:
                Logger.warning(f"AudioBackend: Lỗi khởi tạo VLC - {e}")
        
        if PYGAME_AVAILABLE:
            try:
                pygame.mixer.pre_init(frequency=44100, size=-16, channels=2, buffer=1024)
                pygame.mixer.init()
                self.backend = "pygame"
                Logger.info("AudioBackend: Sử dụng Pygame backend")
                return
            except Exception as e:
                Logger.warning(f"AudioBackend: Lỗi khởi tạo Pygame - {e}")
        
        Logger.error("AudioBackend: Không có backend nào khả dụng!")
        raise RuntimeError("Cài đặt: pip install python-vlc (+ VLC Player) hoặc pygame")
    
    def load_track(self, track_info, callback=None):
        """Load track từ URL hoặc file local"""
        def load_thread():
            try:
                url = track_info.get('url', '')
                title = track_info.get('title', 'Unknown')
                
                if os.path.exists(url):
                    # File local
                    media_path = url
                else:
                    # Download từ SoundCloud
                    media_path = self._download_track(url)
                
                self.current_file = media_path
                
                if self.backend == "vlc":
                    media = self.vlc_instance.media_new(media_path)
                    self.player.set_media(media)
                    # Lấy duration
                    media.parse()
                    self.duration = media.get_duration() / 1000.0 if media.get_duration() > 0 else 0
                else:
                    # Pygame không thể lấy duration dễ dàng
                    self.duration = 0
                
                Clock.schedule_once(lambda dt: callback(True) if callback else None, 0)
                
            except Exception as e:
                error_msg = str(e)
                Logger.error(f"AudioBackend: Lỗi load track - {error_msg}")
                Clock.schedule_once(lambda dt: callback(False, error_msg) if callback else None, 0)
        
        threading.Thread(target=load_thread, daemon=True).start()
    
    def _download_track(self, url):
        """Download track từ URL"""
        temp_dir = tempfile.gettempdir()
        
        format_selector = 'bestaudio/best' if self.backend == "vlc" else 'worst[ext=mp4]/worst[ext=webm]/worst'
        
        ydl_opts = {
            'format': format_selector,
            'outtmpl': os.path.join(temp_dir, 'music_%(id)s.%(ext)s'),
            'quiet': True,
            'no_warnings': True,
            'ignoreerrors': False,
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            media_path = ydl.prepare_filename(info)
            
            # Tìm file đã download
            if not os.path.exists(media_path):
                video_id = info.get('id', 'unknown')
                for ext in ['.mp4', '.webm', '.m4a', '.mp3']:
                    test_file = os.path.join(temp_dir, f'music_{video_id}{ext}')
                    if os.path.exists(test_file):
                        media_path = test_file
                        break
            
            if media_path not in self.temp_files:
                self.temp_files.append(media_path)
            
            return media_path
    
    def play(self):
        """Phát nhạc"""
        if not self.current_file:
            return False
            
        try:
            if self.backend == "vlc":
                self.player.play()
            else:
                if not hasattr(self, '_pygame_loaded') or not self._pygame_loaded:
                    pygame.mixer.music.load(self.current_file)
                    self._pygame_loaded = True
                pygame.mixer.music.play()
            return True
        except Exception as e:
            Logger.error(f"AudioBackend: Lỗi phát nhạc - {e}")
            return False
    
    def pause(self):
        """Tạm dừng"""
        try:
            if self.backend == "vlc":
                self.player.pause()
            else:
                pygame.mixer.music.pause()
            return True
        except Exception as e:
            Logger.error(f"AudioBackend: Lỗi pause - {e}")
            return False
    
    def stop(self):
        """Dừng phát"""
        try:
            if self.backend == "vlc":
                self.player.stop()
            else:
                pygame.mixer.music.stop()
            self.position = 0
            self._pygame_loaded = False
            return True
        except Exception as e:
            Logger.error(f"AudioBackend: Lỗi stop - {e}")
            return False
    
    def set_volume(self, volume):
        """Đặt âm lượng (0-1)"""
        try:
            self.volume = max(0, min(1, volume))
            if self.backend == "vlc":
                self.player.audio_set_volume(int(self.volume * 100))
            else:
                pygame.mixer.music.set_volume(self.volume)
            return True
        except Exception as e:
            Logger.error(f"AudioBackend: Lỗi set volume - {e}")
            return False
    
    def set_position(self, position):
        """Đặt vị trí phát (0-1)"""
        try:
            if self.backend == "vlc":
                self.player.set_position(max(0, min(1, position)))
            # Pygame không hỗ trợ seek dễ dàng
            return True
        except Exception as e:
            Logger.error(f"AudioBackend: Lỗi set position - {e}")
            return False
    
    def get_position(self):
        """Lấy vị trí hiện tại (0-1)"""
        try:
            if self.backend == "vlc":
                return self.player.get_position()
            else:
                # Pygame không hỗ trợ get position
                return 0
        except:
            return 0
    
    def get_time(self):
        """Lấy thời gian hiện tại (giây)"""
        try:
            if self.backend == "vlc":
                return self.player.get_time() / 1000.0
            else:
                return 0
        except:
            return 0
    
    def get_duration(self):
        """Lấy tổng thời gian (giây)"""
        return self.duration
    
    def is_playing(self):
        """Kiểm tra đang phát hay không"""
        try:
            if self.backend == "vlc":
                return self.player.get_state() == vlc.State.Playing
            else:
                return pygame.mixer.music.get_busy()
        except:
            return False
    
    def cleanup(self):
        """Dọn dẹp tài nguyên"""
        try:
            self.stop()
            if self.backend == "pygame":
                pygame.mixer.quit()
            
            # Xóa temp files
            for temp_file in self.temp_files:
                try:
                    if os.path.exists(temp_file):
                        os.unlink(temp_file)
                except:
                    pass
        except Exception as e:
            Logger.error(f"AudioBackend: Lỗi cleanup - {e}")