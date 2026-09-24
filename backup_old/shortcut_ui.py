from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton
from PyQt5.QtCore import Qt, pyqtSignal


class ShortcutRecorder(QDialog):
    """录制按键的专用小窗口"""
    key_recorded = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("录制中...")
        self.setFixedSize(200, 100)
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("请按下组合键...\n(如 Ctrl+Shift+S)", alignment=Qt.AlignCenter))

    def keyPressEvent(self, event):
        modifiers = event.modifiers()
        keys = []
        if modifiers & Qt.ControlModifier: keys.append("ctrl")
        if modifiers & Qt.ShiftModifier: keys.append("shift")
        if modifiers & Qt.AltModifier: keys.append("alt")

        key_text = event.text().lower()
        # 处理特殊键
        if not key_text or ord(event.text()[0]) < 32:
            key_map = {Qt.Key_Space: "space", Qt.Key_Return: "enter", Qt.Key_Tab: "tab"}
            key_text = key_map.get(event.key(), "")

        if key_text:
            keys.append(key_text)
            self.key_recorded.emit("+".join(keys))
            self.accept()


class ShortcutDialog(QDialog):
    """设置主界面"""

    def __init__(self, current_key, parent=None):
        super().__init__(parent)
        self.setWindowTitle("快捷键设置")
        self.current_key = current_key
        layout = QVBoxLayout(self)

        self.label = QLabel(f"当前热键: {self.current_key}")
        layout.addWidget(self.label)

        btn_record = QPushButton("点击设定新快捷键")
        btn_record.clicked.connect(self.start_record)
        layout.addWidget(btn_record)

        btn_confirm = QPushButton("保存")
        btn_confirm.clicked.connect(self.accept)
        layout.addWidget(btn_confirm)

    def start_record(self):
        recorder = ShortcutRecorder(self)
        recorder.key_recorded.connect(self.update_key)
        recorder.exec_()

    def update_key(self, key):
        self.current_key = key
        self.label.setText(f"当前热键: {self.current_key}")