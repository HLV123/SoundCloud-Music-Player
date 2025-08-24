#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from kivy.uix.slider import Slider
from kivy.graphics import Color, Rectangle, Ellipse
from kivy.metrics import dp

class ProgressSlider(Slider):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.thumb_size = dp(20)
        self.track_height = dp(4)
        self.bind(pos=self.update_graphics, size=self.update_graphics)
        self.bind(value=self.update_graphics)
        
    def get_norm_value(self):
        if self.max == self.min:
            return 0
        return (self.value - self.min) / (self.max - self.min)
    
    def get_thumb_x(self):
        track_width = self.width - self.thumb_size
        track_start_x = self.x + self.thumb_size / 2
        norm_value = self.get_norm_value()
        thumb_x = track_start_x + norm_value * track_width
        return thumb_x
    
    def update_graphics(self, *args):
        self.canvas.clear()
        
        with self.canvas:
            Color(0.3, 0.3, 0.3, 1)
            track_y = self.center_y - self.track_height / 2
            Rectangle(
                pos=(self.x + self.thumb_size / 2, track_y),
                size=(self.width - self.thumb_size, self.track_height)
            )
            
            Color(0.2, 0.7, 1, 1)
            norm_value = self.get_norm_value()
            progress_width = (self.width - self.thumb_size) * norm_value
            
            if progress_width > 0:
                Rectangle(
                    pos=(self.x + self.thumb_size / 2, track_y),
                    size=(progress_width, self.track_height)
                )
            
            Color(1, 1, 1, 1)
            thumb_x = self.get_thumb_x()
            thumb_y = self.center_y - self.thumb_size / 2
            
            Ellipse(
                pos=(thumb_x - self.thumb_size / 2, thumb_y),
                size=(self.thumb_size, self.thumb_size)
            )
    
    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            track_start_x = self.x + self.thumb_size / 2
            track_width = self.width - self.thumb_size
            
            relative_x = (touch.pos[0] - track_start_x) / track_width
            relative_x = max(0, min(1, relative_x))
            
            new_value = self.min + relative_x * (self.max - self.min)
            self.value = new_value
            
            touch.grab(self)
            return True
        return False
    
    def on_touch_move(self, touch):
        if touch.grab_current is self:
            track_start_x = self.x + self.thumb_size / 2
            track_width = self.width - self.thumb_size
            
            relative_x = (touch.pos[0] - track_start_x) / track_width
            relative_x = max(0, min(1, relative_x))
            
            new_value = self.min + relative_x * (self.max - self.min)
            self.value = new_value
            
            return True
        return False
    
    def on_touch_up(self, touch):
        if touch.grab_current is self:
            touch.ungrab(self)
            return True
        return False