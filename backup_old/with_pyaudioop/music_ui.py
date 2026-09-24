"""
音乐播放器UI - 控制面板和播放列表管理（支持音量归一化）
"""
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QSlider, QListWidget, QListWidgetItem, QFileDialog, QMessageBox,
    QProgressDialog
)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont
import os


class MusicPlayerDialog(QDialog):
    """音乐播放器主界面"""

    def __init__(self, music_player, parent=None):
        super().__init__(parent)
        self.music_player = music_player

        self.setWindowTitle("🎵 音乐播放器")
        self.setMinimumSize(500, 650)

        # 创建UI
        self.init_ui()

        # 连接信号
        self.music_player.song_changed.connect(self.on_song_changed)
        self.music_player.playback_state_changed.connect(self.on_playback_state_changed)
        self.music_player.position_changed.connect(self.on_position_changed)

        # 更新UI
        self.update_ui()

    def init_ui(self):
        """初始化UI"""
        layout = QVBoxLayout()

        # ========== 当前播放信息 ==========
        info_layout = QVBoxLayout()

        self.current_song_label = QLabel("暂无播放")
        self.current_song_label.setAlignment(Qt.AlignCenter)
        self.current_song_label.setFont(QFont("Arial", 12, QFont.Bold))
        self.current_song_label.setStyleSheet("color: #2196F3; padding: 10px;")
        info_layout.addWidget(self.current_song_label)

        self.time_label = QLabel("00:00 / 00:00")
        self.time_label.setAlignment(Qt.AlignCenter)
        self.time_label.setStyleSheet("color: #666;")
        info_layout.addWidget(self.time_label)

        layout.addLayout(info_layout)

        # ========== 进度条 ==========
        self.progress_slider = QSlider(Qt.Horizontal)
        self.progress_slider.setRange(0, 1000)
        self.progress_slider.setValue(0)
        self.progress_slider.sliderPressed.connect(self.on_slider_pressed)
        self.progress_slider.sliderReleased.connect(self.on_slider_released)
        layout.addWidget(self.progress_slider)

        # ========== 播放控制按钮 ==========
        control_layout = QHBoxLayout()

        self.prev_btn = QPushButton("⏮️ 上一首")
        self.prev_btn.clicked.connect(self.on_previous)
        control_layout.addWidget(self.prev_btn)

        self.play_pause_btn = QPushButton("▶️ 播放")
        self.play_pause_btn.clicked.connect(self.on_play_pause)
        self.play_pause_btn.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                font-weight: bold;
                padding: 10px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
        """)
        control_layout.addWidget(self.play_pause_btn)

        self.next_btn = QPushButton("⏭️ 下一首")
        self.next_btn.clicked.connect(self.on_next)
        control_layout.addWidget(self.next_btn)

        layout.addLayout(control_layout)

        # ========== 音量控制 ==========
        volume_layout = QHBoxLayout()

        volume_label = QLabel("🔊 音量:")
        volume_layout.addWidget(volume_label)

        self.volume_slider = QSlider(Qt.Horizontal)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(self.music_player.base_volume)
        self.volume_slider.valueChanged.connect(self.on_volume_changed)
        volume_layout.addWidget(self.volume_slider)

        self.volume_value_label = QLabel(f"{self.music_player.base_volume}%")
        self.volume_value_label.setMinimumWidth(40)
        volume_layout.addWidget(self.volume_value_label)

        layout.addLayout(volume_layout)

        # ========== 播放模式切换 ==========
        mode_layout = QHBoxLayout()

        self.shuffle_btn = QPushButton("🔀 随机播放")
        self.shuffle_btn.setCheckable(True)
        self.shuffle_btn.setChecked(self.music_player.is_shuffle)
        self.shuffle_btn.clicked.connect(self.on_toggle_shuffle)
        mode_layout.addWidget(self.shuffle_btn)

        self.repeat_btn = QPushButton("🔁 循环播放")
        self.repeat_btn.setCheckable(True)
        self.repeat_btn.setChecked(self.music_player.is_repeat)
        self.repeat_btn.clicked.connect(self.on_toggle_repeat)
        mode_layout.addWidget(self.repeat_btn)

        layout.addLayout(mode_layout)

        # ========== ⭐ 音量归一化开关 ==========
        normalize_layout = QHBoxLayout()

        self.normalize_btn = QPushButton("🎚️ 音量均衡")
        self.normalize_btn.setCheckable(True)
        self.normalize_btn.setChecked(self.music_player.volume_normalize_enabled)
        self.normalize_btn.clicked.connect(self.on_toggle_normalize)
        normalize_layout.addWidget(self.normalize_btn)

        self.analyze_btn = QPushButton("📊 分析全部音量")
        self.analyze_btn.clicked.connect(self.on_analyze_volumes)
        normalize_layout.addWidget(self.analyze_btn)

        layout.addLayout(normalize_layout)

        # ========== 播放列表 ==========
        playlist_label = QLabel(f"📜 播放列表 ({len(self.music_player.playlist)} 首)")
        playlist_label.setFont(QFont("Arial", 10, QFont.Bold))
        layout.addWidget(playlist_label)

        self.playlist_widget = QListWidget()
        self.playlist_widget.itemDoubleClicked.connect(self.on_playlist_item_double_clicked)
        layout.addWidget(self.playlist_widget)

        # ========== 播放列表管理按钮 ==========
        playlist_control_layout = QHBoxLayout()

        add_btn = QPushButton("➕ 添加歌曲")
        add_btn.clicked.connect(self.on_add_songs)
        playlist_control_layout.addWidget(add_btn)

        add_folder_btn = QPushButton("📁 添加文件夹")
        add_folder_btn.clicked.connect(self.on_add_folder)
        playlist_control_layout.addWidget(add_folder_btn)

        remove_btn = QPushButton("➖ 移除选中")
        remove_btn.clicked.connect(self.on_remove_song)
        playlist_control_layout.addWidget(remove_btn)

        clear_btn = QPushButton("🗑️ 清空列表")
        clear_btn.clicked.connect(self.on_clear_playlist)
        playlist_control_layout.addWidget(clear_btn)

        layout.addLayout(playlist_control_layout)

        self.setLayout(layout)

        # 更新播放列表显示
        self.update_playlist_display()

    def update_ui(self):
        """更新UI状态"""
        # 更新当前歌曲显示
        current_song = self.music_player.get_current_song()
        if current_song:
            self.current_song_label.setText(f"♫ {current_song}")
        else:
            self.current_song_label.setText("暂无播放")

        # 更新播放/暂停按钮
        if self.music_player.is_playing():
            self.play_pause_btn.setText("⏸️ 暂停")
        else:
            self.play_pause_btn.setText("▶️ 播放")

        # 更新模式按钮
        self.shuffle_btn.setChecked(self.music_player.is_shuffle)
        self.repeat_btn.setChecked(self.music_player.is_repeat)
        self.normalize_btn.setChecked(self.music_player.volume_normalize_enabled)

    def update_playlist_display(self):
        """更新播放列表显示"""
        self.playlist_widget.clear()

        for i, file_path in enumerate(self.music_player.playlist):
            song_name = os.path.basename(file_path)

            # 标记当前播放的歌曲
            if i == self.music_player.current_index:
                item_text = f"🎵 {song_name}"
            else:
                item_text = f"   {song_name}"

            item = QListWidgetItem(item_text)
            self.playlist_widget.addItem(item)

    # ========== 事件处理 ==========

    def on_play_pause(self):
        """播放/暂停按钮"""
        if self.music_player.is_playing():
            self.music_player.pause()
        else:
            if self.music_player.player.state() == self.music_player.player.PausedState:
                self.music_player.resume()
            else:
                self.music_player.play()

    def on_previous(self):
        """上一首"""
        self.music_player.previous_song()

    def on_next(self):
        """下一首"""
        self.music_player.next_song()

    def on_volume_changed(self, value):
        """音量改变"""
        self.music_player.set_volume(value)
        self.volume_value_label.setText(f"{value}%")

    def on_toggle_shuffle(self):
        """切换随机播放"""
        is_shuffle = self.music_player.toggle_shuffle()
        self.shuffle_btn.setChecked(is_shuffle)

    def on_toggle_repeat(self):
        """切换循环播放"""
        is_repeat = self.music_player.toggle_repeat()
        self.repeat_btn.setChecked(is_repeat)

    def on_toggle_normalize(self):
        """⭐ 切换音量归一化"""
        is_normalize = self.music_player.toggle_normalize()
        self.normalize_btn.setChecked(is_normalize)

        if is_normalize:
            QMessageBox.information(
                self,
                "音量均衡已开启",
                "音量均衡功能会自动调整每首歌的音量，使其保持一致。\n\n"
                "建议点击'分析全部音量'按钮预先分析所有歌曲，\n"
                "这样切换歌曲时会更流畅。"
            )

    def on_analyze_volumes(self):
        """⭐ 分析所有歌曲音量"""
        if not self.music_player.playlist:
            QMessageBox.warning(self, "提示", "播放列表为空")
            return

        # 检查是否安装了必要的库
        try:
            from audio_normalizer import HAS_PYDUB
            if not HAS_PYDUB:
                QMessageBox.warning(
                    self,
                    "功能不可用",
                    "音量分析功能需要安装 pydub 库。\n\n"
                    "安装方法：\n"
                    "1. pip install pydub\n"
                    "2. 安装 ffmpeg: https://ffmpeg.org/download.html"
                )
                return
        except:
            QMessageBox.warning(self, "错误", "无法加载音量归一化模块")
            return

        # 创建进度对话框
        progress = QProgressDialog("正在分析音量...", "取消", 0, len(self.music_player.playlist), self)
        progress.setWindowTitle("分析音量")
        progress.setWindowModality(Qt.WindowModal)
        progress.setMinimumDuration(0)

        def update_progress(current, total):
            progress.setValue(current)
            if progress.wasCanceled():
                return False
            return True

        # 执行分析
        self.music_player.analyze_all_volumes(update_progress)

        progress.setValue(len(self.music_player.playlist))
        QMessageBox.information(
            self,
            "分析完成",
            f"已完成 {len(self.music_player.playlist)} 首歌曲的音量分析。\n\n"
            "音量数据已缓存，下次播放时会自动应用。"
        )

    def on_add_songs(self):
        """添加歌曲"""
        file_paths, _ = QFileDialog.getOpenFileNames(
            self,
            "选择音乐文件",
            "",
            "音频文件 (*.mp3 *.wav *.flac *.m4a *.ogg *.wma);;所有文件 (*)"
        )

        if file_paths:
            added = self.music_player.add_songs(file_paths)
            self.update_playlist_display()
            QMessageBox.information(self, "添加成功", f"已添加 {added} 首歌曲")

    def on_add_folder(self):
        """添加文件夹"""
        folder_path = QFileDialog.getExistingDirectory(self, "选择音乐文件夹")

        if folder_path:
            # 支持的音频格式
            audio_extensions = ['.mp3', '.wav', '.flac', '.m4a', '.ogg', '.wma']

            # 扫描文件夹
            file_paths = []
            for root, dirs, files in os.walk(folder_path):
                for file in files:
                    if os.path.splitext(file)[1].lower() in audio_extensions:
                        file_paths.append(os.path.join(root, file))

            if file_paths:
                added = self.music_player.add_songs(file_paths)
                self.update_playlist_display()
                QMessageBox.information(self, "添加成功", f"已从文件夹添加 {added} 首歌曲")
            else:
                QMessageBox.warning(self, "未找到音乐", "该文件夹中没有找到支持的音频文件")

    def on_remove_song(self):
        """移除选中的歌曲"""
        current_row = self.playlist_widget.currentRow()

        if current_row >= 0:
            reply = QMessageBox.question(
                self,
                "确认移除",
                "确定要移除这首歌曲吗？",
                QMessageBox.Yes | QMessageBox.No
            )

            if reply == QMessageBox.Yes:
                self.music_player.remove_song(current_row)
                self.update_playlist_display()

    def on_clear_playlist(self):
        """清空播放列表"""
        if not self.music_player.playlist:
            return

        reply = QMessageBox.question(
            self,
            "确认清空",
            "确定要清空播放列表吗？",
            QMessageBox.Yes | QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            self.music_player.clear_playlist()
            self.update_playlist_display()
            self.update_ui()

    def on_playlist_item_double_clicked(self, item):
        """双击播放列表项"""
        index = self.playlist_widget.row(item)
        self.music_player.play(index)

    def on_slider_pressed(self):
        """进度条按下"""
        self.slider_pressed = True

    def on_slider_released(self):
        """进度条释放"""
        self.slider_pressed = False
        # 跳转到指定位置
        if self.music_player.duration > 0:
            position = int(self.progress_slider.value() / 1000 * self.music_player.duration)
            self.music_player.player.setPosition(position)

    # ========== 信号槽 ==========

    def on_song_changed(self, song_name):
        """歌曲切换"""
        self.current_song_label.setText(f"♫ {song_name}")
        self.update_playlist_display()

    def on_playback_state_changed(self, is_playing):
        """播放状态改变"""
        if is_playing:
            self.play_pause_btn.setText("⏸️ 暂停")
        else:
            self.play_pause_btn.setText("▶️ 播放")

    def on_position_changed(self, position, duration):
        """进度更新"""
        if duration > 0 and not hasattr(self, 'slider_pressed') or not self.slider_pressed:
            # 更新进度条
            progress = int(position / duration * 1000)
            self.progress_slider.setValue(progress)

            # 更新时间显示
            current_time = self.format_time(position)
            total_time = self.format_time(duration)
            self.time_label.setText(f"{current_time} / {total_time}")

    @staticmethod
    def format_time(ms):
        """格式化时间 (毫秒 -> MM:SS)"""
        seconds = ms // 1000
        minutes = seconds // 60
        seconds = seconds % 60
        return f"{minutes:02d}:{seconds:02d}"