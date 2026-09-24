"""
汇率监控配置存储模块（简化版）
移除主题配置功能，仅保留必要的币种和提醒设置
"""
import json
import os


class ExchangeRateConfig:
    """汇率监控配置管理器（简化版）"""

    def __init__(self, config_file="exchange_config.json"):
        self.config_file = config_file
        self.config = self.load_config()

    def load_config(self):
        """加载配置"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"⚠️ 加载配置失败: {e}")
                return self._default_config()
        else:
            return self._default_config()

    def save_config(self):
        """保存配置"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, ensure_ascii=False, indent=2)
            print("✅ 配置已保存")
        except Exception as e:
            print(f"❌ 保存配置失败: {e}")

    def _default_config(self):
        """默认配置"""
        return {
            # 显示设置
            "widget_visible": False,

            # 监控的币种（最多3个）
            "currencies": [
                {
                    "base": "CNY",
                    "target": "USD",
                    "enabled": True,
                    "alerts": []  # [{type: "below"/"above", threshold: 7.0}]
                }
            ],

            # 更新间隔（分钟）
            "update_interval": 30
        }

    # ========== 币种管理 ==========

    def get_currencies(self):
        """获取所有监控的币种"""
        return self.config.get("currencies", [])

    def get_enabled_currencies(self):
        """获取启用的币种"""
        return [c for c in self.get_currencies() if c.get("enabled", True)]

    def add_currency(self, base, target):
        """添加币种监控"""
        currencies = self.get_currencies()

        # 最多3个
        if len(currencies) >= 3:
            return False, "最多只能监控3个币种"

        # 检查是否已存在
        for c in currencies:
            if c["base"] == base and c["target"] == target:
                return False, "该币种已存在"

        currencies.append({
            "base": base,
            "target": target,
            "enabled": True,
            "alerts": []
        })

        self.config["currencies"] = currencies
        self.save_config()

        return True, "添加成功"

    def remove_currency(self, index):
        """移除币种"""
        currencies = self.get_currencies()

        if 0 <= index < len(currencies):
            removed = currencies.pop(index)
            self.config["currencies"] = currencies
            self.save_config()
            return True, f"已移除 {removed['target']}/{removed['base']}"

        return False, "无效的索引"

    def toggle_currency(self, index):
        """切换币种启用状态"""
        currencies = self.get_currencies()

        if 0 <= index < len(currencies):
            currencies[index]["enabled"] = not currencies[index]["enabled"]
            self.config["currencies"] = currencies
            self.save_config()
            return True

        return False

    def update_currency(self, index, base, target):
        """更新币种"""
        currencies = self.get_currencies()

        if 0 <= index < len(currencies):
            currencies[index]["base"] = base
            currencies[index]["target"] = target
            self.config["currencies"] = currencies
            self.save_config()
            return True

        return False

    # ========== 提醒管理 ==========

    def add_alert(self, currency_index, alert_type, threshold):
        """为指定币种添加提醒"""
        currencies = self.get_currencies()

        if 0 <= currency_index < len(currencies):
            currencies[currency_index]["alerts"].append({
                "type": alert_type,
                "threshold": threshold
            })
            self.config["currencies"] = currencies
            self.save_config()
            return True

        return False

    def remove_alert(self, currency_index, alert_index):
        """移除提醒"""
        currencies = self.get_currencies()

        if 0 <= currency_index < len(currencies):
            alerts = currencies[currency_index]["alerts"]
            if 0 <= alert_index < len(alerts):
                alerts.pop(alert_index)
                self.config["currencies"] = currencies
                self.save_config()
                return True

        return False

    def get_alerts(self, currency_index):
        """获取指定币种的提醒"""
        currencies = self.get_currencies()

        if 0 <= currency_index < len(currencies):
            return currencies[currency_index].get("alerts", [])

        return []

    # ========== 其他设置 ==========

    def is_widget_visible(self):
        """小组件是否可见"""
        return self.config.get("widget_visible", False)

    def set_widget_visible(self, visible):
        """设置小组件可见性"""
        self.config["widget_visible"] = visible
        self.save_config()

    def get_update_interval(self):
        """获取更新间隔（分钟）"""
        return self.config.get("update_interval", 30)

    def set_update_interval(self, minutes):
        """设置更新间隔"""
        if 1 <= minutes <= 1440:  # 1分钟到24小时
            self.config["update_interval"] = minutes
            self.save_config()
            return True
        return False