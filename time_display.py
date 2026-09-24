"""
报时显示组件 - 固定米白色主题版本
直接使用原有的 time_label，移除主题功能，使用与番茄钟一致的米白色样式
"""
from PyQt5.QtGui import QFont


class TimeDisplay:
    """报时显示组件（包装原有 time_label）"""

    def __init__(self, pet_instance, config=None):
        """
        初始化报时组件

        Args:
            pet_instance: 宠物主窗口实例（必须已经创建了 time_label）
            config: 配置实例（可选，用于保存显示状态）
        """
        self.pet = pet_instance
        self.config = config

        # ⭐ 直接使用桌宠已有的 time_label
        if not hasattr(pet_instance, 'time_label'):
            raise ValueError("桌宠实例必须先创建 time_label")

        self.time_label = pet_instance.time_label

        # 根据配置决定是否显示（如果有配置的话）
        if config and hasattr(config, 'is_time_widget_visible'):
            self.is_visible = config.is_time_widget_visible()
        else:
            self.is_visible = True  # 默认显示

        # ⭐ 应用固定的米白色主题（与番茄钟一致）
        self.apply_fixed_theme()

        if self.is_visible:
            self.time_label.show()
        else:
            self.time_label.hide()

        print("🕐 报时显示组件已初始化（米白色主题）")

    def apply_fixed_theme(self):
        """应用固定的米白色主题"""
        # ⭐ 使用与番茄钟和汇率组件一致的米白色主题
        self.time_label.setStyleSheet("""
            QLabel {
                background-color: #F5F5DC;
                color: #5D4037;
                border: 1px solid #D2B48C;
                border-radius: 5px;
                padding: 2px;
                font-weight: bold;
            }
        """)

    def show_widget(self):
        """显示报时组件"""
        self.time_label.show()
        self.is_visible = True

        # 保存状态（如果有配置的话）
        if self.config and hasattr(self.config, 'set_time_widget_visible'):
            self.config.set_time_widget_visible(True)

        print("✅ 报时组件已显示")

    def hide_widget(self):
        """隐藏报时组件"""
        self.time_label.hide()
        self.is_visible = False

        # 保存状态（如果有配置的话）
        if self.config and hasattr(self.config, 'set_time_widget_visible'):
            self.config.set_time_widget_visible(False)

        print("👻 报时组件已隐藏")

    def toggle_widget(self):
        """切换显示/隐藏"""
        if self.is_visible:
            self.hide_widget()
        else:
            self.show_widget()

    def update_time(self, time_str):
        """更新时间显示"""
        self.time_label.setText(time_str)