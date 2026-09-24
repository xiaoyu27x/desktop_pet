"""
汇率监控设置对话框（简化版）
移除主题设置，移除位置设置（通过拖动小组件调整位置）
"""
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QComboBox,
    QPushButton, QSpinBox, QGroupBox, QFormLayout,
    QListWidget, QListWidgetItem, QMessageBox, QTabWidget, QWidget
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont


class ExchangeRateSettingsDialog(QDialog):
    """汇率监控设置对话框（简化版）"""

    def __init__(self, config, parent=None):
        super().__init__(parent)

        self.config = config

        self.setWindowTitle("💱 汇率监控设置")
        self.setMinimumSize(450, 500)

        self.init_ui()
        self.load_current_settings()

    def init_ui(self):
        """初始化UI"""
        layout = QVBoxLayout()

        # 使用标签页
        tab_widget = QTabWidget()

        # ========== 标签页1: 币种管理 ==========
        currency_tab = QWidget()
        currency_layout = QVBoxLayout()

        # 当前监控的币种列表
        list_group = QGroupBox("当前监控的币种")
        list_layout = QVBoxLayout()

        self.currency_list = QListWidget()
        list_layout.addWidget(self.currency_list)

        # 币种操作按钮
        btn_layout = QHBoxLayout()

        self.add_btn = QPushButton("➕ 添加币种")
        self.add_btn.clicked.connect(self.add_currency)
        btn_layout.addWidget(self.add_btn)

        self.remove_btn = QPushButton("➖ 移除选中")
        self.remove_btn.clicked.connect(self.remove_currency)
        btn_layout.addWidget(self.remove_btn)

        list_layout.addLayout(btn_layout)
        list_group.setLayout(list_layout)
        currency_layout.addWidget(list_group)

        # 添加币种区域
        add_group = QGroupBox("添加新币种")
        add_layout = QFormLayout()

        self.base_combo = QComboBox()
        self.base_combo.addItems(["CNY (人民币)"])
        add_layout.addRow("基准货币:", self.base_combo)

        self.target_combo = QComboBox()
        currencies = [
            "USD (美元)",
            "EUR (欧元)",
            "JPY (日元)",
            "HKD (港币)",
            "GBP (英镑)",
            "AUD (澳元)",
            "CAD (加元)",
            "CHF (瑞士法郎)",
            "SGD (新加坡元)",
            "KRW (韩元)"
        ]
        self.target_combo.addItems(currencies)
        add_layout.addRow("目标货币:", self.target_combo)

        add_group.setLayout(add_layout)
        currency_layout.addWidget(add_group)

        currency_tab.setLayout(currency_layout)
        tab_widget.addTab(currency_tab, "💱 币种管理")

        # ========== 标签页2: 更新设置 ==========
        update_tab = QWidget()
        update_layout = QVBoxLayout()

        update_group = QGroupBox("更新间隔")
        update_form = QFormLayout()

        self.interval_spin = QSpinBox()
        self.interval_spin.setRange(1, 1440)
        self.interval_spin.setValue(self.config.get_update_interval())
        self.interval_spin.setSuffix(" 分钟")
        update_form.addRow("自动更新间隔:", self.interval_spin)

        hint = QLabel("建议设置为 30-60 分钟\n过于频繁可能被限制访问")
        hint.setStyleSheet("color: gray; font-size: 10px;")
        update_form.addRow("", hint)

        update_group.setLayout(update_form)
        update_layout.addWidget(update_group)
        update_layout.addStretch()

        update_tab.setLayout(update_layout)
        tab_widget.addTab(update_tab, "⚙️ 更新设置")

        layout.addWidget(tab_widget)

        # ========== 底部按钮 ==========
        btn_layout = QHBoxLayout()

        self.save_btn = QPushButton("💾 保存设置")
        self.save_btn.clicked.connect(self.save_settings)
        self.save_btn.setStyleSheet("""
            QPushButton {
                background-color: #D2B48C;
                color: #5D4037;
                padding: 8px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #C19A6B;
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
        self.refresh_currency_list()

    def refresh_currency_list(self):
        """刷新币种列表"""
        self.currency_list.clear()

        for i, currency in enumerate(self.config.get_currencies()):
            status = "✅" if currency.get('enabled', True) else "❌"
            text = f"{status} {currency['target']}/{currency['base']}"

            # 显示提醒数量
            alert_count = len(currency.get('alerts', []))
            if alert_count > 0:
                text += f"  (🔔×{alert_count})"

            item = QListWidgetItem(text)
            self.currency_list.addItem(item)

    def add_currency(self):
        """添加币种"""
        base = "CNY"
        target = self.target_combo.currentText().split()[0]

        success, message = self.config.add_currency(base, target)

        if success:
            self.refresh_currency_list()
            QMessageBox.information(self, "成功", message)
        else:
            QMessageBox.warning(self, "提示", message)

    def remove_currency(self):
        """移除币种"""
        current_row = self.currency_list.currentRow()

        if current_row >= 0:
            reply = QMessageBox.question(
                self,
                "确认",
                "确定要移除这个币种吗？\n相关的提醒设置也会被删除。",
                QMessageBox.Yes | QMessageBox.No
            )

            if reply == QMessageBox.Yes:
                success, message = self.config.remove_currency(current_row)
                if success:
                    self.refresh_currency_list()
                    QMessageBox.information(self, "成功", message)
        else:
            QMessageBox.warning(self, "提示", "请先选择要移除的币种")

    def save_settings(self):
        """保存所有设置"""
        # 保存更新间隔
        self.config.set_update_interval(self.interval_spin.value())

        QMessageBox.information(self, "成功", "设置已保存")
        self.accept()


class AlertSettingsDialog(QDialog):
    """提醒设置对话框"""

    def __init__(self, config, parent=None):
        super().__init__(parent)

        self.config = config

        self.setWindowTitle("🔔 汇率提醒设置")
        self.setMinimumSize(450, 400)

        self.init_ui()
        self.load_alerts()

    def init_ui(self):
        """初始化UI"""
        layout = QVBoxLayout()

        # 选择币种
        currency_group = QGroupBox("选择币种")
        currency_layout = QHBoxLayout()

        self.currency_combo = QComboBox()
        self.refresh_currency_combo()
        self.currency_combo.currentIndexChanged.connect(self.load_alerts)
        currency_layout.addWidget(QLabel("币种:"))
        currency_layout.addWidget(self.currency_combo)

        currency_group.setLayout(currency_layout)
        layout.addWidget(currency_group)

        # 提醒列表
        alert_group = QGroupBox("当前提醒")
        alert_layout = QVBoxLayout()

        self.alert_list = QListWidget()
        alert_layout.addWidget(self.alert_list)

        # 提醒操作按钮
        btn_layout = QHBoxLayout()

        self.add_alert_btn = QPushButton("➕ 添加提醒")
        self.add_alert_btn.clicked.connect(self.add_alert)
        btn_layout.addWidget(self.add_alert_btn)

        self.remove_alert_btn = QPushButton("➖ 移除选中")
        self.remove_alert_btn.clicked.connect(self.remove_alert)
        btn_layout.addWidget(self.remove_alert_btn)

        alert_layout.addLayout(btn_layout)
        alert_group.setLayout(alert_layout)
        layout.addWidget(alert_group)

        # 添加提醒区域
        add_group = QGroupBox("添加新提醒")
        add_layout = QHBoxLayout()

        add_layout.addWidget(QLabel("当汇率"))

        self.alert_type_combo = QComboBox()
        self.alert_type_combo.addItems(["低于", "高于"])
        add_layout.addWidget(self.alert_type_combo)

        self.threshold_spin = QSpinBox()
        self.threshold_spin.setRange(1, 999999)
        self.threshold_spin.setValue(7)
        add_layout.addWidget(self.threshold_spin)

        add_group.setLayout(add_layout)
        layout.addWidget(add_group)

        # 底部按钮
        btn_layout = QHBoxLayout()

        close_btn = QPushButton("关闭")
        close_btn.clicked.connect(self.accept)
        btn_layout.addWidget(close_btn)

        layout.addLayout(btn_layout)

        self.setLayout(layout)

    def refresh_currency_combo(self):
        """刷新币种下拉框"""
        self.currency_combo.clear()

        currencies = self.config.get_currencies()
        for currency in currencies:
            text = f"{currency['target']}/{currency['base']}"
            self.currency_combo.addItem(text)

    def load_alerts(self):
        """加载提醒列表"""
        self.alert_list.clear()

        currency_index = self.currency_combo.currentIndex()
        if currency_index < 0:
            return

        alerts = self.config.get_alerts(currency_index)

        for alert in alerts:
            type_text = "低于" if alert['type'] == "below" else "高于"
            text = f"{type_text} {alert['threshold']}"
            self.alert_list.addItem(text)

    def add_alert(self):
        """添加提醒"""
        currency_index = self.currency_combo.currentIndex()
        if currency_index < 0:
            QMessageBox.warning(self, "提示", "请先选择币种")
            return

        alert_type = "below" if self.alert_type_combo.currentText() == "低于" else "above"
        threshold = self.threshold_spin.value()

        if self.config.add_alert(currency_index, alert_type, threshold):
            self.load_alerts()
            QMessageBox.information(self, "成功", "提醒已添加")

    def remove_alert(self):
        """移除提醒"""
        currency_index = self.currency_combo.currentIndex()
        alert_index = self.alert_list.currentRow()

        if alert_index >= 0:
            if self.config.remove_alert(currency_index, alert_index):
                self.load_alerts()
                QMessageBox.information(self, "成功", "提醒已移除")
        else:
            QMessageBox.warning(self, "提示", "请先选择要移除的提醒")