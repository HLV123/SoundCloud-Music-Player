#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from kivy.app import App
from kivy.config import Config

# Cấu hình cửa sổ
Config.set('graphics', 'width', '1200')
Config.set('graphics', 'height', '800')
Config.set('graphics', 'minimum_width', '800')
Config.set('graphics', 'minimum_height', '600')
Config.set('graphics', 'resizable', True)

from music_player import MusicPlayerApp

if __name__ == '__main__':
    print("SoundCloud Music Player - Simplified Version")
    print("Tinh nang moi:")
    print("- Audio visualizer thay the artwork")
    print("- Chi co repeat off/one/all (khong shuffle)")
    print("- Loai bo thu vien, chi Search va Player")
    print("- Cai dat: pip install kivy python-vlc yt-dlp")
    
    try:
        app = MusicPlayerApp()
        app.run()
    except Exception as e:
        print(f"Loi khoi dong: {e}")
        input("Nhan Enter de thoat...")