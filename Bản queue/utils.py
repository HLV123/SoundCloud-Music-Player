#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import tempfile
from kivy.logger import Logger

class FileManager:
    def __init__(self):
        self.temp_files = []
        
    def add_temp_file(self, filepath):
        if filepath and filepath not in self.temp_files:
            self.temp_files.append(filepath)
    
    def cleanup_temp_files(self):
        for temp_file in self.temp_files:
            try:
                if os.path.exists(temp_file):
                    os.unlink(temp_file)
            except Exception as e:
                Logger.error(f"FileManager: Loi xoa file {temp_file} - {e}")
        self.temp_files.clear()

class AudioUtils:
    @staticmethod
    def format_duration(seconds):
        if not seconds or seconds <= 0:
            return "00:00"
        minutes = int(seconds) // 60
        seconds = int(seconds) % 60
        return f"{minutes:02d}:{seconds:02d}"
    
    @staticmethod
    def is_audio_file(filepath):
        audio_extensions = ['.mp3', '.wav', '.ogg', '.m4a', '.aac', '.flac', '.wma']
        ext = os.path.splitext(filepath)[1].lower()
        return ext in audio_extensions