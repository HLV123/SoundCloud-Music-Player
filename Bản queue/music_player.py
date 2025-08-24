#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from kivy.app import App
from kivy.uix.screenmanager import ScreenManager
from kivy.clock import Clock
from kivy.logger import Logger

from audio_backend import AudioBackend
from ui_search import SearchScreen
from ui_player import PlayerScreen
from utils import FileManager

class MusicPlayerApp(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.title = "SoundCloud Music Player"
        
        self.audio_backend = AudioBackend()
        self.file_manager = FileManager()
        
        self.current_track = None
        self.playlist = []
        self.current_index = 0
        self.is_playing = False
        self.repeat_mode = 0
        
    def build(self):
        self.sm = ScreenManager()
        
        self.search_screen = SearchScreen(app=self, name='search')
        self.player_screen = PlayerScreen(app=self, name='player')
        
        self.sm.add_widget(self.search_screen)
        self.sm.add_widget(self.player_screen)
        
        self.sm.current = 'search'
        
        Clock.schedule_interval(self.update_ui, 0.5)
        
        return self.sm
    
    def get_downloaded_queue(self):
        return [track for track in self.playlist if track.get('local_path')]
    
    def get_current_index_in_downloaded_queue(self):
        downloaded_queue = self.get_downloaded_queue()
        if not downloaded_queue or not self.current_track:
            return -1
        
        current_url = self.current_track.get('url', '')
        for i, track in enumerate(downloaded_queue):
            if track.get('url') == current_url or track.get('local_path') == current_url:
                return i
        return -1
    
    def update_ui(self, dt):
        if self.current_track and self.is_playing:
            if hasattr(self.player_screen, 'update_position'):
                self.player_screen.update_position()
            
            if self.audio_backend.backend == "vlc":
                import vlc
                state = self.audio_backend.player.get_state()
                if state == vlc.State.Ended:
                    self.on_track_ended()
            elif self.audio_backend.backend == "pygame":
                import pygame
                if not pygame.mixer.music.get_busy() and self.is_playing:
                    self.on_track_ended()
    
    def on_track_ended(self):
        if self.repeat_mode == 1:
            self.audio_backend.stop()
            Clock.schedule_once(lambda dt: self.restart_current_track(), 0.2)
        else:
            downloaded_queue = self.get_downloaded_queue()
            if len(downloaded_queue) > 1:
                self.next_track()
            else:
                self.is_playing = False
                self.player_screen.update_play_button()
    
    def restart_current_track(self):
        if self.repeat_mode == 1 and self.current_track:
            self.audio_backend.load_track(self.current_track, self.on_repeat_track_loaded)
    
    def on_repeat_track_loaded(self, success, message=""):
        if success:
            self.audio_backend.play()
            self.is_playing = True
            self.player_screen.update_play_button()
        else:
            self.is_playing = False
            self.player_screen.update_play_button()
    
    def play_track(self, track_info, playlist=None, index=0):
        if not track_info.get('local_path'):
            Logger.warning("MusicPlayer: Track chua duoc download, khong the phat")
            return
        
        if playlist:
            self.playlist = playlist
            self.current_index = index
        
        track_to_play = track_info.copy()
        track_to_play['url'] = track_info['local_path']
        
        self.current_track = track_to_play
        self.audio_backend.load_track(track_to_play, self.on_track_loaded)
        
        self.sm.current = 'player'
    
    def on_track_loaded(self, success, message=""):
        if success:
            self.audio_backend.play()
            self.is_playing = True
            self.player_screen.update_track_info()
            self.player_screen.update_play_button()
            Logger.info(f"MusicPlayer: Dang phat {self.current_track.get('title', 'Unknown')}")
        else:
            Logger.error(f"MusicPlayer: Loi load track - {message}")
    
    def play_pause(self):
        if self.current_track is None:
            return
            
        if self.is_playing:
            self.audio_backend.pause()
            self.is_playing = False
        else:
            self.audio_backend.play()
            self.is_playing = True
            
        self.player_screen.update_play_button()
    
    def stop(self):
        self.audio_backend.stop()
        self.is_playing = False
        self.player_screen.update_play_button()
    
    def next_track(self):
        downloaded_queue = self.get_downloaded_queue()
        
        if not downloaded_queue:
            Logger.info("MusicPlayer: Khong co bai nao da download de next")
            return
        
        if len(downloaded_queue) <= 1:
            if self.repeat_mode == 1:
                self.audio_backend.set_position(0)
                return
            else:
                return
        
        current_index = self.get_current_index_in_downloaded_queue()
        
        if self.repeat_mode == 1:
            self.audio_backend.set_position(0)
            return
        
        next_index = (current_index + 1) % len(downloaded_queue)
        next_track = downloaded_queue[next_index]
        
        for i, track in enumerate(self.playlist):
            if track.get('url') == next_track.get('url'):
                self.current_index = i
                break
        
        self.play_track(next_track)
    
    def previous_track(self):
        downloaded_queue = self.get_downloaded_queue()
        
        if not downloaded_queue:
            Logger.info("MusicPlayer: Khong co bai nao da download de previous")
            return
        
        if len(downloaded_queue) <= 1:
            if self.repeat_mode == 1:
                self.audio_backend.set_position(0)
                return
            else:
                return
        
        current_index = self.get_current_index_in_downloaded_queue()
        
        if self.repeat_mode == 1:
            self.audio_backend.set_position(0)
            return
        
        prev_index = (current_index - 1) % len(downloaded_queue)
        prev_track = downloaded_queue[prev_index]
        
        for i, track in enumerate(self.playlist):
            if track.get('url') == prev_track.get('url'):
                self.current_index = i
                break
        
        self.play_track(prev_track)
    
    def set_volume(self, volume):
        self.audio_backend.set_volume(volume)
    
    def set_position(self, position):
        self.audio_backend.set_position(position)
    
    def on_stop(self):
        self.audio_backend.cleanup()
        self.file_manager.cleanup_temp_files()
        return True