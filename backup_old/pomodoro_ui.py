"""
番茄钟用户界面模块（修改版 - 加深休息时字体颜色）
文件名: pomodoro_ui_fixed.py
位置: 项目根目录
"""

from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QSpinBox, QCheckBox
)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont


class PomodoroSetupDialog(QDialog):
    """番茄钟设置对话框"""

    def __init__(self, parent=None):
        """初始化设置界面"""
        super().__init__(parent)

        self.setWindowTitle("🍅 番茄钟设置")
        self.setMinimumWidth(350)

        layout = QVBoxLayout(self)

        # 标题
        title = QLabel("番茄钟设置")
        title.setFont(QFont("Microsoft YaHei", 14, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        layout.addSpacing(10)

        # 工作时长
        work_layout = QHBoxLayout()
        work_layout.addWidget(QLabel("工作时长:"))
        self.work_spin = QSpinBox()
        self.work_spin.setRange(1, 120)
        self.work_spin.setValue(25)
        self.work_spin.setSuffix(" 分钟")
        work_layout.addWidget(self.work_spin)
        work_layout.addStretch()
        layout.addLayout(work_layout)

        # 休息时长
        break_layout = QHBoxLayout()
        break_layout.addWidget(QLabel("休息时长:"))
        self.break_spin = QSpinBox()
        self.break_spin.setRange(1, 60)
        self.break_spin.setValue(5)
        self.break_spin.setSuffix(" 分钟")
        break_layout.addWidget(self.break_spin)
        break_layout.addStretch()
        layout.addLayout(break_layout)

        # 轮数
        round_layout = QHBoxLayout()
        round_layout.addWidget(QLabel("轮数:"))
        self.round_spin = QSpinBox()
        self.round_spin.setRange(1, 10)
        self.round_spin.setValue(1)
        self.round_spin.setSuffix(" 轮")
        round_layout.addWidget(self.round_spin)
        round_layout.addStretch()
        layout.addLayout(round_layout)

        # 是否重复
        self.repeat_check = QCheckBox("完成后自动重复")
        layout.addWidget(self.repeat_check)

        layout.addSpacing(10)

        # 提示
        hint = QLabel("💡 每轮工作后会自动休息\n完成所有轮次后停止（除非勾选重复）")
        hint.setStyleSheet("color: gray; font-size: 10px;")
        hint.setAlignment(Qt.AlignCenter)
        layout.addWidget(hint)

        layout.addSpacing(10)

        # 按钮
        btn_layout = QHBoxLayout()

        btn_start = QPushButton("🍅 开始番茄钟")
        btn_start.setFont(QFont("Microsoft YaHei", 10))
        btn_start.setStyleSheet("""
            QPushButton {
                background-color: #FF6347;
                color: white;
                padding: 8px;
                border-radius: 5px;
                border: none;
            }
            QPushButton:hover {
                background-color: #FF4500;
            }
        """)
        btn_start.clicked.connect(self.accept)

        btn_cancel = QPushButton("取消")
        btn_cancel.clicked.connect(self.reject)

        btn_layout.addWidget(btn_start)
        btn_layout.addWidget(btn_cancel)

        layout.addLayout(btn_layout)

    def get_settings(self):
        """
        获取用户设置

        Returns:
            dict: {"work_minutes", "break_minutes", "rounds", "is_repeat"}
        """
        return {
            "work_minutes": self.work_spin.value(),
            "break_minutes": self.break_spin.value(),
            "rounds": self.round_spin.value(),
            "is_repeat": self.repeat_check.isChecked()
        }


class PomodoroDisplay:
    """番茄钟倒计时显示（独立窗口）"""

    def __init__(self, pet_instance):
        """
        初始化显示组件

        Args:
            pet_instance: 宠物主窗口实例
        """
        self.pet = pet_instance

        # ⭐ 创建窗口（
        self.display_label = QLabel(pet_instance)

        # ⭐ 设置为独立的置顶窗口
        self.display_label.setWindowFlags(
            Qt.FramelessWindowHint |
            Qt.WindowStaysOnTopHint |
            Qt.Tool
        )
        # ⭐ 不设置透明背景，使用普通背景
        # self.display_label.setAttribute(Qt.WA_TranslucentBackground)  # 删除这行

        # ⭐ 设置对齐方式：水平和垂直都居中
        self.display_label.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)

        # ⭐ 允许自动换行
        self.display_label.setWordWrap(True)
        self.display_label.setStyleSheet("""
            QLabel {
                background-color: #F5F5DC;
                color: #5D4037;
                border: 2px solid #D2B48C;
                border-radius: 8px;
                padding: 18px;
                font-weight: bold;
            }
        """)

        # ⭐ 缩小字体
        self.display_label.setFont(QFont("Arial", 10))

        # ⭐ 再次增大尺寸，确保文字完整显示
        self.display_label.setFixedSize(240, 80)

        # ⭐ 设置行间距
        self.display_label.setTextFormat(Qt.PlainText)  # 使用纯文本格式

        # ⭐ 设置边距，避免文字贴边
        self.display_label.setContentsMargins(5, 5, 5, 5)

        # 默认隐藏
        self.display_label.hide()

        # 状态
        self.is_visible = False
        self.work_minutes = 25
        self.break_minutes = 5
        self.total_rounds = 1
        self.current_round = 1

        # ⭐ 不使用定时器，改为直接跟随宠物的 move 事件
        # 删除定时器相关代码

    def show_timer(self, work_minutes, break_minutes, rounds):
        """
        显示番茄钟（初始化）

        Args:
            work_minutes: 工作时长
            break_minutes: 休息时长
            rounds: 总轮数
        """
        self.work_minutes = work_minutes
        self.break_minutes = break_minutes
        self.total_rounds = rounds
        self.current_round = 1

        # ⭐ 先更新位置，再显示（避免在屏幕中央闪现）
        self.update_position()

        # 显示窗口
        self.display_label.show()
        self.is_visible = True

        print(f"📊 番茄钟显示已开启（独立窗口）")

    def update_countdown(self, remaining_seconds, is_break, current_round=None):
        """
        更新倒计时显示

        Args:
            remaining_seconds: 剩余秒数
            is_break: 是否休息中
            current_round: 当前轮数（可选）
        """
        if current_round is not None:
            self.current_round = current_round

        # 计算时分秒
        hours = remaining_seconds // 3600
        minutes = (remaining_seconds % 3600) // 60
        seconds = remaining_seconds % 60

        # 格式化时间字符串
        if hours > 0:
            time_str = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        else:
            time_str = f"{minutes:02d}:{seconds:02d}"

        # ⭐ 状态文字 - 倒计时前显示"工作"/"休息"
        if is_break:
            prefix = "休息"
            color = "#2E7D32"  # ⭐ 改为深绿色（加深）
        else:
            prefix = "工作"
            color = "#228B22"  # 深绿色

        # ⭐ 组合文本：第一行轮数，第二行倒计时
        text = f"{self.current_round}/{self.total_rounds}轮\n{prefix}: {time_str}"
        self.display_label.setText(text)

        # ⭐ 根据状态改变倒计时颜色（休息时字体加深）
        if is_break:
            self.display_label.setStyleSheet("""
                QLabel {
                    background-color: #F5F5DC;
                    color: #2E7D32;
                    border: 2px solid #D2B48C;
                    border-radius: 8px;
                    padding: 18px;
                    font-weight: bold;
                }
            """)
        else:
            self.display_label.setStyleSheet("""
                QLabel {
                    background-color: #F5F5DC;
                    color: #228B22;
                    border: 2px solid #D2B48C;
                    border-radius: 8px;
                    padding: 18px;
                    font-weight: bold;
                }
            """)

    def show_completion(self):
        """显示完成消息"""
        self.display_label.setText("🎉 番茄钟完成！")
        self.display_label.setStyleSheet("""
            QLabel {
                background-color: #F5F5DC;
                color: #5D4037;
                border: 2px solid #D2B48C;
                border-radius: 8px;
                padding: 18px;
                font-weight: bold;
            }
        """)
        print("🎊 番茄钟完成显示")

    def hide(self):
        """隐藏番茄钟显示"""
        self.display_label.hide()
        self.is_visible = False
        print("📊 番茄钟显示已隐藏")

    def update_position(self):
        """⭐ 更新显示位置（跟随宠物）"""
        # ⭐ 即使未显示也要计算位置（避免首次显示时在屏幕中央）

        # 获取宠物的全局位置
        pet_global_pos = self.pet.pos()
        pet_x = pet_global_pos.x()
        pet_y = pet_global_pos.y()
        pet_width = self.pet.pet_width

        # 计算番茄钟窗口位置
        # 水平：居中对齐
        display_width = 240  # ⭐ 更新宽度
        display_x = pet_x + (pet_width - display_width) // 2

        # 垂直：在宠物上方
        display_y = pet_y - 90  # ⭐ 增加距离

        # 移动独立窗口
        self.display_label.move(display_x, display_y)