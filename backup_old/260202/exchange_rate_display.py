"""
汇率显示小组件 - 独立窗口，跟随桌宠移动
保留所有原有功能：抓取、存储、提醒、Excel导出
"""
from PyQt5.QtWidgets import QLabel
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont


class ExchangeRateDisplay:
    """汇率显示组件（独立窗口）"""

    def __init__(self, pet_instance, config):
        """
        初始化显示组件

        Args:
            pet_instance: 宠物主窗口实例
            config: ExchangeRateConfig 配置实例
        """
        self.pet = pet_instance
        self.config = config

        # ⭐ 创建独立窗口
        self.display_label = QLabel()

        # ⭐ 设置为独立的置顶窗口
        self.display_label.setWindowFlags(
            Qt.FramelessWindowHint |
            Qt.WindowStaysOnTopHint |
            Qt.Tool
        )

        # ⭐ 设置对齐方式：居中
        self.display_label.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)

        # ⭐ 允许自动换行
        self.display_label.setWordWrap(True)

        # ⭐ 设置字体
        self.display_label.setFont(QFont("Arial", 9))

        # ⭐ 设置固定尺寸
        self.display_label.setFixedSize(200, 120)

        # ⭐ 设置边距
        self.display_label.setContentsMargins(8, 8, 8, 8)

        # 默认隐藏
        self.display_label.hide()

        # 状态
        self.is_visible = False

        # 当前显示的汇率数据
        self.current_rates = []  # [{currency_pair, rate, time, base, target}, ...]

        # 应用主题
        self.apply_theme()

        print("💱 汇率显示组件已创建（独立窗口）")

    def apply_theme(self):
        """应用主题颜色"""
        theme_colors = self.config.get_theme_colors()

        self.display_label.setStyleSheet(f"""
            QLabel {{
                background-color: {theme_colors['bg_color']};
                color: {theme_colors['text_color']};
                border: 2px solid {theme_colors['border_color']};
                border-radius: 8px;
                padding: 10px;
                font-weight: bold;
            }}
        """)

    def show_widget(self):
        """显示小组件"""
        # ⭐ 先更新位置，再显示
        self.update_position()

        # 显示窗口
        self.display_label.show()
        self.is_visible = True

        # 保存状态
        self.config.set_widget_visible(True)

        print("✅ 汇率显示组件已显示")

    def hide_widget(self):
        """隐藏小组件"""
        self.display_label.hide()
        self.is_visible = False

        # 保存状态
        self.config.set_widget_visible(False)

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
            self.display_label.setText("💱 汇率监控\n等待更新...")
            return

        # 获取启用的币种
        enabled_currencies = self.config.get_enabled_currencies()

        if not enabled_currencies:
            self.display_label.setText("💱 汇率监控\n未设置币种")
            return

        # 构建显示文本
        lines = ["💱 汇率监控"]

        for currency in enabled_currencies:
            currency_pair = f"{currency['target']}/{currency['base']}"

            # 查找对应的汇率
            rate_data = None
            for item in self.current_rates:
                if item['currency_pair'] == currency_pair:
                    rate_data = item
                    break

            if rate_data:
                rate = rate_data['rate']
                time_str = rate_data['time'].strftime("%H:%M")
                lines.append(f"{currency['target']}: {rate:.4f}")

                # 检查提醒
                alerts = currency.get('alerts', [])
                for alert in alerts:
                    if alert['type'] == 'below' and rate <= alert['threshold']:
                        lines.append(f"  ⚠️ 低于 {alert['threshold']:.4f}")
                    elif alert['type'] == 'above' and rate >= alert['threshold']:
                        lines.append(f"  ⚠️ 高于 {alert['threshold']:.4f}")
            else:
                lines.append(f"{currency['target']}: ---.----")

        # 添加更新时间
        if self.current_rates:
            last_update = self.current_rates[-1]['time'].strftime("%H:%M:%S")
            lines.append(f"\n更新: {last_update}")

        # 设置文本
        text = "\n".join(lines)
        self.display_label.setText(text)

    def update_position(self):
        """⭐ 更新显示位置（跟随宠物）"""
        # 获取宠物的全局位置
        pet_global_pos = self.pet.pos()
        pet_x = pet_global_pos.x()
        pet_y = pet_global_pos.y()
        pet_width = self.pet.pet_width
        pet_height = self.pet.pet_height

        # 计算小组件位置
        display_width = 200
        display_height = 120

        # 显示在右侧
        display_x = pet_x + pet_width + 10
        display_y = pet_y

        # 检查是否与番茄钟冲突
        if hasattr(self.pet, 'pomodoro_display'):
            if self.pet.pomodoro_display.is_visible:
                # 番茄钟在上方，汇率组件可能需要调整
                # 但右侧通常不冲突，保持原位置
                pass

        # 移动独立窗口
        self.display_label.move(display_x, display_y)

    def clear_rates(self):
        """清空汇率数据"""
        self.current_rates.clear()
        self.refresh_display()

    def get_current_rates(self):
        """获取当前汇率数据（用于外部查询）"""
        return self.current_rates.copy()