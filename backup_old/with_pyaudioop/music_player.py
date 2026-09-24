"""
音乐播放器模块 - 支持随机播放、列表管理、音量控制、音量归一化
"""
import os
import random
import json
from PyQt5.QtCore import QUrl, QTimer, pyqtSignal, QObject
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent

# 导入音量归一化工具
try:
    from audio_normalizer import audio_normalizer
    HAS_NORMALIZER = True
except ImportError:
    HAS_NORMALIZER = False
    print("⚠️ 音量归一化功能不可用")


class MusicPlayer(QObject):
    """音乐播放器核心类"""

    # 信号
    song_changed = pyqtSignal(str)  # 歌曲切换信号 (歌曲名)
    playback_state_changed = pyqtSignal(bool)  # 播放状态变化 (是否正在播放)
    position_changed = pyqtSignal(int, int)  # 进度变化 (当前位置, 总时长)

    def __init__(self):
        super().__init__()

        # 媒体播放器
        self.player = QMediaPlayer()

        # 播放列表
        self.playlist = []  # 存储音乐文件路径
        self.current_index = -1

        # 播放模式
        self.is_shuffle = True  # 默认随机播放
        self.is_repeat = True   # 默认循环播放

        # 音量 (0-100)
        self.volume = 50
        self.base_volume = 50  # 基础音量
        self.player.setVolume(self.volume)

        # ⭐ 音量归一化开关
        self.volume_normalize_enabled = True

        # 连接信号
        self.player.stateChanged.connect(self._on_state_changed)
        self.player.mediaStatusChanged.connect(self._on_media_status_changed)
        self.player.positionChanged.connect(self._on_position_changed)
        self.player.durationChanged.connect(self._on_duration_changed)

        # 当前时长
        self.duration = 0

        # 加载播放列表
        self.load_playlist()

        print("🎵 音乐播放器已初始化")

    def load_playlist(self):
        """从配置文件加载播放列表"""
        if os.path.exists("music_playlist.json"):
            try:
                with open("music_playlist.json", "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.playlist = data.get("playlist", [])
                    self.volume = data.get("volume", 50)
                    self.base_volume = self.volume
                    self.is_shuffle = data.get("shuffle", True)
                    self.is_repeat = data.get("repeat", True)
                    self.volume_normalize_enabled = data.get("normalize", True)
                    self.player.setVolume(self.volume)
                    print(f"✅ 已加载播放列表: {len(self.playlist)} 首歌曲")
            except Exception as e:
                print(f"⚠️ 加载播放列表失败: {e}")
                self.playlist = []

        # ⭐ 新增：如果播放列表为空，加载默认歌单
        if not self.playlist:
            self.load_default_music()

    def load_default_music(self):
        """加载默认歌单（default_music 文件夹）"""
        default_folder = "default_music"

        if not os.path.exists(default_folder):
            print(f"ℹ️ 默认音乐文件夹不存在: {default_folder}")
            return

        # 支持的音频格式
        audio_extensions = ['.mp3', '.wav', '.flac', '.m4a', '.ogg', '.wma']

        # 扫描 default_music 文件夹
        file_paths = []
        try:
            for root, dirs, files in os.walk(default_folder):
                for file in files:
                    if os.path.splitext(file)[1].lower() in audio_extensions:
                        file_paths.append(os.path.abspath(os.path.join(root, file)))

            if file_paths:
                self.playlist = file_paths
                self.save_playlist()
                print(f"🎵 已加载默认歌单: {len(file_paths)} 首歌曲")
            else:
                print(f"ℹ️ 默认音乐文件夹为空")
        except Exception as e:
            print(f"⚠️ 加载默认歌单失败: {e}")

    def save_playlist(self):
        """保存播放列表到配置文件"""
        try:
            data = {
                "playlist": self.playlist,
                "volume": self.base_volume,
                "shuffle": self.is_shuffle,
                "repeat": self.is_repeat,
                "normalize": self.volume_normalize_enabled
            }
            with open("music_playlist.json", "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            print("✅ 播放列表已保存")
        except Exception as e:
            print(f"⚠️ 保存播放列表失败: {e}")

    def add_songs(self, file_paths):
        """添加歌曲到播放列表"""
        added = 0
        for path in file_paths:
            if os.path.exists(path) and path not in self.playlist:
                self.playlist.append(path)
                added += 1

        if added > 0:
            self.save_playlist()
            print(f"✅ 已添加 {added} 首歌曲")
        return added

    def remove_song(self, index):
        """从播放列表移除歌曲"""
        if 0 <= index < len(self.playlist):
            removed = self.playlist.pop(index)

            # 如果移除的是当前播放的歌曲
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
        """清空播放列表"""
        self.stop()
        self.playlist.clear()
        self.current_index = -1
        self.save_playlist()
        print("🗑️ 播放列表已清空")

    def play(self, index=None):
        """播放指定索引的歌曲，如果不指定则播放下一首"""
        if not self.playlist:
            print("⚠️ 播放列表为空")
            return False

        # 如果指定了索引
        if index is not None:
            if 0 <= index < len(self.playlist):
                self.current_index = index
            else:
                return False
        else:
            # 如果当前没有播放歌曲，选择第一首或随机一首
            if self.current_index == -1:
                if self.is_shuffle:
                    self.current_index = random.randint(0, len(self.playlist) - 1)
                else:
                    self.current_index = 0

        # 播放当前歌曲
        file_path = self.playlist[self.current_index]

        if not os.path.exists(file_path):
            print(f"❌ 文件不存在: {file_path}")
            self.remove_song(self.current_index)
            return False

        media = QMediaContent(QUrl.fromLocalFile(file_path))
        self.player.setMedia(media)

        # ⭐ 应用音量归一化
        self._apply_normalized_volume(file_path)

        self.player.play()

        song_name = os.path.basename(file_path)
        print(f"🎵 正在播放: {song_name}")
        self.song_changed.emit(song_name)

        return True

    def _apply_normalized_volume(self, file_path):
        """应用音量归一化"""
        if self.volume_normalize_enabled and HAS_NORMALIZER:
            try:
                # 获取该文件的音量倍数
                multiplier = audio_normalizer.get_volume_multiplier(file_path)

                # 应用倍数到当前音量
                adjusted_volume = int(self.base_volume * multiplier)
                adjusted_volume = max(0, min(100, adjusted_volume))

                self.player.setVolume(adjusted_volume)

                if multiplier != 1.0:
                    print(f"🔊 音量调整: {self.base_volume}% × {multiplier:.2f} = {adjusted_volume}%")
            except Exception as e:
                print(f"⚠️ 音量归一化失败: {e}")
                self.player.setVolume(self.base_volume)
        else:
            self.player.setVolume(self.base_volume)

    def pause(self):
        """暂停播放"""
        if self.player.state() == QMediaPlayer.PlayingState:
            self.player.pause()
            print("⏸️ 已暂停")

    def resume(self):
        """继续播放"""
        if self.player.state() == QMediaPlayer.PausedState:
            self.player.play()
            print("▶️ 继续播放")

    def stop(self):
        """停止播放"""
        self.player.stop()
        print("⏹️ 已停止")

    def next_song(self):
        """下一首"""
        if not self.playlist:
            return False

        if self.is_shuffle:
            # 随机播放
            self.current_index = random.randint(0, len(self.playlist) - 1)
        else:
            # 顺序播放
            self.current_index = (self.current_index + 1) % len(self.playlist)

        return self.play(self.current_index)

    def previous_song(self):
        """上一首"""
        if not self.playlist:
            return False

        if self.is_shuffle:
            # 随机播放
            self.current_index = random.randint(0, len(self.playlist) - 1)
        else:
            # 顺序播放
            self.current_index = (self.current_index - 1) % len(self.playlist)

        return self.play(self.current_index)

    def set_volume(self, volume):
        """设置基础音量 (0-100)"""
        self.base_volume = max(0, min(100, volume))
        self.volume = self.base_volume

        # 如果正在播放，重新应用音量归一化
        if 0 <= self.current_index < len(self.playlist):
            file_path = self.playlist[self.current_index]
            self._apply_normalized_volume(file_path)
        else:
            self.player.setVolume(self.base_volume)

        self.save_playlist()
        print(f"🔊 基础音量: {self.base_volume}%")

    def toggle_shuffle(self):
        """切换随机播放模式"""
        self.is_shuffle = not self.is_shuffle
        self.save_playlist()
        print(f"🔀 随机播放: {'开' if self.is_shuffle else '关'}")
        return self.is_shuffle

    def toggle_repeat(self):
        """切换循环播放模式"""
        self.is_repeat = not self.is_repeat
        self.save_playlist()
        print(f"🔁 循环播放: {'开' if self.is_repeat else '关'}")
        return self.is_repeat

    def toggle_normalize(self):
        """⭐ 切换音量归一化"""
        self.volume_normalize_enabled = not self.volume_normalize_enabled
        self.save_playlist()

        # 如果正在播放，立即应用新设置
        if 0 <= self.current_index < len(self.playlist):
            file_path = self.playlist[self.current_index]
            self._apply_normalized_volume(file_path)

        print(f"🎚️ 音量归一化: {'开' if self.volume_normalize_enabled else '关'}")
        return self.volume_normalize_enabled

    def analyze_all_volumes(self, progress_callback=None):
        """⭐ 分析所有歌曲的音量（后台任务）"""
        if HAS_NORMALIZER:
            audio_normalizer.batch_analyze(self.playlist, progress_callback)
        else:
            print("⚠️ 音量归一化功能不可用，请安装 pydub")

    def is_playing(self):
        """是否正在播放"""
        return self.player.state() == QMediaPlayer.PlayingState

    def get_current_song(self):
        """获取当前播放的歌曲名"""
        if 0 <= self.current_index < len(self.playlist):
            return os.path.basename(self.playlist[self.current_index])
        return None

    def get_playlist_info(self):
        """获取播放列表信息"""
        return {
            "total": len(self.playlist),
            "current": self.current_index,
            "shuffle": self.is_shuffle,
            "repeat": self.is_repeat,
            "volume": self.base_volume,
            "normalize": self.volume_normalize_enabled
        }

    # ============ 内部信号处理 ============

    def _on_state_changed(self, state):
        """播放状态变化"""
        is_playing = (state == QMediaPlayer.PlayingState)
        self.playback_state_changed.emit(is_playing)

    def _on_media_status_changed(self, status):
        """媒体状态变化"""
        # 当前歌曲播放结束
        if status == QMediaPlayer.EndOfMedia:
            if self.is_repeat:
                # 循环模式：播放下一首
                self.next_song()
            else:
                # 非循环模式：停止
                self.stop()

    def _on_position_changed(self, position):
        """播放进度变化"""
        if self.duration > 0:
            self.position_changed.emit(position, self.duration)

    def _on_duration_changed(self, duration):
        """时长变化"""
        self.duration = duration