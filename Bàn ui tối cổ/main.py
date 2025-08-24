import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
import tempfile
import os
import yt_dlp
import time

try:
    import vlc
    VLC_AVAILABLE = True
except:
    VLC_AVAILABLE = False
    try:
        import pygame
        PYGAME_AVAILABLE = True
    except:
        PYGAME_AVAILABLE = False

class SimpleMusicPlayer:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("SoundCloud Music Player")
        self.root.geometry("800x600")
        
        self.backend = None
        self.init_audio_backend()
        
        self.current_track = None
        self.current_file = None
        self.is_playing = False
        self.is_paused = False
        self.temp_files = []
        
        self.setup_ui()
        
    def init_audio_backend(self):
        if VLC_AVAILABLE:
            try:
                self.vlc_instance = vlc.Instance()
                self.player = self.vlc_instance.media_player_new()
                self.backend = "vlc"
                return
            except:
                pass
        
        if PYGAME_AVAILABLE:
            try:
                pygame.mixer.pre_init(frequency=44100, size=-16, channels=2, buffer=1024)
                pygame.mixer.init()
                self.backend = "pygame"
                return
            except:
                pass
        
        messagebox.showerror("Error", "Install: pip install python-vlc (+ VLC Player) or pygame")
        self.root.destroy()
        
    def setup_ui(self):
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        title_text = f"🎵 SoundCloud Music Player ({self.backend.upper()})"
        ttk.Label(main_frame, text=title_text, font=("Arial", 14, "bold")).pack(pady=(0, 10))
        
        search_frame = ttk.LabelFrame(main_frame, text="Tìm kiếm nhạc trên SoundCloud", padding=10)
        search_frame.pack(fill="x", pady=(0, 10))
        
        search_input_frame = ttk.Frame(search_frame)
        search_input_frame.pack(fill="x", pady=(0, 10))
        ttk.Label(search_input_frame, text="Tìm kiếm:").pack(side="left")
        self.search_entry = ttk.Entry(search_input_frame, width=50)
        self.search_entry.pack(side="left", padx=(5, 5), fill="x", expand=True)
        self.search_entry.bind("<Return>", lambda e: self.search_tracks())
        self.search_btn = ttk.Button(search_input_frame, text="🔍 Tìm", command=self.search_tracks)
        self.search_btn.pack(side="left")
        
        ttk.Button(search_frame, text="📁 Mở file local", command=self.load_local_file).pack()
        
        results_frame = ttk.LabelFrame(main_frame, text="Danh sách bài hát", padding=10)
        results_frame.pack(fill="both", expand=True, pady=(0, 10))
        
        columns = ("Title", "Artist", "Duration", "Platform", "URL")
        self.results_tree = ttk.Treeview(results_frame, columns=columns, show="headings", height=8)
        
        self.results_tree.heading("Title", text="Tên bài hát")
        self.results_tree.heading("Artist", text="Nghệ sĩ")
        self.results_tree.heading("Duration", text="Thời lượng")
        self.results_tree.heading("Platform", text="Nguồn")
        self.results_tree.heading("URL", text="URL")
        
        self.results_tree.column("Title", width=200)
        self.results_tree.column("Artist", width=150)
        self.results_tree.column("Duration", width=80)
        self.results_tree.column("Platform", width=80)
        self.results_tree.column("URL", width=200)
        
        scrollbar = ttk.Scrollbar(results_frame, orient="vertical", command=self.results_tree.yview)
        self.results_tree.configure(yscrollcommand=scrollbar.set)
        self.results_tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        self.results_tree.bind("<Double-1>", self.on_track_select)
        
        control_frame = ttk.LabelFrame(main_frame, text="Điều khiển phát nhạc", padding=10)
        control_frame.pack(fill="x")
        
        self.track_info = ttk.Label(control_frame, text="Chưa chọn bài hát", font=("Arial", 10, "bold"))
        self.track_info.pack(pady=(0, 10))
        
        btn_frame = ttk.Frame(control_frame)
        btn_frame.pack(pady=(0, 10))
        self.play_btn = ttk.Button(btn_frame, text="▶ Phát", command=self.play_pause, state="disabled")
        self.play_btn.pack(side="left", padx=5)
        self.stop_btn = ttk.Button(btn_frame, text="⏹ Dừng", command=self.stop, state="disabled")
        self.stop_btn.pack(side="left", padx=5)
        
        vol_frame = ttk.Frame(control_frame)
        vol_frame.pack(pady=(0, 10))
        ttk.Label(vol_frame, text="Âm lượng:").pack(side="left")
        self.volume_var = tk.IntVar(value=70)
        self.volume_scale = ttk.Scale(vol_frame, from_=0, to=100, variable=self.volume_var, 
                                     command=self.update_volume, length=300)
        self.volume_scale.pack(side="left", padx=10)
        self.volume_label = ttk.Label(vol_frame, text="70%")
        self.volume_label.pack(side="left")
        
        self.status = ttk.Label(control_frame, text="Sẵn sàng", foreground="green")
        self.status.pack()
    
    def load_local_file(self):
        filetypes = (
            ('Supported Audio', '*.wav *.mp3 *.ogg *.aiff *.flac *.aac'),
            ('WAV files', '*.wav'),
            ('MP3 files', '*.mp3'),
            ('OGG files', '*.ogg'),
            ('AIFF files', '*.aiff'),
            ('FLAC files', '*.flac'),
            ('AAC files', '*.aac')
        )
        filepath = filedialog.askopenfilename(title='Chọn file nhạc', filetypes=filetypes)
        if filepath:
            name = os.path.basename(filepath)
            self.results_tree.insert("", "end", values=(name, "Local File", "Unknown", "Local", filepath))
            self.status.config(text="Đã thêm file local", foreground="green")
    
    def search_tracks(self):
        query = self.search_entry.get().strip()
        if not query:
            messagebox.showwarning("Cảnh báo", "Vui lòng nhập từ khóa tìm kiếm")
            return
        
        self.status.config(text="Đang tìm kiếm trên SoundCloud...", foreground="orange")
        self.search_btn.config(state="disabled")
        
        def search_thread():
            try:
                search_query = f"scsearch10:{query}"
                ydl_opts = {
                    'quiet': True,
                    'no_warnings': True,
                    'extract_flat': True,
                }
                
                try:
                    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                        results = ydl.extract_info(search_query, download=False)
                        
                        if results and 'entries' in results:
                            self.root.after(0, self.clear_results)
                            count = 0
                            
                            for entry in results['entries']:
                                if entry and count < 10:
                                    title = entry.get('title', 'Unknown Title')
                                    if len(title) > 50:
                                        title = title[:47] + "..."
                                    
                                    artist = entry.get('uploader', 'Unknown Artist')
                                    if len(artist) > 30:
                                        artist = artist[:27] + "..."
                                    
                                    duration = self.format_duration(entry.get('duration', 0))
                                    url = entry.get('webpage_url', entry.get('url', ''))
                                    
                                    if url:
                                        self.root.after(0, lambda t=title, a=artist, d=duration, u=url: 
                                                       self.add_result(t, a, d, "SoundCloud", u))
                                        count += 1
                            
                            if count > 0:
                                self.root.after(0, lambda: self.status.config(text=f"Tìm thấy {count} bài hát", foreground="green"))
                            else:
                                self.root.after(0, lambda: self.status.config(text="Không tìm thấy kết quả", foreground="red"))
                        else:
                            self.root.after(0, lambda: self.status.config(text="Không tìm thấy kết quả", foreground="red"))
                            
                except Exception as search_error:
                    error_msg = f"Lỗi tìm kiếm SoundCloud: {str(search_error)[:50]}..."
                    self.root.after(0, lambda: self.status.config(text=error_msg, foreground="red"))
                    self.root.after(0, lambda: messagebox.showerror("Lỗi tìm kiếm", 
                        f"Không thể tìm kiếm trên SoundCloud:\n{str(search_error)}"))
                        
            except Exception as e:
                self.root.after(0, lambda: self.status.config(text=f"Lỗi: {str(e)[:30]}...", foreground="red"))
            finally:
                self.root.after(0, lambda: self.search_btn.config(state="normal"))
        
        threading.Thread(target=search_thread, daemon=True).start()
    
    def clear_results(self):
        for item in self.results_tree.get_children():
            self.results_tree.delete(item)
    
    def add_result(self, title, artist, duration, platform, url):
        self.results_tree.insert("", "end", values=(title, artist, duration, platform, url))
    
    def format_duration(self, seconds):
        if not seconds:
            return "Unknown"
        minutes, seconds = divmod(int(seconds), 60)
        return f"{minutes:02d}:{seconds:02d}"
    
    def on_track_select(self, event):
        selection = self.results_tree.selection()
        if not selection:
            return
        
        item = self.results_tree.item(selection[0])
        values = item['values']
        if len(values) >= 5:
            title, artist, duration, platform, url = values
            self.load_and_play_track(title, artist, url, platform)
    
    def load_and_play_track(self, title, artist, url, platform="Unknown"):
        self.stop()
        self.status.config(text=f"Đang tải từ {platform}...", foreground="orange")
        
        def load_thread():
            try:
                if os.path.exists(url):
                    media_path = url
                else:
                    temp_dir = tempfile.gettempdir()
                    
                    if self.backend == "vlc":
                        format_selector = 'bestaudio/best'
                    else:
                        format_selector = 'worst[ext=mp4]/worst[ext=webm]/worst'
                    
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
                        
                        if not os.path.exists(media_path):
                            video_id = info.get('id', 'unknown')
                            for ext in ['.mp4', '.webm', '.m4a', '.mp3']:
                                test_file = os.path.join(temp_dir, f'music_{video_id}{ext}')
                                if os.path.exists(test_file):
                                    media_path = test_file
                                    break
                        
                        if media_path not in self.temp_files:
                            self.temp_files.append(media_path)
                
                if not os.path.exists(media_path):
                    raise FileNotFoundError("Không thể tải file nhạc")
                
                self.current_track = {'title': title, 'artist': artist, 'platform': platform}
                self.current_file = media_path
                
                display_text = f"{artist} - {title}"
                if len(display_text) > 60:
                    display_text = display_text[:57] + "..."
                
                self.root.after(0, lambda: self.track_info.config(text=display_text))
                self.root.after(0, lambda: self.play_btn.config(state="normal"))
                self.root.after(0, lambda: self.stop_btn.config(state="normal"))
                
                if self.backend == "vlc":
                    media = self.vlc_instance.media_new(media_path)
                    self.player.set_media(media)
                    self.player.play()
                else:
                    pygame.mixer.music.load(media_path)
                    pygame.mixer.music.play()
                
                self.is_playing = True
                self.root.after(0, lambda: self.play_btn.config(text="⏸ Tạm dừng"))
                self.root.after(0, lambda: self.status.config(text=f"Đang phát từ {platform}", foreground="green"))
                
            except Exception as e:
                error_msg = str(e)
                if "ModPlug" in error_msg:
                    error_msg = "File không tương thích với pygame. Cài VLC để phát tất cả format."
                
                self.root.after(0, lambda: self.status.config(text="Lỗi phát nhạc", foreground="red"))
                self.root.after(0, lambda: messagebox.showerror("Lỗi phát nhạc", error_msg))
        
        threading.Thread(target=load_thread, daemon=True).start()
    
    def play_pause(self):
        if not self.current_file:
            messagebox.showwarning("Cảnh báo", "Chưa chọn bài hát")
            return
        
        try:
            if self.backend == "vlc":
                if self.is_playing:
                    if self.player.get_state() == vlc.State.Playing:
                        self.player.pause()
                        self.play_btn.config(text="▶ Tiếp tục")
                        self.status.config(text="Tạm dừng", foreground="orange")
                    else:
                        self.player.play()
                        self.play_btn.config(text="⏸ Tạm dừng")
                        self.status.config(text="Đang phát", foreground="green")
                else:
                    self.player.play()
                    self.is_playing = True
                    self.play_btn.config(text="⏸ Tạm dừng")
                    self.status.config(text="Đang phát", foreground="green")
            else:
                if not self.is_playing:
                    pygame.mixer.music.load(self.current_file)
                    pygame.mixer.music.play()
                    self.is_playing = True
                    self.is_paused = False
                    self.play_btn.config(text="⏸ Tạm dừng")
                    self.status.config(text="Đang phát", foreground="green")
                else:
                    if self.is_paused:
                        pygame.mixer.music.unpause()
                        self.is_paused = False
                        self.play_btn.config(text="⏸ Tạm dừng")
                        self.status.config(text="Đang phát", foreground="green")
                    else:
                        pygame.mixer.music.pause()
                        self.is_paused = True
                        self.play_btn.config(text="▶ Tiếp tục")
                        self.status.config(text="Tạm dừng", foreground="orange")
        except Exception as e:
            messagebox.showerror("Lỗi", f"Lỗi phát nhạc: {str(e)}")
    
    def stop(self):
        if self.backend == "vlc":
            self.player.stop()
        else:
            pygame.mixer.music.stop()
        
        self.is_playing = False
        self.is_paused = False
        self.play_btn.config(text="▶ Phát")
        self.status.config(text="Đã dừng", foreground="blue")
    
    def update_volume(self, value):
        volume = int(float(value))
        if self.backend == "vlc":
            self.player.audio_set_volume(volume)
        else:
            pygame.mixer.music.set_volume(volume / 100.0)
        self.volume_label.config(text=f"{volume}%")
    
    def run(self):
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.mainloop()
    
    def on_closing(self):
        try:
            if self.backend == "vlc":
                self.player.stop()
            else:
                pygame.mixer.music.stop()
                pygame.mixer.quit()
            
            for temp_file in self.temp_files:
                try:
                    if os.path.exists(temp_file):
                        os.unlink(temp_file)
                except:
                    pass
        except:
            pass
        self.root.destroy()

if __name__ == "__main__":
    print("🎵 SoundCloud Music Player")
    print("Tìm kiếm: Mặc định trên SoundCloud")
    print("Local files: WAV, MP3, OGG, AIFF, FLAC, AAC")
    print("Cài đặt: pip install python-vlc yt-dlp (+ VLC Player)")
    print("Hoặc: pip install pygame yt-dlp")
    
    try:
        app = SimpleMusicPlayer()
        app.run()
    except Exception as e:
        print(f"Lỗi: {e}")
        input("Press Enter to exit...")