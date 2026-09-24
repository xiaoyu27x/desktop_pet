"""
汇率显示小组件 - 显示在桌宠左侧或右侧
"""
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont, QPainter, QColor, QPen
import math


class ExchangeRateWidget(QWidget):
    """汇率显示小组件"""

    def __init__(self, parent=None, position="right"):
        super().__init__(parent)

        self.parent_pet = parent
        self.position = position  # "left" 或 "right"

        # 窗口设置
        self.setWindowFlags(
            Qt.FramelessWindowHint |
            Qt.WindowStaysOnTopHint |
            Qt.Tool
        )
        self.setAttribute(Qt.WA_TranslucentBackground)

        # 组件大小
        self.widget_width = 180
        self.widget_height = 200
        self.resize(self.widget_width, self.widget_height)

        # 当前汇率数据
        self.current_rate = None
        self.currency_pair = "USD/CNY"
        self.rate_history = []  # 用于绘制折线图

        # 是否显示
        self.is_visible = False

        # 创建UI
        self.init_ui()

        # 更新位置定时器
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_position)

        print(f"💱 汇率小组件已创建 (位置: {position})")

    def init_ui(self):
        """初始化UI"""
        layout = QVBoxLayout()
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)

        # 背景容器（用于绘制背景）
        self.setStyleSheet("""
            QWidget {
                background-color: rgba(255, 255, 255, 230);
                border: 2px solid #2196F3;
                border-radius: 10px;
            }
            QLabel {
                background-color: transparent;
                color: #333;
            }
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
        """)

        # 标题
        self.title_label = QLabel("💱 汇率监控")
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setFont(QFont("Arial", 10, QFont.Bold))
        layout.addWidget(self.title_label)

        # 货币对
        self.pair_label = QLabel(self.currency_pair)
        self.pair_label.setAlignment(Qt.AlignCenter)
        self.pair_label.setFont(QFont("Arial", 9))
        layout.addWidget(self.pair_label)

        # 当前汇率
        self.rate_label = QLabel("---.----")
        self.rate_label.setAlignment(Qt.AlignCenter)
        self.rate_label.setFont(QFont("Arial", 16, QFont.Bold))
        self.rate_label.setStyleSheet("color: #2196F3;")
        layout.addWidget(self.rate_label)

        # 更新时间
        self.time_label = QLabel("等待更新...")
        self.time_label.setAlignment(Qt.AlignCenter)
        self.time_label.setFont(QFont("Arial", 8))
        self.time_label.setStyleSheet("color: #999;")
        layout.addWidget(self.time_label)

        # 迷你折线图区域（使用自定义绘制）
        self.chart_widget = MiniChartWidget(self)
        self.chart_widget.setMinimumHeight(80)
        layout.addWidget(self.chart_widget)

        # 按钮区域
        btn_layout = QHBoxLayout()

        self.excel_btn = QPushButton("📊")
        self.excel_btn.setMaximumWidth(40)
        self.excel_btn.setToolTip("打开Excel")
        btn_layout.addWidget(self.excel_btn)

        self.alert_btn = QPushButton("🔔")
        self.alert_btn.setMaximumWidth(40)
        self.alert_btn.setToolTip("设置提醒")
        btn_layout.addWidget(self.alert_btn)

        self.settings_btn = QPushButton("⚙️")
        self.settings_btn.setMaximumWidth(40)
        self.settings_btn.setToolTip("设置")
        btn_layout.addWidget(self.settings_btn)

        self.close_btn = QPushButton("❌")
        self.close_btn.setMaximumWidth(40)
        self.close_btn.setToolTip("关闭")
        self.close_btn.clicked.connect(self.hide_widget)
        btn_layout.addWidget(self.close_btn)

        layout.addLayout(btn_layout)

        self.setLayout(layout)

    def show_widget(self):
        """显示小组件"""
        self.is_visible = True
        self.show()
        self.update_position()
        self.update_timer.start(100)  # 每100ms更新位置
        print("✅ 汇率小组件已显示")

    def hide_widget(self):
        """隐藏小组件"""
        self.is_visible = False
        self.hide()
        self.update_timer.stop()
        print("👻 汇率小组件已隐藏")

    def update_position(self):
        """更新小组件位置（跟随桌宠）"""
        if not self.parent_pet or not self.is_visible:
            return

        # 获取桌宠位置
        pet_x = self.parent_pet.x
        pet_y = self.parent_pet.y
        pet_width = self.parent_pet.pet_width
        pet_height = self.parent_pet.pet_height

        # 计算小组件位置
        if self.position == "right":
            # 显示在右侧
            x = pet_x + pet_width + 10
            y = pet_y
        else:
            # 显示在左侧
            x = pet_x - self.widget_width - 10
            y = pet_y

        # 检查番茄钟位置，避免冲突
        if hasattr(self.parent_pet, 'pomodoro_display'):
            pomo = self.parent_pet.pomodoro_display
            if pomo.is_visible:
                # 番茄钟通常在左上方，如果我们也在左侧，往下移
                if self.position == "left":
                    y = pet_y + pet_height + 10

        self.move(int(x), int(y))

    def update_rate(self, rate_data):
        """
        更新汇率显示

        Args:
            rate_data: {currency_pair, rate, time}
        """
        self.current_rate = rate_data['rate']
        self.currency_pair = rate_data['currency_pair']

        # 更新显示
        self.pair_label.setText(self.currency_pair)
        self.rate_label.setText(f"{self.current_rate:.4f}")
        self.time_label.setText(rate_data['time'].strftime("%H:%M:%S"))

        # 添加到历史
        self.rate_history.append({
            'time': rate_data['time'],
            'rate': self.current_rate
        })

        # 只保留最近50个数据点
        if len(self.rate_history) > 50:
            self.rate_history.pop(0)

        # 更新图表
        self.chart_widget.set_data(self.rate_history)

    def mousePressEvent(self, event):
        """鼠标按下 - 准备拖动"""
        if event.button() == Qt.LeftButton:
            self.drag_position = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        """鼠标移动 - 拖动窗口"""
        if event.buttons() == Qt.LeftButton:
            self.move(event.globalPos() - self.drag_position)
            event.accept()


