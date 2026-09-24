"""
汇率显示小组件 - 独立窗口，跟随桌宠移动
完全重构版本：
1. 移除所有主题配置，使用与番茄钟一致的米白色背景
2. 小组件集成功能按钮（币种设置、提醒、Excel导出）
3. 跟随宠物移动，无需定时器
"""
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont


class ExchangeRateDisplay(QWidget):
    """汇率显示组件（独立窗口，带功能按钮）"""

    # 信号
    currency_clicked = pyqtSignal()   # 币种设置按钮
    alert_clicked = pyqtSignal()      # 提醒设置按钮
    excel_clicked = pyqtSignal()      # Excel导出按钮
    debug_clicked = pyqtSignal()      # 调试按钮（新增）

    def __init__(self, pet_instance):
        """
        初始化显示组件

        Args:
            pet_instance: 宠物主窗口实例
        """
        super().__init__()

        self.pet = pet_instance

        # ⭐ 设置为独立的置顶窗口
        self.setWindowFlags(
            Qt.FramelessWindowHint |
            Qt.WindowStaysOnTopHint |
            Qt.Tool
        )

        # ⭐ 设置固定尺寸（增加宽度以容纳5个按钮）
        self.setFixedSize(260, 180)

        # 状态
        self.is_visible = False

        # 当前显示的汇率数据
        self.current_rates = []  # [{currency_pair, rate, time, base, target}, ...]

        # 初始化UI
        self.init_ui()

        # 默认隐藏
        self.hide()

        print("💱 汇率显示组件已创建（米白色背景，带功能按钮）")

    def init_ui(self):
        """初始化用户界面"""
        # 主布局
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(8)

        # ========== 标题区域 ==========
        title_label = QLabel("💱 汇率监控")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setFont(QFont("Microsoft YaHei", 10, QFont.Bold))
        title_label.setStyleSheet("color: #5D4037;")
        main_layout.addWidget(title_label)

        # ========== 汇率显示区域 ==========
        self.rate_label = QLabel("等待更新...")
        self.rate_label.setAlignment(Qt.AlignCenter)
        self.rate_label.setFont(QFont("Arial", 9))
        self.rate_label.setWordWrap(True)
        self.rate_label.setStyleSheet("color: #5D4037; padding: 5px;")
        self.rate_label.setMinimumHeight(80)
        main_layout.addWidget(self.rate_label)

        # ========== 按钮区域 ==========
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(5)

        # 币种设置按钮
        self.currency_btn = QPushButton("💰")
        self.currency_btn.setFixedSize(40, 30)
        self.currency_btn.setToolTip("币种设置")
        self.currency_btn.clicked.connect(self.currency_clicked.emit)
        btn_layout.addWidget(self.currency_btn)

        # 提醒按钮
        self.alert_btn = QPushButton("🔔")
        self.alert_btn.setFixedSize(40, 30)
        self.alert_btn.setToolTip("设置提醒")
        self.alert_btn.clicked.connect(self.alert_clicked.emit)
        btn_layout.addWidget(self.alert_btn)

        # Excel按钮
        self.excel_btn = QPushButton("📊")
        self.excel_btn.setFixedSize(40, 30)
        self.excel_btn.setToolTip("导出Excel")
        self.excel_btn.clicked.connect(self.excel_clicked.emit)
        btn_layout.addWidget(self.excel_btn)

        # 调试按钮（新增）
        self.debug_btn = QPushButton("🧪")
        self.debug_btn.setFixedSize(40, 30)
        self.debug_btn.setToolTip("调试测试")
        self.debug_btn.clicked.connect(self.debug_clicked.emit)
        btn_layout.addWidget(self.debug_btn)

        # 关闭按钮
        self.close_btn = QPushButton("❌")
        self.close_btn.setFixedSize(40, 30)
        self.close_btn.setToolTip("关闭")
        self.close_btn.clicked.connect(self.hide_widget)
        btn_layout.addWidget(self.close_btn)

        main_layout.addLayout(btn_layout)

        # ========== 应用整体样式（与番茄钟一致）==========
        self.setStyleSheet("""
            QWidget {
                background-color: #F5F5DC;
                border: 2px solid #D2B48C;
                border-radius: 8px;
            }
            QPushButton {
                background-color: #D2B48C;
                color: #5D4037;
                border: 1px solid #C19A6B;
                border-radius: 4px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #C19A6B;
            }
            QPushButton:pressed {
                background-color: #B8860B;
            }
        """)

    def show_widget(self):
        """显示小组件"""
        # ⭐ 先更新位置，再显示（避免在屏幕中央闪现）
        self.update_position()

        # 显示窗口
        self.show()
        self.is_visible = True

        print("✅ 汇率显示组件已显示")

    def hide_widget(self):
        """隐藏小组件"""
        self.hide()
        self.is_visible = False

        print("👻 汇率显示组件已隐藏")

    def toggle_widget(self):
        """切换显示/隐藏"""
        if self.is_visible:
            self.hide_widget()
        else:
            self.show_widget()

    def update_rate(self, currency_pair, rate, time, base=None, target=None):
        """
        更新单个币种的汇率

        Args:
            currency_pair: 货币对 (如 "USD/CNY")
            rate: 汇率值
            time: 更新时间
            base: 基准货币（可选）
            target: 目标货币（可选）
        """
        # 查找并更新对应的汇率
        found = False
        for item in self.current_rates:
            if item['currency_pair'] == currency_pair:
                item['rate'] = rate
                item['time'] = time
                if base:
                    item['base'] = base
                if target:
                    item['target'] = target
                found = True
                break

        if not found:
            self.current_rates.append({
                'currency_pair': currency_pair,
                'rate': rate,
                'time': time,
                'base': base or 'CNY',
                'target': target or currency_pair.split('/')[0]
            })

        # 更新显示
        self.refresh_display()

    def refresh_display(self):
        """刷新显示内容"""
        if not self.current_rates:
            self.rate_label.setText("等待更新...")
            return

        # 构建显示文本
        lines = []

        for item in self.current_rates:
            rate = item['rate']
            target = item.get('target', item['currency_pair'].split('/')[0])

            lines.append(f"{target}: {rate:.4f}")

        # 添加更新时间
        if self.current_rates:
            last_update = self.current_rates[-1]['time'].strftime("%H:%M:%S")
            lines.append(f"\n更新: {last_update}")

        # 设置文本
        text = "\n".join(lines)
        self.rate_label.setText(text)

    def update_position(self):
        """⭐ 更新显示位置（跟随宠物）"""
        # ⭐ 即使未显示也要计算位置（避免首次显示时在屏幕中央闪现）

        # 获取宠物的全局位置
        pet_global_pos = self.pet.pos()
        pet_x = pet_global_pos.x()
        pet_y = pet_global_pos.y()
        pet_width = self.pet.pet_width

        # 水平：显示在宠物右侧
        display_x = pet_x + pet_width + 10

        # 垂直：与宠物顶部对齐
        display_y = pet_y

        # 检查是否与番茄钟冲突
        if hasattr(self.pet, 'pomodoro_display'):
            if hasattr(self.pet.pomodoro_display, 'is_visible'):
                if self.pet.pomodoro_display.is_visible:
                    # 番茄钟在宠物上方，汇率组件在右侧通常不冲突
                    pass

        # 移动独立窗口
        self.move(display_x, display_y)

    def clear_rates(self):
        """清空汇率数据"""
        self.current_rates.clear()
        self.refresh_display()

    def get_current_rates(self):
        """获取当前汇率数据（用于外部查询）"""
        return self.current_rates.copy()

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