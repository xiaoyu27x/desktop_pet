"""
主题和汇率设置对话框
"""
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QComboBox,
    QPushButton, QGroupBox, QFormLayout, QListWidget,
    QListWidgetItem, QMessageBox, QDoubleSpinBox, QSpinBox,
    QCheckBox, QRadioButton, QButtonGroup
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QColor


class ThemeSettingsDialog(QDialog):
    """主题和汇率监控设置对话框"""

    def __init__(self, config, parent=None):
        super().__init__(parent)

        self.config = config

        self.setWindowTitle("⚙️ 主题与汇率设置")
        self.setMinimumSize(550, 650)

        self.init_ui()
        self.load_current_settings()

    def init_ui(self):
        """初始化UI"""
        layout = QVBoxLayout()

        # ========== 主题设置 ==========
        theme_group = QGroupBox("🎨 主题颜色")
        theme_layout = QVBoxLayout()

        theme_hint = QLabel("选择主题颜色（影响小组件和报时框）")
        theme_hint.setStyleSheet("color: gray; font-size: 10px;")
        theme_layout.addWidget(theme_hint)

        # 主题选择按钮组
        self.theme_group = QButtonGroup()
        theme_buttons_layout = QHBoxLayout()

        themes = [
            ("🟤 棕色", "brown"),
            ("🔵 蓝色", "blue"),
            ("🟢 绿色", "green"),
            ("🩷 粉色", "pink"),
            ("⚫ 灰色", "gray")
        ]

        for i, (name, value) in enumerate(themes):
            radio = QRadioButton(name)
            radio.setProperty("theme_value", value)
            self.theme_group.addButton(radio, i)
            theme_buttons_layout.addWidget(radio)

        theme_layout.addLayout(theme_buttons_layout)

        # 预览框
        self.theme_preview = QLabel("预览")
        self.theme_preview.setAlignment(Qt.AlignCenter)
        self.theme_preview.setFixedHeight(60)
        self.theme_preview.setFont(QFont("Arial", 11, QFont.Bold))
        theme_layout.addWidget(self.theme_preview)

        # 连接信号
        self.theme_group.buttonClicked.connect(self.update_preview)

        theme_group.setLayout(theme_layout)
        layout.addWidget(theme_group)

        # ========== 组件显示设置 ==========
        display_group = QGroupBox("👁️ 显示设置")
        display_layout = QVBoxLayout()

        self.show_time_widget = QCheckBox("显示报时组件")
        display_layout.addWidget(self.show_time_widget)

        self.show_exchange_widget = QCheckBox("显示汇率组件")
        display_layout.addWidget(self.show_exchange_widget)

        display_group.setLayout(display_layout)
        layout.addWidget(display_group)

        # ========== 汇率监控设置 ==========
        currency_group = QGroupBox("💱 汇率监控")
        currency_layout = QVBoxLayout()

        # 更新间隔
        interval_layout = QHBoxLayout()
        interval_layout.addWidget(QLabel("更新间隔:"))

        self.interval_spin = QSpinBox()
        self.interval_spin.setRange(1, 1440)
        self.interval_spin.setValue(30)
        self.interval_spin.setSuffix(" 分钟")
        interval_layout.addWidget(self.interval_spin)
        interval_layout.addStretch()

        currency_layout.addLayout(interval_layout)

        # 监控的币种列表
        currency_layout.addWidget(QLabel("监控的币种（最多3个）:"))

        self.currency_list = QListWidget()
        self.currency_list.setMaximumHeight(120)
        currency_layout.addWidget(self.currency_list)

        # 币种管理按钮
        currency_btn_layout = QHBoxLayout()

        self.add_currency_btn = QPushButton("➕ 添加币种")
        self.add_currency_btn.clicked.connect(self.add_currency)
        currency_btn_layout.addWidget(self.add_currency_btn)

        self.remove_currency_btn = QPushButton("➖ 移除选中")
        self.remove_currency_btn.clicked.connect(self.remove_currency)
        currency_btn_layout.addWidget(self.remove_currency_btn)

        self.toggle_currency_btn = QPushButton("⏸️ 启用/禁用")
        self.toggle_currency_btn.clicked.connect(self.toggle_currency)
        currency_btn_layout.addWidget(self.toggle_currency_btn)

        currency_layout.addLayout(currency_btn_layout)

        currency_group.setLayout(currency_layout)
        layout.addWidget(currency_group)

        # ========== 提醒设置 ==========
        alert_group = QGroupBox("🔔 提醒设置")
        alert_layout = QVBoxLayout()

        # 添加提醒
        add_alert_layout = QHBoxLayout()

        add_alert_layout.addWidget(QLabel("当汇率"))

        self.alert_type_combo = QComboBox()
        self.alert_type_combo.addItems(["低于", "高于"])
        add_alert_layout.addWidget(self.alert_type_combo)

        self.alert_value_spin = QDoubleSpinBox()
        self.alert_value_spin.setDecimals(4)
        self.alert_value_spin.setRange(0.0001, 999999.9999)
        self.alert_value_spin.setValue(7.0000)
        add_alert_layout.addWidget(self.alert_value_spin)

        self.add_alert_btn = QPushButton("添加")
        self.add_alert_btn.clicked.connect(self.add_alert)
        add_alert_layout.addWidget(self.add_alert_btn)

        alert_layout.addLayout(add_alert_layout)

        # 提醒列表
        self.alert_list = QListWidget()
        self.alert_list.setMaximumHeight(100)
        alert_layout.addWidget(self.alert_list)

        self.remove_alert_btn = QPushButton("➖ 移除选中提醒")
        self.remove_alert_btn.clicked.connect(self.remove_alert)
        alert_layout.addWidget(self.remove_alert_btn)

        alert_group.setLayout(alert_layout)
        layout.addWidget(alert_group)

        # ========== 按钮 ==========
        btn_layout = QHBoxLayout()

        self.save_btn = QPushButton("💾 保存设置")
        self.save_btn.clicked.connect(self.save_settings)
        self.save_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                font-weight: bold;
                padding: 8px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        btn_layout.addWidget(self.save_btn)

        self.cancel_btn = QPushButton("❌ 取消")
        self.cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(self.cancel_btn)

        layout.addLayout(btn_layout)

        self.setLayout(layout)

    def load_current_settings(self):
        """加载当前设置"""
        # 加载主题
        current_theme = self.config.get_theme()
        for button in self.theme_group.buttons():
            if button.property("theme_value") == current_theme:
                button.setChecked(True)
                break

        # 更新预览
        self.update_preview()

        # 加载显示设置
        self.show_time_widget.setChecked(self.config.is_time_widget_visible())
        self.show_exchange_widget.setChecked(self.config.is_widget_visible())

        # 加载更新间隔
        self.interval_spin.setValue(self.config.get_update_interval())

        # 加载币种列表
        self.refresh_currency_list()

        # 加载提醒列表（当前选中的币种）
        self.refresh_alert_list()

    def update_preview(self):
        """更新主题预览"""
        # 获取选中的主题
        selected_button = self.theme_group.checkedButton()
        if selected_button:
            theme = selected_button.property("theme_value")
            colors = self.config.get_theme_colors(theme)

            self.theme_preview.setStyleSheet(f"""
                QLabel {{
                    background-color: {colors['bg_color']};
                    color: {colors['text_color']};
                    border: 2px solid {colors['border_color']};
                    border-radius: 8px;
                    padding: 10px;
                    font-weight: bold;
                }}
            """)

            self.theme_preview.setText(f"{theme.upper()} 主题预览")

    def refresh_currency_list(self):
        """刷新币种列表"""
        self.currency_list.clear()

        for i, currency in enumerate(self.config.get_currencies()):
            pair = f"{currency['target']}/{currency['base']}"
            status = "✅" if currency.get("enabled", True) else "❌"
            alerts_count = len(currency.get("alerts", []))

            text = f"{status} {pair} ({alerts_count}个提醒)"

            item = QListWidgetItem(text)
            self.currency_list.addItem(item)

    def refresh_alert_list(self):
        """刷新提醒列表"""
        self.alert_list.clear()

        # 获取当前选中的币种
        current_row = self.currency_list.currentRow()
        if current_row < 0:
            return

        alerts = self.config.get_alerts(current_row)

        for alert in alerts:
            type_text = "低于" if alert['type'] == "below" else "高于"
            text = f"{type_text} {alert['threshold']:.4f}"

            item = QListWidgetItem(text)
            self.alert_list.addItem(item)

    def add_currency(self):
        """添加币种"""
        from PyQt5.QtWidgets import QInputDialog

        # 选择目标货币
        currencies = ["USD", "EUR", "JPY", "HKD", "GBP", "AUD", "CAD", "CHF", "SGD", "KRW"]

        target, ok = QInputDialog.getItem(
            self,
            "选择货币",
            "选择要监控的货币:",
            currencies,
            0,
            False
        )

        if ok:
            success, message = self.config.add_currency("CNY", target)

            if success:
                self.refresh_currency_list()
                QMessageBox.information(self, "成功", message)
            else:
                QMessageBox.warning(self, "失败", message)

    def remove_currency(self):
        """移除币种"""
        current_row = self.currency_list.currentRow()

        if current_row >= 0:
            success, message = self.config.remove_currency(current_row)

            if success:
                self.refresh_currency_list()
                self.refresh_alert_list()
                QMessageBox.information(self, "成功", message)
        else:
            QMessageBox.warning(self, "提示", "请先选择要移除的币种")

    def toggle_currency(self):
        """切换币种启用状态"""
        current_row = self.currency_list.currentRow()

        if current_row >= 0:
            if self.config.toggle_currency(current_row):
                self.refresh_currency_list()
        else:
            QMessageBox.warning(self, "提示", "请先选择币种")

    def add_alert(self):
        """添加提醒"""
        current_row = self.currency_list.currentRow()

        if current_row < 0:
            QMessageBox.warning(self, "提示", "请先选择币种")
            return

        alert_type = "below" if self.alert_type_combo.currentText() == "低于" else "above"
        threshold = self.alert_value_spin.value()

        if self.config.add_alert(current_row, alert_type, threshold):
            self.refresh_currency_list()
            self.refresh_alert_list()
            QMessageBox.information(self, "成功", f"已添加提醒: {self.alert_type_combo.currentText()} {threshold:.4f}")

    def remove_alert(self):
        """移除提醒"""
        currency_row = self.currency_list.currentRow()
        alert_row = self.alert_list.currentRow()

        if currency_row < 0:
            QMessageBox.warning(self, "提示", "请先选择币种")
            return

        if alert_row < 0:
            QMessageBox.warning(self, "提示", "请先选择要移除的提醒")
            return

        if self.config.remove_alert(currency_row, alert_row):
            self.refresh_currency_list()
            self.refresh_alert_list()
            QMessageBox.information(self, "成功", "已移除提醒")

    def save_settings(self):
        """保存设置"""
        # 保存主题
        selected_button = self.theme_group.checkedButton()
        if selected_button:
            theme = selected_button.property("theme_value")
            self.config.set_theme(theme)

        # 保存显示设置
        self.config.set_time_widget_visible(self.show_time_widget.isChecked())
        self.config.set_widget_visible(self.show_exchange_widget.isChecked())

        # 保存更新间隔
        self.config.set_update_interval(self.interval_spin.value())

        QMessageBox.information(self, "成功", "设置已保存！\n\n请重启应用使主题生效。")

        self.accept()