def update_bg(self, instance, value):
        self.bg_rect.pos = instance.pos
        self.bg_rect.size = instance.size
    #!/usr/bin/env python3
# -*- coding: utf-8 -*-

import math
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.widget import Widget
from kivy.uix.popup import Popup
from kivy.uix.filechooser import FileChooserListView
from kivy.uix.scrollview import ScrollView
from kivy.graphics import Color, Rectangle, Line, Ellipse
from kivy.graphics.instructions import InstructionGroup
from kivy.core.text import Label as CoreLabel
from kivy.metrics import dp
from kivy.clock import Clock
from ui_base import GradientButton
import threading
import os
import yt_dlp

class VinylDiscWidget(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.selected_tracks = []  # Only tracks added to disc
        self.track_positions = []
        self.rotation_angle = 0
        self.callback = None
        
        self.bind(size=self.update_graphics, pos=self.update_graphics)
        
        # Always start rotation
        Clock.schedule_once(lambda dt: self.start_rotation(), 0.5)
        
    def add_track_to_disc(self, track_info):
        """Add a track to the disc"""
        print(f"VinylDiscWidget: Adding track '{track_info.get('title', 'Unknown')}' to disc")
        print(f"Current tracks on disc: {len(self.selected_tracks)}")
        
        # Check if track already exists
        for existing_track in self.selected_tracks:
            if existing_track.get('url') == track_info.get('url'):
                print("Track already exists on disc, skipping")
                return
        
        self.selected_tracks.append(track_info)
        print(f"Track added. New disc size: {len(self.selected_tracks)}")
        self.calculate_positions()
        self.update_graphics()
        
    def remove_track_from_disc(self, track_info):
        """Remove a track from disc"""
        self.selected_tracks = [t for t in self.selected_tracks if t.get('url') != track_info.get('url')]
        self.calculate_positions()
        self.update_graphics()
        
    def clear_disc(self):
        """Clear all tracks from disc"""
        self.selected_tracks = []
        self.track_positions = []
        self.update_graphics()
        
    def set_callback(self, callback):
        self.callback = callback
    
    def calculate_positions(self):
        if not self.selected_tracks:
            self.track_positions = []
            return
            
        center_x, center_y = self.center_x, self.center_y
        radius = min(self.width, self.height) * 0.25
        
        angle_step = 360.0 / len(self.selected_tracks)
        
        self.track_positions = []
        for i in range(len(self.selected_tracks)):
            angle = math.radians(i * angle_step - 90 + self.rotation_angle)
            x = center_x + math.cos(angle) * radius
            y = center_y + math.sin(angle) * radius
            
            track_data = {
                'x': x,
                'y': y,
                'angle': i * angle_step - 90,
                'downloaded': self.selected_tracks[i].get('local_path') is not None,
                'number': self.selected_tracks[i].get('original_index', i + 1),  # Use original index
                'track': self.selected_tracks[i]
            }
            self.track_positions.append(track_data)
    
    def start_rotation(self):
        self.rotation_event = Clock.schedule_interval(self.update_rotation, 1/30.0)
    
    def stop_rotation(self):
        if hasattr(self, 'rotation_event'):
            self.rotation_event.cancel()
    
    def update_rotation(self, dt):
        self.rotation_angle += 1
        if self.rotation_angle >= 360:
            self.rotation_angle = 0
        self.calculate_positions()
        self.update_graphics()
    
    def update_graphics(self, *args):
        if self.size[0] <= 0 or self.size[1] <= 0:
            return
            
        self.canvas.clear()
        
        with self.canvas:
            # Main disc background
            Color(0.05, 0.05, 0.05, 1)
            disc_radius = min(self.width, self.height) * 0.4
            Ellipse(
                pos=(self.center_x - disc_radius, self.center_y - disc_radius),
                size=(disc_radius * 2, disc_radius * 2)
            )
            
            # Groove lines
            Color(0.1, 0.1, 0.1, 1)
            for i in range(5):
                groove_radius = disc_radius * 0.3 + i * (disc_radius * 0.15)
                Line(circle=(self.center_x, self.center_y, groove_radius), width=1)
            
            # Center label
            Color(0.2, 0.2, 0.2, 1)
            center_radius = disc_radius * 0.2
            Ellipse(
                pos=(self.center_x - center_radius, self.center_y - center_radius),
                size=(center_radius * 2, center_radius * 2)
            )
            
            # Center hole
            Color(0.0, 0.0, 0.0, 1)
            hole_radius = dp(8)
            Ellipse(
                pos=(self.center_x - hole_radius, self.center_y - hole_radius),
                size=(hole_radius * 2, hole_radius * 2)
            )
            
            # Draw tracks with numbers
            track_radius = dp(25)
            for i, pos_data in enumerate(self.track_positions):
                x, y = pos_data['x'], pos_data['y']
                downloaded = pos_data['downloaded']
                number = pos_data['number']
                
                # Track color
                if downloaded:
                    Color(0.1, 0.8, 0.3, 0.9)
                else:
                    Color(0.2, 0.6, 1.0, 0.9)
                
                # Main track circle
                Ellipse(
                    pos=(x - track_radius, y - track_radius),
                    size=(track_radius * 2, track_radius * 2)
                )
                
                # Inner circle for vinyl look
                Color(0.1, 0.1, 0.1, 1)
                inner_radius = track_radius * 0.5
                Ellipse(
                    pos=(x - inner_radius, y - inner_radius),
                    size=(inner_radius * 2, inner_radius * 2)
                )
                

            
            # Draw numbers on top (separate loop to ensure they're visible)
            for i, pos_data in enumerate(self.track_positions):
                x, y = pos_data['x'], pos_data['y']
                number = pos_data['number']
                
                # Create text label
                label = CoreLabel(text=str(number), font_size=dp(14), color=(1, 1, 1, 1))
                label.refresh()
                texture = label.texture
                
                # Position text in center of circle
                text_x = x - texture.width / 2
                text_y = y - texture.height / 2
                
                Color(1, 1, 1, 1)
                Rectangle(texture=texture, pos=(text_x, text_y), size=texture.size)
    
    def on_touch_down(self, touch):
        if not self.collide_point(*touch.pos):
            return False
        
        track_radius = dp(25)
        
        for i, pos_data in enumerate(self.track_positions):
            x, y = pos_data['x'], pos_data['y']
            distance = math.sqrt((touch.pos[0] - x)**2 + (touch.pos[1] - y)**2)
            
            if distance <= track_radius:
                track = pos_data['track']
                
                if track.get('local_path') and self.callback:
                    self.callback(track)
                
                return True
        
        return False

class TrackListWidget(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.tracks = []
        self.on_add_callback = None
        
        # Scrollable track list (no header)
        self.scroll = ScrollView()
        self.track_list = BoxLayout(orientation='vertical', spacing=dp(2), size_hint_y=None)
        self.track_list.bind(minimum_height=self.track_list.setter('height'))
        self.scroll.add_widget(self.track_list)
        self.add_widget(self.scroll)
    
    def set_tracks(self, tracks, on_add_callback=None):
        self.tracks = tracks
        self.on_add_callback = on_add_callback
        self.track_list.clear_widgets()
        
        for i, track in enumerate(tracks):
            # Add original index to track info
            track['original_index'] = i + 1
            
            item_layout = BoxLayout(
                orientation='horizontal', 
                size_hint_y=None, 
                height=dp(40),
                spacing=dp(5)
            )
            
            # Background
            with item_layout.canvas.before:
                Color(0.1, 0.1, 0.15, 0.8)
                item_layout.bg_rect = Rectangle(pos=item_layout.pos, size=item_layout.size)
            item_layout.bind(pos=self.update_item_bg, size=self.update_item_bg)
            
            # Track number
            num_label = Label(
                text=str(i + 1),
                size_hint=(None, 1),
                width=dp(30),
                font_size=dp(12),
                bold=True,
                color=(1, 1, 1, 1)
            )
            item_layout.add_widget(num_label)
            
            # Track info
            info_layout = BoxLayout(orientation='vertical', padding=(0, dp(2)))
            
            title_label = Label(
                text=track.get('title', 'Unknown')[:25] + ('...' if len(track.get('title', '')) > 25 else ''),
                font_size=dp(10),
                color=(1, 1, 1, 1),
                text_size=(None, None),
                halign='left'
            )
            
            artist_label = Label(
                text=track.get('artist', 'Unknown')[:20] + ('...' if len(track.get('artist', '')) > 20 else ''),
                font_size=dp(8),
                color=(0.7, 0.7, 0.7, 1),
                text_size=(None, None),
                halign='left'
            )
            
            info_layout.add_widget(title_label)
            info_layout.add_widget(artist_label)
            item_layout.add_widget(info_layout)
            
            # Duration
            duration_label = Label(
                text=track.get('duration', '?'),
                size_hint=(None, 1),
                width=dp(35),
                font_size=dp(9),
                color=(0.6, 0.6, 0.6, 1)
            )
            item_layout.add_widget(duration_label)
            
            # Add to disc button
            add_btn = GradientButton(
                text='+',
                size_hint=(None, 1),
                width=dp(30),
                font_size=dp(14),
                gradient_colors=[(0.2, 0.8, 0.2, 1), (0.1, 0.6, 0.1, 1)]
            )
            add_btn.track_info = track
            add_btn.bind(on_press=self.on_add_track)
            item_layout.add_widget(add_btn)
            
            self.track_list.add_widget(item_layout)
    
    def on_add_track(self, button):
        if self.on_add_callback:
            self.on_add_callback(button.track_info)
    
    def update_item_bg(self, instance, value):
        if hasattr(instance, 'bg_rect'):
            instance.bg_rect.pos = instance.pos
            instance.bg_rect.size = instance.size

class SearchScreen(Screen):
    def __init__(self, app=None, **kwargs):
        super().__init__(**kwargs)
        self.app = app
        self.search_results = []
        
        # Main layout - initially single layout
        self.main_layout = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(10))
        
        with self.main_layout.canvas.before:
            Color(0.03, 0.03, 0.08, 1)
            self.bg_rect = Rectangle(pos=self.main_layout.pos, size=self.main_layout.size)
        self.main_layout.bind(pos=self.update_bg, size=self.update_bg)
        
        # Header
        header = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(50))
        
        title = Label(
            text='SoundCloud Music Player - Vinyl Mode',
            font_size=dp(18),
            bold=True,
            color=(1, 1, 1, 1)
        )
        header.add_widget(title)
        
        player_btn = GradientButton(text='PLAYER', size_hint=(None, 1), width=dp(100))
        player_btn.bind(on_press=lambda x: setattr(self.app.sm, 'current', 'player'))
        header.add_widget(player_btn)
        
        self.main_layout.add_widget(header)
        
        # Search controls
        search_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(40), spacing=dp(5))
        
        self.search_input = TextInput(
            hint_text='Tim kiem nhac...',
            size_hint=(0.5, 1),
            multiline=False,
            background_color=(0.2, 0.2, 0.2, 1),
            foreground_color=(1, 1, 1, 1),
            font_size=dp(14)
        )
        self.search_input.bind(on_text_validate=self.search_music)
        search_layout.add_widget(self.search_input)
        
        search_btn = GradientButton(text='TIM', size_hint=(None, 1), width=dp(60))
        search_btn.bind(on_press=self.search_music)
        search_layout.add_widget(search_btn)
        
        local_btn = GradientButton(text='FILE', size_hint=(None, 1), width=dp(60))
        local_btn.bind(on_press=self.open_file_chooser)
        search_layout.add_widget(local_btn)
        
        clear_btn = GradientButton(text='XOA', size_hint=(None, 1), width=dp(60))
        clear_btn.bind(on_press=self.clear_results)
        search_layout.add_widget(clear_btn)
        
        self.main_layout.add_widget(search_layout)
        
        # Content area - initially just vinyl disc
        self.content_area = BoxLayout(orientation='vertical')
        
        # Vinyl disc widget
        self.vinyl_disc = VinylDiscWidget()
        self.content_area.add_widget(self.vinyl_disc)
        
        self.main_layout.add_widget(self.content_area)
        
        # Status
        self.status_label = Label(
            text='San sang tim kiem',
            size_hint_y=None,
            height=dp(30),
            color=(0, 1, 0, 1),
            font_size=dp(12)
        )
        self.main_layout.add_widget(self.status_label)
        
        # Track list (initially None)
        self.track_list = None
        self.is_split_layout = False
        
        self.add_widget(self.main_layout)
    
    def update_bg(self, instance, value):
        self.bg_rect.pos = instance.pos
        self.bg_rect.size = instance.size
    
    def on_add_track_to_disc(self, track_info):
        """Add track to disc and download if needed"""
        print(f"Adding track to disc: {track_info.get('title', 'Unknown')}")
        
        # Check if track already on disc
        for existing_track in self.vinyl_disc.selected_tracks:
            if existing_track.get('url') == track_info.get('url'):
                print("Track already on disc, skipping")
                return
        
        if track_info.get('local_path'):
            # Already downloaded, add directly
            print("Track already downloaded, adding to disc")
            self.vinyl_disc.add_track_to_disc(track_info)
        else:
            # Need to download first
            print("Need to download track first")
            # Show downloading status
            self.status_label.text = f'Dang tai: {track_info.get("title", "Unknown")[:30]}...'
            self.status_label.color = (1, 1, 0, 1)
            
            def on_complete(success, filepath=None):
                print(f"Download complete: success={success}, filepath={filepath}")
                if success:
                    track_info['local_path'] = filepath
                    self.vinyl_disc.add_track_to_disc(track_info)
                    self.status_label.text = f'Da them: {track_info.get("title", "Unknown")[:30]}...'
                    self.status_label.color = (0, 1, 0, 1)
                    print("Track added to disc after download")
                else:
                    self.status_label.text = 'Loi tai nhac - Thu lai'
                    self.status_label.color = (1, 0, 0, 1)
                    print("Download failed")
            
            self.download_track(track_info, on_complete)
    

    
    def switch_to_split_layout(self):
        """Chuyển sang layout 2 cột khi có kết quả"""
        if self.is_split_layout:
            return
            
        # Remove vinyl disc from current parent
        if self.vinyl_disc.parent:
            self.vinyl_disc.parent.remove_widget(self.vinyl_disc)
            
        # Remove current content area
        self.main_layout.remove_widget(self.content_area)
        
        # Create horizontal split layout
        split_layout = BoxLayout(orientation='horizontal', spacing=dp(10))
        
        # Left side - disc (70%)
        left_layout = BoxLayout(orientation='vertical', size_hint=(0.7, 1))
        left_layout.add_widget(self.vinyl_disc)
        split_layout.add_widget(left_layout)
        
        # Right side - track list (30%)
        self.track_list = TrackListWidget(size_hint=(0.3, 1))
        split_layout.add_widget(self.track_list)
        
        # Add split layout to main
        self.main_layout.add_widget(split_layout)
        
        self.is_split_layout = True
    
    def switch_to_single_layout(self):
        """Chuyển về layout 1 cột khi xóa kết quả"""
        if not self.is_split_layout:
            return
        
        # Remove vinyl disc from current parent
        if self.vinyl_disc.parent:
            self.vinyl_disc.parent.remove_widget(self.vinyl_disc)
        
        # Find and remove split layout
        for child in self.main_layout.children[:]:
            if isinstance(child, BoxLayout) and child.orientation == 'horizontal':
                self.main_layout.remove_widget(child)
                break
        
        # Recreate single content area
        self.content_area = BoxLayout(orientation='vertical')
        self.content_area.add_widget(self.vinyl_disc)
        self.main_layout.add_widget(self.content_area)
        
        self.track_list = None
        self.is_split_layout = False
    
    def toggle_rotation(self, *args):
        # Remove this method since disc always rotates
        pass
    
    def clear_results(self, *args):
        self.vinyl_disc.clear_disc()
        self.search_results = []
        self.status_label.text = 'Da xoa - San sang tim kiem moi'
        self.status_label.color = (0, 1, 0, 1)
        
        # Switch back to single layout
        self.switch_to_single_layout()
    
    def search_music(self, *args):
        query = self.search_input.text.strip()
        if not query:
            return
        
        self.status_label.text = 'Dang tim kiem...'
        self.status_label.color = (1, 1, 0, 1)
        
        def search_thread():
            try:
                search_query = f"scsearch30:{query}"
                ydl_opts = {
                    'quiet': True,
                    'no_warnings': True,
                    'extract_flat': True,
                }
                
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    results = ydl.extract_info(search_query, download=False)
                    
                    if results and 'entries' in results:
                        tracks = []
                        for entry in results['entries'][:30]:
                            if entry:
                                track_info = {
                                    'title': entry.get('title', 'Unknown Title'),
                                    'artist': entry.get('uploader', 'Unknown Artist'),
                                    'duration': self.format_duration(entry.get('duration', 0)),
                                    'url': entry.get('webpage_url', ''),
                                    'platform': 'SoundCloud'
                                }
                                tracks.append(track_info)
                        
                        self.search_results = tracks
                        Clock.schedule_once(lambda dt: self.display_results(tracks), 0)
                        Clock.schedule_once(lambda dt: self.update_status(f'Tim thay {len(tracks)} bai', (0, 1, 0, 1)), 0)
                    else:
                        Clock.schedule_once(lambda dt: self.update_status('Khong tim thay', (1, 0, 0, 1)), 0)
                        
            except Exception as e:
                Clock.schedule_once(lambda dt: self.update_status(f'Loi: {str(e)[:30]}', (1, 0, 0, 1)), 0)
        
        threading.Thread(target=search_thread, daemon=True).start()
    
    def display_results(self, tracks):
        # Switch to split layout when showing results
        self.switch_to_split_layout()
        
        # Clear disc but keep it rotating
        self.vinyl_disc.clear_disc()
        self.vinyl_disc.set_callback(self.on_track_select)
        
        if self.track_list:
            self.track_list.set_tracks(tracks, on_add_callback=self.on_add_track_to_disc)
    
    def download_track(self, track_info, complete_callback):
        def download_thread():
            try:
                import tempfile
                temp_dir = tempfile.gettempdir()
                
                print(f"Starting download for: {track_info.get('title', 'Unknown')}")
                print(f"URL: {track_info.get('url', '')}")
                
                ydl_opts = {
                    'format': 'bestaudio/best',
                    'outtmpl': os.path.join(temp_dir, '%(title)s.%(ext)s'),
                    'quiet': True,
                    'no_warnings': True,
                    'retries': 3,
                    'fragment_retries': 3,
                }
                
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(track_info['url'], download=True)
                    filepath = ydl.prepare_filename(info)
                    
                    # Check if file actually exists and has reasonable size
                    if os.path.exists(filepath) and os.path.getsize(filepath) > 1000:  # At least 1KB
                        print(f"Download successful: {filepath} ({os.path.getsize(filepath)} bytes)")
                        Clock.schedule_once(lambda dt: complete_callback(True, filepath), 0)
                    else:
                        print(f"Download failed: File doesn't exist or too small")
                        Clock.schedule_once(lambda dt: complete_callback(False), 0)
                    
            except Exception as e:
                print(f"Download error: {e}")
                Clock.schedule_once(lambda dt: complete_callback(False), 0)
        
        threading.Thread(target=download_thread, daemon=True).start()
    
    def refresh_track_list(self):
        if self.track_list:
            self.track_list.set_tracks(self.search_results)
    
    def format_duration(self, seconds):
        if not seconds:
            return "?"
        minutes, seconds = divmod(int(seconds), 60)
        return f"{minutes:02d}:{seconds:02d}"
    
    def update_status(self, message, color):
        self.status_label.text = message
        self.status_label.color = color
    
    def on_track_select(self, track_info):
        if track_info.get('local_path'):
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
                self.search_results.append(track_info)
                self.display_results(self.search_results)
                popup.dismiss()
        
        select_btn.bind(on_press=on_select)
        cancel_btn.bind(on_press=popup.dismiss)
        
        popup.open()