"""
统一的配置管理模块 - 完整版
支持：窗口避让、碰撞距离、快捷键等设置记忆
"""
import json
import os


class SettingsManager:
    """统一管理所有配置"""

    def __init__(self, filename="settings.json"):
        self.filename = filename
        self.settings = self.load_settings()

    def load_settings(self):
        """加载配置"""
        default_settings = {
            "window_avoidance_enabled": False,  # 窗口避让是否开启（默认关闭）
            "collision_margin": 20,  # 碰撞边距
            "current_hotkey": "ctrl+shift+a",  # 当前快捷键
            "report_time_enabled": True,  # 是否启用报时
        }

        if os.path.exists(self.filename):
            try:
                with open(self.filename, 'r', encoding='utf-8') as f:
                    loaded = json.load(f)
                    # 合并默认值和加载的值
                    default_settings.update(loaded)
                    return default_settings
            except Exception as e:
                print(f"⚠️ 加载配置失败: {e}")
                return default_settings
        return default_settings

    def save_settings(self):
        """保存配置"""
        try:
            with open(self.filename, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, ensure_ascii=False, indent=4)
            print(f"✅ 配置已保存: {self.filename}")
            return True
        except Exception as e:
            print(f"❌ 保存配置失败: {e}")
            return False

    def get(self, key, default=None):
        """获取配置值"""
        return self.settings.get(key, default)

    def set(self, key, value):
        """设置配置值"""
        self.settings[key] = value
        self.save_settings()

    def get_window_avoidance(self):
        """获取窗口避让状态"""
        return self.settings.get("window_avoidance_enabled", False)

    def set_window_avoidance(self, enabled):
        """设置窗口避让状态"""
        self.settings["window_avoidance_enabled"] = enabled
        self.save_settings()

    def get_collision_margin(self):
        """获取碰撞边距"""
        return self.settings.get("collision_margin", 20)

    def set_collision_margin(self, margin):
        """设置碰撞边距 - 自动保存"""
        self.settings["collision_margin"] = margin
        self.save_settings()

    def get_hotkey(self):
        """获取快捷键"""
        return self.settings.get("current_hotkey", "ctrl+shift+a")

    def set_hotkey(self, hotkey):
        """设置快捷键"""
        self.settings["current_hotkey"] = hotkey
        self.save_settings()