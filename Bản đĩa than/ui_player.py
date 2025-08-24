#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.graphics import Color, RoundedRectangle
from kivy.metrics import dp
from ui_base import GradientButton, StylishSlider
from slider import ProgressSlider
from visualizer import AudioVisualizer
import time

class PlayerScreen(Screen):
    """Màn hình phát nhạc chính với visualizer"""
    def __init__(self, app=None, **kwargs):
        super().__init__(**kwargs)
        self.app = app
        
        main_layout = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(10))
        
        with main_layout.canvas.before:
            Color(0.03, 0.03, 0.08, 1)
            self.bg_rect = RoundedRectangle(pos=main_layout.pos, size=main_layout.size)
        main_layout.bind(pos=self.update_bg, size=self.update_bg)
        
        header = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(40), pos_hint={'top': 1})
        
        back_btn = GradientButton(text='< TIM KIEM', size_hint=(None, 1), width=dp(120))
        back_btn.bind(on_press=lambda x: setattr(self.app.sm, 'current', 'search'))
        header.add_widget(back_btn)
        
        header.add_widget(Label())
        main_layout.add_widget(header)
        
        self.visualizer = AudioVisualizer(size_hint=(1, 0.5))
        main_layout.add_widget(self.visualizer)
        
        info_layout = BoxLayout(orientation='vertical', size_hint_y=None, height=dp(80), spacing=dp(5))
        
        self.title_label = Label(
            text='Chua chon bai hat',
            font_size=dp(28),
            bold=True,
            color=(1, 1, 1, 1),
            text_size=(None, None),
            halign='center'
        )
        
        self.artist_label = Label(
            text='Unknown Artist',
            font_size=dp(20),
            color=(0.8, 0.8, 0.8, 1),
            text_size=(None, None),
            halign='center'
        )
        
        info_layout.add_widget(self.title_label)
        info_layout.add_widget(self.artist_label)
        main_layout.add_widget(info_layout)
        
        main_layout.add_widget(self.create_progress_section())
        
        control_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(80), spacing=dp(20))
        control_layout.add_widget(Label())
        
        prev_btn = GradientButton(text='PREV', size_hint=(None, 1), width=dp(80), font_size=dp(14))
        prev_btn.bind(on_press=self.previous_track)
        control_layout.add_widget(prev_btn)
        
        self.play_btn = GradientButton(
            text='PLAY',
            size_hint=(None, 1),
            width=dp(100),
            font_size=dp(16),
            gradient_colors=[(0.1, 0.8, 0.3, 1), (0.05, 0.6, 0.2, 1)]
        )
        self.play_btn.bind(on_press=self.play_pause)
        control_layout.add_widget(self.play_btn)
        
        next_btn = GradientButton(text='NEXT', size_hint=(None, 1), width=dp(80), font_size=dp(14))
        next_btn.bind(on_press=self.next_track)
        control_layout.add_widget(next_btn)
        
        control_layout.add_widget(Label())
        main_layout.add_widget(control_layout)
        
        repeat_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(60), spacing=dp(15))
        repeat_layout.add_widget(Label())
        
        self.repeat_one_btn = GradientButton(text='REPEAT ONE', size_hint=(None, 1), width=dp(200), font_size=dp(14))
        self.repeat_one_btn.bind(on_press=self.toggle_repeat_one)
        repeat_layout.add_widget(self.repeat_one_btn)
        
        repeat_layout.add_widget(Label())
        main_layout.add_widget(repeat_layout)
        
        volume_container = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(50))
        volume_container.add_widget(Label(size_hint=(0.25, 1)))
        
        volume_layout = BoxLayout(orientation='horizontal', size_hint=(0.5, 1), spacing=dp(10))
        
        volume_layout.add_widget(Label(text='VOL', size_hint=(None, 1), width=dp(30)))
        
        self.volume_slider = StylishSlider(min=0, max=100, value=70)
        self.volume_slider.bind(value=self.on_volume_change)
        volume_layout.add_widget(self.volume_slider)
        
        self.volume_label = Label(text='70%', size_hint=(None, 1), width=dp(50), color=(0.8, 0.8, 0.8, 1))
        volume_layout.add_widget(self.volume_label)
        
        volume_container.add_widget(volume_layout)
        volume_container.add_widget(Label(size_hint=(0.25, 1)))
        main_layout.add_widget(volume_container)
        
        self.add_widget(main_layout)
        self.update_repeat_button()
    
    def create_progress_section(self):
        """Tạo phần điều khiển progress với chiều rộng full"""
        progress_container = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(40))
        
        self.time_label = Label(text='00:00', size_hint=(None, 1), width=dp(60), color=(0.8, 0.8, 0.8, 1))
        progress_container.add_widget(self.time_label)
        
        self.progress_slider = ProgressSlider(min=0, max=100, value=0)
        self.progress_slider.bind(on_touch_up=self.on_progress_seek)
        progress_container.add_widget(self.progress_slider)
        
        self.duration_label = Label(text='00:00', size_hint=(None, 1), width=dp(60), color=(0.8, 0.8, 0.8, 1))
        progress_container.add_widget(self.duration_label)
        
        return progress_container

    def on_progress_seek(self, instance, touch):
        """Xử lý khi người dùng seek"""
        if instance.max > 0:
            position = instance.value / instance.max
            if self.app.audio_backend.backend == "vlc":
                self.app.set_position(position)
                print(f"Seeking to: {self.format_time(instance.value)}")
            else:
                print("Seeking không được hỗ trợ với Pygame backend")
        return True
    
    def update_bg(self, instance, value):
        self.bg_rect.pos = instance.pos
        self.bg_rect.size = instance.size
    
    def update_track_info(self):
        if self.app.current_track:
            track = self.app.current_track
            self.title_label.text = track.get('title', 'Unknown Title')
            self.artist_label.text = track.get('artist', 'Unknown Artist')
            
            duration = self.app.audio_backend.get_duration()
            if duration > 0:
                self.duration_label.text = self.format_time(duration)
                self.progress_slider.max = duration
    
    def update_play_button(self):
        if self.app.is_playing:
            self.play_btn.text = 'PAUSE'
            self.visualizer.set_playing(True)
        else:
            self.play_btn.text = 'PLAY'
            self.visualizer.set_playing(False)
    
    def update_position(self):
        """Cập nhật vị trí hiện tại"""            
        if self.app.current_track and self.app.is_playing:
            current_time = self.app.audio_backend.get_time()
            self.time_label.text = self.format_time(current_time)
            
            if current_time > 0:
                self.progress_slider.value = current_time
    
    def format_time(self, seconds):
        minutes = int(seconds) // 60
        seconds = int(seconds) % 60
        return f"{minutes:02d}:{seconds:02d}"
    
    def play_pause(self, *args):
        self.app.play_pause()
    
    def previous_track(self, *args):
        self.app.previous_track()
    
    def next_track(self, *args):
        self.app.next_track()
    
    def toggle_repeat_one(self, *args):
        """Toggle repeat one mode"""
        if self.app.repeat_mode == 1:
            self.app.repeat_mode = 0
        else:
            self.app.repeat_mode = 1
        self.update_repeat_button()
    
    def update_repeat_button(self):
        """Update repeat button appearance"""
        default_colors = [(0.2, 0.6, 1, 1), (0.1, 0.4, 0.8, 1)]
        active_colors = [(0.1, 0.8, 0.3, 1), (0.05, 0.6, 0.2, 1)]
        
        if self.app.repeat_mode == 1:
            self.repeat_one_btn.gradient_colors = active_colors
            self.repeat_one_btn.text = 'REPEAT ONE ✓'
        else:
            self.repeat_one_btn.gradient_colors = default_colors
            self.repeat_one_btn.text = 'REPEAT ONE'
        
        self.repeat_one_btn.update_graphics()
    
    def on_volume_change(self, instance, value):
        volume = value / 100.0
        self.app.set_volume(volume)
        self.volume_label.text = f"{int(value)}%"