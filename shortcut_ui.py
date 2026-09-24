from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont


class ShortcutRecorder(QDialog):
    """录制按键的专用小窗口 - 优化字体版"""
    key_recorded = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("录制中...")
        self.setFixedSize(320, 150)
        self.setWindowFlags(Qt.Dialog | Qt.WindowStaysOnTopHint)

        layout = QVBoxLayout(self)

        self.label = QLabel("请按下组合键...\n\n支持：Ctrl/Shift/Alt + 字母/数字", self)
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setFont(QFont("Microsoft YaHei", 11))  # 增大字体
        self.label.setStyleSheet("padding: 10px;")
        layout.addWidget(self.label)

        self.info_label = QLabel("", self)
        self.info_label.setAlignment(Qt.AlignCenter)
        self.info_label.setFont(QFont("Microsoft YaHei", 12, QFont.Bold))  # 加粗显示
        self.info_label.setStyleSheet("color: #2196F3; padding: 5px;")
        layout.addWidget(self.info_label)

    def keyPressEvent(self, event):
        """改进的按键捕捉逻辑"""
        # 忽略单独的修饰键
        if event.key() in [Qt.Key_Control, Qt.Key_Shift, Qt.Key_Alt,
                           Qt.Key_Meta, Qt.Key_Super_L, Qt.Key_Super_R]:
            return

        modifiers = event.modifiers()
        keys = []

        # 添加修饰键
        if modifiers & Qt.ControlModifier:
            keys.append("ctrl")
        if modifiers & Qt.ShiftModifier:
            keys.append("shift")
        if modifiers & Qt.AltModifier:
            keys.append("alt")

        # 必须至少有一个修饰键
        if not keys:
            self.label.setText("⚠️ 请配合 Ctrl/Shift/Alt 使用\n\n示例：Ctrl+Shift+A")
            return

        # 获取主按键
        key_text = self._get_key_text(event)

        if not key_text:
            self.label.setText("⚠️ 不支持的按键\n\n请使用字母、数字或空格键")
            return

        keys.append(key_text)
        hotkey = "+".join(keys)

        # 显示录制的快捷键
        self.info_label.setText(f"已录制: {hotkey}")

        # 延迟发送信号，让用户看到结果
        from PyQt5.QtCore import QTimer
        QTimer.singleShot(500, lambda: self._emit_and_close(hotkey))

    def _get_key_text(self, event):
        """获取按键文本 - 改进版"""
        key = event.key()

        # 字母键 (A-Z)
        if Qt.Key_A <= key <= Qt.Key_Z:
            return chr(key).lower()

        # 数字键 (0-9)
        if Qt.Key_0 <= key <= Qt.Key_9:
            return chr(key)

        # 功能键 (F1-F12)
        if Qt.Key_F1 <= key <= Qt.Key_F12:
            return f"f{key - Qt.Key_F1 + 1}"

        # 特殊键
        special_keys = {
            Qt.Key_Space: "space",
            Qt.Key_Tab: "tab",
            Qt.Key_Return: "enter",
            Qt.Key_Enter: "enter",
            Qt.Key_Backspace: "backspace",
            Qt.Key_Delete: "delete",
            Qt.Key_Escape: "esc",
            Qt.Key_Plus: "plus",
            Qt.Key_Minus: "minus",
            Qt.Key_Equal: "equal",
            Qt.Key_BracketLeft: "[",
            Qt.Key_BracketRight: "]",
            Qt.Key_Semicolon: ";",
            Qt.Key_Apostrophe: "'",
            Qt.Key_Comma: ",",
            Qt.Key_Period: ".",
            Qt.Key_Slash: "/",
            Qt.Key_Backslash: "\\",
        }

        if key in special_keys:
            return special_keys[key]

        # 尝试使用 text()（作为备用）
        text = event.text().lower()
        if text and text.isprintable() and text not in ['\r', '\n', '\t', ' ']:
            return text

        return None

    def _emit_and_close(self, hotkey):
        """发送信号并关闭"""
        self.key_recorded.emit(hotkey)
        self.accept()


class ShortcutDialog(QDialog):
    """设置主界面 - 优化字体版"""

    def __init__(self, current_key, parent=None):
        super().__init__(parent)
        self.setWindowTitle("快捷键设置")
        self.setMinimumSize(380, 200)
        self.current_key = current_key

        layout = QVBoxLayout(self)
        layout.setSpacing(15)

        # 当前快捷键显示 - 更大更清晰
        self.label = QLabel(f"当前热键: <b>{self.current_key}</b>")
        self.label.setFont(QFont("Microsoft YaHei", 14))
        self.label.setStyleSheet("padding: 15px; background-color: #F5F5F5; border-radius: 5px;")
        self.label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.label)

        # 提示信息
        tip_label = QLabel("💡 建议使用 Ctrl/Shift/Alt + 字母的组合")
        tip_label.setFont(QFont("Microsoft YaHei", 10))
        tip_label.setStyleSheet("color: gray;")
        tip_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(tip_label)

        # 录制按钮 - 增大字体和按钮尺寸
        btn_record = QPushButton("🎙️ 点击设定新快捷键")
        btn_record.setFont(QFont("Microsoft YaHei", 11))
        btn_record.setStyleSheet("""
            QPushButton {
                padding: 12px;
                background-color: #2196F3;
                color: white;
                border-radius: 5px;
                border: none;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
            QPushButton:pressed {
                background-color: #0D47A1;
            }
        """)
        btn_record.clicked.connect(self.start_record)
        layout.addWidget(btn_record)

        # 保存按钮
        btn_confirm = QPushButton("✅ 保存")
        btn_confirm.setFont(QFont("Microsoft YaHei", 11))
        btn_confirm.setStyleSheet("""
            QPushButton {
                padding: 12px;
                background-color: #4CAF50;
                color: white;
                border-radius: 5px;
                border: none;
            }
            QPushButton:hover {
                background-color: #388E3C;
            }
            QPushButton:pressed {
                background-color: #1B5E20;
            }
        """)
        btn_confirm.clicked.connect(self.accept)
        layout.addWidget(btn_confirm)

    def start_record(self):
        """开始录制"""
        recorder = ShortcutRecorder(self)
        recorder.key_recorded.connect(self.update_key)
        recorder.exec_()

    def update_key(self, key):
        """更新显示的快捷键"""
        self.current_key = key
        self.label.setText(f"当前热键: <b>{self.current_key}</b>")