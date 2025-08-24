#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from kivy.uix.button import Button
from kivy.uix.slider import Slider
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.graphics import Color, RoundedRectangle
from kivy.metrics import dp

class GradientButton(Button):
    def __init__(self, gradient_colors=[(0.2, 0.6, 1, 1), (0.1, 0.4, 0.8, 1)], **kwargs):
        super().__init__(**kwargs)
        self.gradient_colors = gradient_colors
        self.background_normal = ''
        self.background_color = (0, 0, 0, 0)
        self.original_size = None
        self.bind(pos=self.update_graphics, size=self.update_graphics)
        self.bind(on_press=self.on_press_effect)
        self.bind(on_release=self.on_release_effect)
        
    def on_enter(self):
        if not self.original_size:
            self.original_size = self.size[:]
        self.size = (self.original_size[0] * 1.1, self.original_size[1] * 1.1)
        
    def on_leave(self):
        if self.original_size:
            self.size = self.original_size
        
    def update_graphics(self, *args):
        self.canvas.before.clear()
        with self.canvas.before:
            Color(*self.gradient_colors[0])
            self.rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[dp(10)])
    
    def on_press_effect(self, *args):
        with self.canvas.before:
            Color(*self.gradient_colors[1])
            self.rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[dp(10)])
    
    def on_release_effect(self, *args):
        with self.canvas.before:
            Color(*self.gradient_colors[0])
            self.rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[dp(10)])

class StylishSlider(Slider):
    """Slider với style đẹp"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

class TrackWidget(BoxLayout):
    """Widget hiển thị một track trong danh sách"""
    def __init__(self, track_info, callback=None, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'horizontal'
        self.size_hint_y = None
        self.height = dp(80)
        self.track_info = track_info
        self.callback = callback
        
        # Background
        with self.canvas.before:
            Color(0.1, 0.1, 0.1, 0.8)
            self.rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[dp(8)])
        self.bind(pos=self.update_rect, size=self.update_rect)
        
        # Track info
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
        
        # Duration
        duration_label = Label(
            text=track_info.get('duration', '00:00'),
            size_hint=(None, 1),
            width=dp(60),
            color=(0.6, 0.6, 0.6, 1)
        )
        self.add_widget(duration_label)
        
        # Play button
        play_btn = GradientButton(
            text='PLAY',
            size_hint=(None, 1),
            width=dp(60),
            font_size=dp(12)
        )
        play_btn.bind(on_press=self.on_play)
        self.add_widget(play_btn)
    
    def update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size
    
    def on_play(self, *args):
        if self.callback:
            self.callback(self.track_info)