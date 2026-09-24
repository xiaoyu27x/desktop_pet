"""
音乐播放器模块 - 支持随机播放、列表管理、音量控制
"""
import os
import random
import json
from PyQt5.QtCore import QUrl, QTimer, pyqtSignal, QObject
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent

# 加密资源加载器（有则用，没有则回退文件系统）
try:
    from resource_loader import res as _res
    _RES_AVAILABLE = _res.available()
except ImportError:
    _res = None
    _RES_AVAILABLE = False

# 默认音乐的资源前缀（在 resources.dat 里的 key 前缀）
_DEFAULT_MUSIC_PREFIX = "resources/default_music/"


def _is_default_music(path: str) -> bool:
    """判断是否是内置默认音乐（加密包里的）"""
    return path.startswith(_DEFAULT_MUSIC_PREFIX)


def _resolve_path(path: str) -> str:
    """
    把 key 解析成可以播放的实际路径。
    - 用户自己的文件：直接返回原路径
    - 默认音乐（加密包里的）：解密到临时文件后返回临时路径
    """
    if _RES_AVAILABLE and _is_default_music(path):
        return _res.extract_temp(path, suffix=os.path.splitext(path)[1])
    return path


class MusicPlayer(QObject):
    """音乐播放器核心类"""

    song_changed = pyqtSignal(str)
    playback_state_changed = pyqtSignal(bool)
    position_changed = pyqtSignal(int, int)

    def __init__(self):
        super().__init__()

        self.player = QMediaPlayer()

        self.playlist = []          # 路径列表（默认音乐用 key，用户音乐用绝对路径）
        self.watched_folders = []   # ⭐ 用户添加过的文件夹（记住，方便重新扫描）
        self.current_index = -1

        self.is_shuffle = True
        self.is_repeat = True

        self.volume = 50
        self.player.setVolume(self.volume)

        self.player.stateChanged.connect(self._on_state_changed)
        self.player.mediaStatusChanged.connect(self._on_media_status_changed)
        self.player.positionChanged.connect(self._on_position_changed)
        self.player.durationChanged.connect(self._on_duration_changed)

        self.duration = 0

        self.load_playlist()
        print("🎵 音乐播放器已初始化")

    # ============================================================
    # 播放列表持久化
    # ============================================================

    def load_playlist(self):
        """从配置文件加载播放列表"""
        if os.path.exists("music_playlist.json"):
            try:
                with open("music_playlist.json", "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.playlist        = data.get("playlist", [])
                    self.watched_folders = data.get("watched_folders", [])  # ⭐
                    self.volume          = data.get("volume", 50)
                    self.is_shuffle      = data.get("shuffle", True)
                    self.is_repeat       = data.get("repeat", True)
                    self.player.setVolume(self.volume)
                    print(f"✅ 已加载播放列表: {len(self.playlist)} 首歌曲")
            except Exception as e:
                print(f"⚠️ 加载播放列表失败: {e}")
                self.playlist = []

        if not self.playlist:
            self.load_default_music()

    def load_default_music(self):
        """加载内置默认歌单（从加密包或文件系统）"""
        audio_extensions = {'.mp3', '.wav', '.flac', '.m4a', '.ogg', '.wma'}
        file_keys = []

        if _RES_AVAILABLE:
            # 从加密包索引里找 default_music 下的文件
            for key in sorted(_res._index.keys()):
                if key.startswith(_DEFAULT_MUSIC_PREFIX):
                    ext = os.path.splitext(key)[1].lower()
                    if ext in audio_extensions:
                        file_keys.append(key)
            if file_keys:
                print(f"🎵 从加密包加载默认歌单: {len(file_keys)} 首")
        else:
            # 回退：直接扫描文件系统
            default_folder = "resources/default_music"
            if os.path.exists(default_folder):
                for root, _, files in os.walk(default_folder):
                    for file in files:
                        if os.path.splitext(file)[1].lower() in audio_extensions:
                            # 统一用正斜杠 key 格式
                            abs_path = os.path.abspath(os.path.join(root, file))
                            rel_key  = os.path.relpath(abs_path).replace("\\", "/")
                            file_keys.append(rel_key)
                if file_keys:
                    print(f"🎵 从文件系统加载默认歌单: {len(file_keys)} 首")

        if file_keys:
            self.playlist = file_keys
            self.save_playlist()
        else:
            print("ℹ️ 没有找到默认音乐")

    def save_playlist(self):
        """保存播放列表到配置文件"""
        try:
            data = {
                "playlist":       self.playlist,
                "watched_folders": self.watched_folders,   # ⭐
                "volume":         self.volume,
                "shuffle":        self.is_shuffle,
                "repeat":         self.is_repeat
            }
            with open("music_playlist.json", "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"⚠️ 保存播放列表失败: {e}")

    # ============================================================
    # 播放列表管理
    # ============================================================

    def add_songs(self, file_paths):
        """添加单个文件到播放列表"""
        added = 0
        for path in file_paths:
            if os.path.exists(path) and path not in self.playlist:
                self.playlist.append(path)
                added += 1
        if added > 0:
            self.save_playlist()
            print(f"✅ 已添加 {added} 首歌曲")
        return added

    def add_folder(self, folder_path: str) -> int:
        """
        ⭐ 添加文件夹，记住文件夹路径，方便以后重新扫描。
        返回新增歌曲数量。
        """
        folder_path = os.path.abspath(folder_path)
        audio_extensions = {'.mp3', '.wav', '.flac', '.m4a', '.ogg', '.wma'}

        # 记住文件夹
        if folder_path not in self.watched_folders:
            self.watched_folders.append(folder_path)

        # 扫描文件夹里的音频文件
        added = 0
        for root, _, files in os.walk(folder_path):
            for file in files:
                if os.path.splitext(file)[1].lower() in audio_extensions:
                    abs_path = os.path.join(root, file)
                    if abs_path not in self.playlist:
                        self.playlist.append(abs_path)
                        added += 1

        if added > 0:
            self.save_playlist()
            print(f"✅ 文件夹已添加 {added} 首歌曲: {folder_path}")
        return added

    def rescan_watched_folders(self) -> int:
        """
        ⭐ 重新扫描所有已记录的文件夹，把新文件加进来。
        返回新增数量。
        """
        total_added = 0
        for folder in self.watched_folders:
            if os.path.exists(folder):
                added = self.add_folder(folder)
                total_added += added
            else:
                print(f"⚠️ 文件夹已不存在，跳过: {folder}")
        return total_added

    def remove_song(self, index):
        """从播放列表移除歌曲"""
        if 0 <= index < len(self.playlist):
            removed = self.playlist.pop(index)
            if index == self.current_index:
                self.stop()
                self.current_index = -1
            elif index < self.current_index:
                self.current_index -= 1
            self.save_playlist()
            print(f"✅ 已移除: {os.path.basename(removed)}")
            return True
        return False

    def clear_playlist(self):
        """清空播放列表（保留 watched_folders 记录）"""
        self.stop()
        self.playlist.clear()
        self.current_index = -1
        self.save_playlist()
        print("🗑️ 播放列表已清空")

    # ============================================================
    # 播放控制
    # ============================================================

    def play(self, index=None):
        """播放指定索引的歌曲"""
        if not self.playlist:
            print("⚠️ 播放列表为空")
            return False

        if index is not None:
            if 0 <= index < len(self.playlist):
                self.current_index = index
            else:
                return False
        else:
            if self.current_index == -1:
                self.current_index = random.randint(0, len(self.playlist) - 1) \
                    if self.is_shuffle else 0

        path_key = self.playlist[self.current_index]

        # ⭐ 解析路径：默认音乐解密到临时文件，用户文件直接用
        real_path = _resolve_path(path_key)

        if not os.path.exists(real_path):
            print(f"❌ 文件不存在: {path_key}")
            # 只从列表移除用户文件（默认音乐不移除）
            if not _is_default_music(path_key):
                self.remove_song(self.current_index)
            return False

        media = QMediaContent(QUrl.fromLocalFile(real_path))
        self.player.setMedia(media)
        self.player.play()

        song_name = os.path.basename(path_key)
        print(f"🎵 正在播放: {song_name}")
        self.song_changed.emit(song_name)
        return True

    def pause(self):
        if self.player.state() == QMediaPlayer.PlayingState:
            self.player.pause()

    def resume(self):
        if self.player.state() == QMediaPlayer.PausedState:
            self.player.play()

    def stop(self):
        self.player.stop()

    def next_song(self):
        if not self.playlist:
            return False
        self.current_index = random.randint(0, len(self.playlist) - 1) \
            if self.is_shuffle else (self.current_index + 1) % len(self.playlist)
        return self.play(self.current_index)

    def previous_song(self):
        if not self.playlist:
            return False
        self.current_index = random.randint(0, len(self.playlist) - 1) \
            if self.is_shuffle else (self.current_index - 1) % len(self.playlist)
        return self.play(self.current_index)

    def set_volume(self, volume):
        self.volume = max(0, min(100, volume))
        self.player.setVolume(self.volume)
        self.save_playlist()

    def toggle_shuffle(self):
        self.is_shuffle = not self.is_shuffle
        self.save_playlist()
        return self.is_shuffle

    def toggle_repeat(self):
        self.is_repeat = not self.is_repeat
        self.save_playlist()
        return self.is_repeat

    def is_playing(self):
        return self.player.state() == QMediaPlayer.PlayingState

    def get_current_song(self):
        if 0 <= self.current_index < len(self.playlist):
            return os.path.basename(self.playlist[self.current_index])
        return None

    def get_playlist_info(self):
        return {
            "total":    len(self.playlist),
            "current":  self.current_index,
            "shuffle":  self.is_shuffle,
            "repeat":   self.is_repeat,
            "volume":   self.volume,
            "watched_folders": self.watched_folders   # ⭐
        }

    # ============================================================
    # 内部信号处理
    # ============================================================

    def _on_state_changed(self, state):
        self.playback_state_changed.emit(state == QMediaPlayer.PlayingState)

    def _on_media_status_changed(self, status):
        if status == QMediaPlayer.EndOfMedia:
            self.next_song() if self.is_repeat else self.stop()

    def _on_position_changed(self, position):
        if self.duration > 0:
            self.position_changed.emit(position, self.duration)

    def _on_duration_changed(self, duration):
        self.duration = duration