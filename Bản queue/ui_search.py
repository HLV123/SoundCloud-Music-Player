#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView
from kivy.uix.popup import Popup
from kivy.uix.filechooser import FileChooserListView
from kivy.uix.progressbar import ProgressBar
from kivy.graphics import Color, RoundedRectangle
from kivy.metrics import dp
from kivy.clock import Clock
from ui_base import GradientButton
import threading
import os
import yt_dlp

class DownloadTrackWidget(BoxLayout):
    """Widget hiển thị track với nút download"""
    def __init__(self, track_info, callback=None, download_callback=None, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'horizontal'
        self.size_hint_y = None
        self.height = dp(80)
        self.track_info = track_info
        self.callback = callback
        self.download_callback = download_callback
        self.is_downloaded = False
        
        with self.canvas.before:
            Color(0.1, 0.1, 0.1, 0.8)
            self.rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[dp(8)])
        self.bind(pos=self.update_rect, size=self.update_rect)
        
        info_layout = BoxLayout(orientation='vertical', padding=dp(15))
        
        title = Label(
            text=track_info.get('title', 'Unknown Title')[:50],
            font_size=dp(16),
            bold=True,
            color=(1, 1, 1, 1),
            text_size=(None, None),
            halign='left',
            valign='top'
        )
        
        artist = Label(
            text=track_info.get('artist', 'Unknown Artist')[:40],
            font_size=dp(12),
            color=(0.8, 0.8, 0.8, 1),
            text_size=(None, None),
            halign='left',
            valign='bottom'
        )
        
        info_layout.add_widget(title)
        info_layout.add_widget(artist)
        self.add_widget(info_layout)
        
        duration_label = Label(
            text=track_info.get('duration', '00:00'),
            size_hint=(None, 1),
            width=dp(60),
            color=(0.6, 0.6, 0.6, 1)
        )
        self.add_widget(duration_label)
        
        self.download_btn = GradientButton(
            text='DOWNLOAD',
            size_hint=(None, 1),
            width=dp(90),
            font_size=dp(10),
            gradient_colors=[(0.8, 0.4, 0.1, 1), (0.6, 0.3, 0.1, 1)]
        )
        self.download_btn.bind(on_press=self.on_download)
        self.add_widget(self.download_btn)
        
        self.play_btn = GradientButton(
            text='PLAY',
            size_hint=(None, 1),
            width=dp(60),
            font_size=dp(12),
            gradient_colors=[(0.5, 0.5, 0.5, 1), (0.3, 0.3, 0.3, 1)]
        )
        self.play_btn.bind(on_press=self.on_play)
        self.add_widget(self.play_btn)
        
        # Disable play button initially
        self.play_btn.disabled = True
    
    def update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size
    
    def on_download(self, *args):
        if self.is_downloaded:
            return
            
        self.download_btn.text = 'DOWNLOADING...'
        self.download_btn.gradient_colors = [(0.5, 0.5, 0.5, 1), (0.3, 0.3, 0.3, 1)]
        self.download_btn.update_graphics()
        self.download_btn.disabled = True
        
        if self.download_callback:
            self.download_callback(self.track_info, self.on_download_complete)
    
    def on_download_complete(self, success, filepath=None):
        if success:
            self.is_downloaded = True
            self.track_info['local_path'] = filepath
            self.download_btn.text = 'DOWNLOADED'
            self.download_btn.gradient_colors = [(0.1, 0.8, 0.3, 1), (0.05, 0.6, 0.2, 1)]
            self.download_btn.update_graphics()
            
            # Enable play button
            self.play_btn.disabled = False
            self.play_btn.gradient_colors = [(0.1, 0.8, 0.3, 1), (0.05, 0.6, 0.2, 1)]
            self.play_btn.update_graphics()
        else:
            self.download_btn.text = 'FAILED'
            self.download_btn.gradient_colors = [(0.8, 0.1, 0.1, 1), (0.6, 0.05, 0.05, 1)]
            self.download_btn.update_graphics()
            self.download_btn.disabled = False
    
    def on_play(self, *args):
        if self.is_downloaded and self.callback:
            self.callback(self.track_info)

