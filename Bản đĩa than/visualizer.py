#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import random
import math
from kivy.uix.widget import Widget
from kivy.graphics import Color, Rectangle
from kivy.clock import Clock
from kivy.metrics import dp

class AudioVisualizer(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        self.bar_count = 120
        self.bar_width = dp(6)
        self.bar_spacing = dp(2)
        self.max_height = dp(300)
        self.min_height = dp(8)
        
        self.audio_data = [0.1] * self.bar_count
        self.target_data = [0.1] * self.bar_count
        self.velocity_data = [0.0] * self.bar_count
        
        self.scroll_offset = 0
        self.is_playing = False
        self.time_accumulator = 0
        
        self.colors = [
            (0.1, 0.8, 0.3, 1),
            (0.3, 0.9, 0.5, 1),
            (0.9, 0.9, 0.2, 1),
            (1.0, 0.6, 0.2, 1),
            (1.0, 0.3, 0.3, 1),
            (0.8, 0.2, 1.0, 1),
            (0.2, 0.6, 1.0, 1),
        ]
        
        self.bind(size=self.update_graphics)
        self.bind(pos=self.update_graphics)
        self.animation_event = None
    
    def start_animation(self):
        self.is_playing = True
        if self.animation_event:
            self.animation_event.cancel()
        self.animation_event = Clock.schedule_interval(self.update_animation, 1/60.0)
    
    def stop_animation(self):
        self.is_playing = False
        if self.animation_event:
            self.animation_event.cancel()
            self.animation_event = None
        self.fade_out_animation()
    
    def fade_out_animation(self):
        def fade_step(dt):
            fade_complete = True
            for i in range(self.bar_count):
                if self.audio_data[i] > 0.05:
                    self.audio_data[i] *= 0.95
                    fade_complete = False
            
            if fade_complete:
                return False
            
            self.update_graphics()
            return True
        
        Clock.schedule_interval(fade_step, 1/30.0)
    
    def update_animation(self, dt):
        if not self.is_playing:
            return
        
        self.time_accumulator += dt
        self.scroll_offset += dp(2)
        
        self.generate_smooth_audio_data(dt)
        self.apply_physics_smoothing(dt)
        self.update_graphics()
    
    def generate_smooth_audio_data(self, dt):
        time_factor = self.time_accumulator
        
        for i in range(self.bar_count):
            freq_base = i / self.bar_count * 2 * math.pi
            
            bass = math.sin(time_factor * 2.0 + freq_base * 0.5) * 0.6
            mid = math.sin(time_factor * 4.0 + freq_base * 1.5) * 0.4
            high = math.sin(time_factor * 8.0 + freq_base * 3.0) * 0.3
            
            noise = (random.random() - 0.5) * 0.1
            amplitude = abs(bass + mid + high + noise)
            
            beat = abs(math.sin(time_factor * 3.0)) * 0.4
            amplitude += beat
            
            amplitude = max(0.05, min(1.5, amplitude))
            amplitude = self.smooth_curve(amplitude)
            
            self.target_data[i] = amplitude
    
    def smooth_curve(self, value):
        return value * value * (3.0 - 2.0 * value)
    
    def apply_physics_smoothing(self, dt):
        spring_strength = 15.0
        damping = 8.0
        
        for i in range(self.bar_count):
            diff = self.target_data[i] - self.audio_data[i]
            force = diff * spring_strength
            
            self.velocity_data[i] += force * dt
            self.velocity_data[i] *= (1.0 - damping * dt)
            
            self.audio_data[i] += self.velocity_data[i] * dt
            self.audio_data[i] = max(0.05, min(2.0, self.audio_data[i]))
    
    def update_graphics(self, *args):
        if self.size[0] <= 0 or self.size[1] <= 0:
            return
            
        self.canvas.clear()
        
        with self.canvas:
            Color(0.02, 0.02, 0.08, 0.95)
            Rectangle(pos=self.pos, size=self.size)
            
            total_width = self.bar_count * (self.bar_width + self.bar_spacing)
            start_x = self.center_x - total_width / 2
            
            if total_width > self.width:
                available_width = self.width - dp(20)
                scale_factor = available_width / total_width
                scaled_bar_width = self.bar_width * scale_factor
                scaled_spacing = self.bar_spacing * scale_factor
                start_x = self.x + dp(10)
            else:
                scaled_bar_width = self.bar_width
                scaled_spacing = self.bar_spacing
            
            for i in range(self.bar_count):
                bar_x = start_x + i * (scaled_bar_width + scaled_spacing)
                
                amplitude = self.audio_data[i]
                bar_height = self.min_height + amplitude * (self.max_height - self.min_height)
                bar_y = self.center_y - bar_height / 2
                
                color = self.get_smooth_color(amplitude, i)
                Color(*color)
                
                Rectangle(
                    pos=(bar_x, bar_y),
                    size=(scaled_bar_width, bar_height)
                )
                
                if amplitude > 0.5:
                    glow_intensity = (amplitude - 0.5) * 0.4
                    Color(color[0], color[1], color[2], glow_intensity)
                    
                    glow_size = dp(3)
                    Rectangle(
                        pos=(bar_x - glow_size/2, bar_y - glow_size),
                        size=(scaled_bar_width + glow_size, bar_height + glow_size*2)
                    )
                
                if amplitude > 0.3:
                    reflection_height = bar_height * 0.3 * amplitude
                    reflection_alpha = 0.15 * amplitude
                    Color(color[0], color[1], color[2], reflection_alpha)
                    
                    Rectangle(
                        pos=(bar_x, self.center_y - reflection_height),
                        size=(scaled_bar_width, reflection_height)
                    )
    
    def get_smooth_color(self, amplitude, index):
        color_float = amplitude * (len(self.colors) - 1)
        color_index = int(color_float)
        blend_factor = color_float - color_index
        
        color_index = max(0, min(len(self.colors) - 2, color_index))
        
        color1 = self.colors[color_index]
        color2 = self.colors[color_index + 1]
        
        blended_color = (
            color1[0] + (color2[0] - color1[0]) * blend_factor,
            color1[1] + (color2[1] - color1[1]) * blend_factor,
            color1[2] + (color2[2] - color1[2]) * blend_factor,
            color1[3]
        )
        
        time_offset = self.time_accumulator * 2.0 + index * 0.1
        color_variation = math.sin(time_offset) * 0.1
        
        return (
            max(0, min(1, blended_color[0] + color_variation)),
            max(0, min(1, blended_color[1] + color_variation)),
            max(0, min(1, blended_color[2] + color_variation)),
            blended_color[3]
        )
    
    def set_audio_data(self, data):
        if len(data) == self.bar_count:
            for i in range(self.bar_count):
                self.target_data[i] = data[i]
    
    def set_playing(self, is_playing):
        if is_playing:
            self.start_animation()
        else:
            self.stop_animation()