class MiniChartWidget(QWidget):
    """迷你折线图组件"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.data = []  # [{time, rate}, ...]
        self.setMinimumSize(160, 80)

    def set_data(self, data):
        """设置数据并重绘"""
        self.data = data
        self.update()

    def paintEvent(self, event):
        """绘制折线图"""
        if not self.data or len(self.data) < 2:
            return

        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # 绘制区域
        width = self.width() - 20
        height = self.height() - 20
        margin_x = 10
        margin_y = 10

        # 计算数据范围
        rates = [item['rate'] for item in self.data]
        min_rate = min(rates)
        max_rate = max(rates)
        rate_range = max_rate - min_rate

        if rate_range == 0:
            rate_range = 1

        # 绘制背景网格
        painter.setPen(QPen(QColor(200, 200, 200), 1, Qt.DashLine))
        for i in range(5):
            y = margin_y + (height * i / 4)
            painter.drawLine(margin_x, int(y), margin_x + width, int(y))

        # 绘制折线
        painter.setPen(QPen(QColor(33, 150, 243), 2))

        points = []
        for i, item in enumerate(self.data):
            # 计算坐标
            x = margin_x + (width * i / max(len(self.data) - 1, 1))
            y_normalized = (item['rate'] - min_rate) / rate_range
            y = margin_y + height - (y_normalized * height)

            points.append((int(x), int(y)))

        # 绘制线段
        for i in range(len(points) - 1):
            painter.drawLine(points[i][0], points[i][1],
                             points[i + 1][0], points[i + 1][1])

        # 绘制数据点
        painter.setBrush(QColor(33, 150, 243))
        for x, y in points:
            painter.drawEllipse(x - 2, y - 2, 4, 4)

        # 绘制最高最低值标签
        painter.setPen(QPen(QColor(0, 0, 0)))
        painter.setFont(QFont("Arial", 7))
        painter.drawText(margin_x + width - 40, margin_y + 10,
                         f"{max_rate:.4f}")
        painter.drawText(margin_x + width - 40, margin_y + height,
                         f"{min_rate:.4f}")