class SearchScreen(Screen):
    """Màn hình tìm kiếm với download"""
    def __init__(self, app=None, **kwargs):
        super().__init__(**kwargs)
        self.app = app
        self.search_results = []
        
        main_layout = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(15))
        
        with main_layout.canvas.before:
            Color(0.05, 0.05, 0.1, 1)
            self.bg_rect = RoundedRectangle(pos=main_layout.pos, size=main_layout.size)
        main_layout.bind(pos=self.update_bg, size=self.update_bg)
        
        header = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(60))
        
        title = Label(
            text='SoundCloud Music Player',
            font_size=dp(24),
            bold=True,
            color=(1, 1, 1, 1)
        )
        header.add_widget(title)
        
        player_btn = GradientButton(text='PLAYER', size_hint=(None, 1), width=dp(120))
        player_btn.bind(on_press=lambda x: setattr(self.app.sm, 'current', 'player'))
        header.add_widget(player_btn)
        
        main_layout.add_widget(header)
        
        search_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(50), spacing=dp(10))
        
        self.search_input = TextInput(
            hint_text='Tim kiem nhac tren SoundCloud...',
            size_hint=(0.7, 1),
            multiline=False,
            background_color=(0.2, 0.2, 0.2, 1),
            foreground_color=(1, 1, 1, 1),
            font_size=dp(35)
        )
        self.search_input.bind(on_text_validate=self.search_music)
        search_layout.add_widget(self.search_input)
        
        search_btn = GradientButton(text='TIM', size_hint=(0.15, 1))
        search_btn.bind(on_press=self.search_music)
        search_layout.add_widget(search_btn)
        
        local_btn = GradientButton(text='FILE LOCAL', size_hint=(0.15, 1))
        local_btn.bind(on_press=self.open_file_chooser)
        search_layout.add_widget(local_btn)
        
        main_layout.add_widget(search_layout)
        
        self.results_scroll = ScrollView()
        self.results_layout = BoxLayout(orientation='vertical', spacing=dp(5), size_hint_y=None)
        self.results_layout.bind(minimum_height=self.results_layout.setter('height'))
        self.results_scroll.add_widget(self.results_layout)
        main_layout.add_widget(self.results_scroll)
        
        self.status_label = Label(
            text='San sang tim kiem',
            size_hint_y=None,
            height=dp(30),
            color=(0, 1, 0, 1)
        )
        main_layout.add_widget(self.status_label)
        
        self.add_widget(main_layout)
    
    def update_bg(self, instance, value):
        self.bg_rect.pos = instance.pos
        self.bg_rect.size = instance.size
    
    def search_music(self, *args):
        query = self.search_input.text.strip()
        if not query:
            return
        
        self.status_label.text = 'Dang tim kiem...'
        self.status_label.color = (1, 1, 0, 1)
        
        def search_thread():
            try:
                search_query = f"scsearch10:{query}"
                ydl_opts = {
                    'quiet': True,
                    'no_warnings': True,
                    'extract_flat': True,
                }
                
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    results = ydl.extract_info(search_query, download=False)
                    
                    if results and 'entries' in results:
                        Clock.schedule_once(lambda dt: self.clear_results(), 0)
                        
                        for entry in results['entries'][:10]:
                            if entry:
                                track_info = {
                                    'title': entry.get('title', 'Unknown Title'),
                                    'artist': entry.get('uploader', 'Unknown Artist'),
                                    'duration': self.format_duration(entry.get('duration', 0)),
                                    'url': entry.get('webpage_url', ''),
                                    'platform': 'SoundCloud'
                                }
                                Clock.schedule_once(lambda dt, track=track_info: self.add_result(track), 0)
                        
                        Clock.schedule_once(lambda dt: self.update_status(f'Tim thay {len(results["entries"])} bai hat', (0, 1, 0, 1)), 0)
                    else:
                        Clock.schedule_once(lambda dt: self.update_status('Khong tim thay ket qua', (1, 0, 0, 1)), 0)
                        
            except Exception as e:
                error_msg = f'Loi tim kiem: {str(e)[:50]}'
                Clock.schedule_once(lambda dt: self.update_status(error_msg, (1, 0, 0, 1)), 0)
        
        threading.Thread(target=search_thread, daemon=True).start()
    
    def download_track(self, track_info, complete_callback):
        """Download track hoàn toàn"""
        def download_thread():
            try:
                import tempfile
                temp_dir = tempfile.gettempdir()
                
                ydl_opts = {
                    'format': 'bestaudio/best',
                    'outtmpl': os.path.join(temp_dir, '%(title)s.%(ext)s'),
                    'quiet': True,
                    'no_warnings': True,
                }
                
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(track_info['url'], download=True)
                    filepath = ydl.prepare_filename(info)
                    Clock.schedule_once(lambda dt: complete_callback(True, filepath), 0)
                    
            except Exception as e:
                print(f"Download error: {e}")
                Clock.schedule_once(lambda dt: complete_callback(False), 0)
        
        threading.Thread(target=download_thread, daemon=True).start()
    
    def format_duration(self, seconds):
        if not seconds:
            return "Unknown"
        minutes, seconds = divmod(int(seconds), 60)
        return f"{minutes:02d}:{seconds:02d}"
    
    def clear_results(self):
        self.results_layout.clear_widgets()
        self.search_results = []
    
    def add_result(self, track_info):
        track_widget = DownloadTrackWidget(
            track_info, 
            callback=self.on_track_select,
            download_callback=self.download_track
        )
        self.results_layout.add_widget(track_widget)
        self.search_results.append(track_info)
    
    def update_status(self, message, color):
        self.status_label.text = message
        self.status_label.color = color
    
    def on_track_select(self, track_info):
        if track_info.get('local_path'):
            # Sử dụng file đã download
            track_info['url'] = track_info['local_path']
        self.app.play_track(track_info, self.search_results, self.search_results.index(track_info))
    
    def open_file_chooser(self, *args):
        content = BoxLayout(orientation='vertical')
        
        filechooser = FileChooserListView(
            filters=['*.mp3', '*.wav', '*.ogg', '*.m4a', '*.flac', '*.aac']
        )
        content.add_widget(filechooser)
        
        buttons = BoxLayout(size_hint_y=None, height=dp(50), spacing=dp(10))
        
        select_btn = Button(text='CHON', size_hint=(0.5, 1))
        cancel_btn = Button(text='HUY', size_hint=(0.5, 1))
        
        buttons.add_widget(select_btn)
        buttons.add_widget(cancel_btn)
        content.add_widget(buttons)
        
        popup = Popup(title='Chon file nhac', content=content, size_hint=(0.8, 0.8))
        
        def on_select(*args):
            if filechooser.selection:
                filepath = filechooser.selection[0]
                track_info = {
                    'title': os.path.basename(filepath),
                    'artist': 'Local File',
                    'duration': 'Unknown',
                    'url': filepath,
                    'platform': 'Local',
                    'local_path': filepath
                }
                self.add_result(track_info)
                popup.dismiss()
        
        select_btn.bind(on_press=on_select)
        cancel_btn.bind(on_press=popup.dismiss)
        
        popup.open()