"""
现汇抓取模块 - 中国银行实时汇率抓取
"""
import requests
import json
import time
from datetime import datetime
from PyQt5.QtCore import QTimer, QObject, pyqtSignal
from bs4 import BeautifulSoup


class ExchangeRateFetcher(QObject):
    """汇率抓取器"""

    # 信号
    rate_updated = pyqtSignal(dict)  # 汇率更新信号 {currency_pair, rate, time}
    fetch_error = pyqtSignal(str)  # 抓取错误信号

    # 中国银行汇率URL
    BOC_URL = "https://www.boc.cn/sourcedb/whpj/"

    # 常用货币代码映射
    CURRENCY_MAP = {
        "美元": "USD",
        "欧元": "EUR",
        "日元": "JPY",
        "港币": "HKD",
        "英镑": "GBP",
        "澳元": "AUD",
        "加元": "CAD",
        "瑞士法郎": "CHF",
        "新加坡元": "SGD",
        "韩元": "KRW",
        "泰铢": "THB",
        "新西兰元": "NZD",
        "人民币": "CNY"
    }

    def __init__(self):
        super().__init__()

        # 当前监控的货币对
        self.base_currency = "CNY"  # 基准货币（人民币）
        self.target_currency = "USD"  # 目标货币（美元）

        # 抓取定时器（30分钟一次）
        self.fetch_timer = QTimer()
        self.fetch_timer.timeout.connect(self.fetch_rate)
        self.fetch_interval = 30 * 60 * 1000  # 30分钟（毫秒）

        # 历史汇率数据（用于绘图）
        self.rate_history = []  # [{time, rate}, ...]

        # 当前汇率
        self.current_rate = None

        print("💱 汇率抓取器已初始化")

    def start_monitoring(self, base="CNY", target="USD"):
        """
        开始监控汇率

        Args:
            base: 基准货币
            target: 目标货币
        """
        self.base_currency = base
        self.target_currency = target

        # 立即抓取一次
        self.fetch_rate()

        # 启动定时器
        self.fetch_timer.start(self.fetch_interval)

        print(f"✅ 开始监控汇率: {target}/{base}")

    def stop_monitoring(self):
        """停止监控"""
        self.fetch_timer.stop()
        print("⏹️ 汇率监控已停止")

    def fetch_rate(self):
        """抓取当前汇率"""
        try:
            # 构建货币对
            currency_pair = f"{self.target_currency}/{self.base_currency}"

            # 抓取汇率
            rate = self._fetch_from_boc()

            if rate:
                # 记录当前汇率
                self.current_rate = rate

                # 添加到历史记录
                now = datetime.now()
                self.rate_history.append({
                    "time": now,
                    "rate": rate,
                    "timestamp": now.timestamp()
                })

                # 发送更新信号
                self.rate_updated.emit({
                    "currency_pair": currency_pair,
                    "rate": rate,
                    "time": now,
                    "base": self.base_currency,
                    "target": self.target_currency
                })

                print(f"💱 {currency_pair}: {rate:.4f} ({now.strftime('%H:%M:%S')})")

            else:
                self.fetch_error.emit("无法获取汇率数据")

        except Exception as e:
            error_msg = f"抓取汇率失败: {str(e)}"
            print(f"❌ {error_msg}")
            self.fetch_error.emit(error_msg)

    def _fetch_from_boc(self):
        """
        从中国银行抓取汇率
        返回: 汇率值（float）或 None
        """
        try:
            # 中国银行外汇牌价页面
            url = "https://www.boc.cn/sourcedb/whpj/index.html"

            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }

            response = requests.get(url, headers=headers, timeout=10)
            response.encoding = 'utf-8'

            if response.status_code == 200:
                # 解析HTML
                soup = BeautifulSoup(response.text, 'html.parser')

                # 查找表格
                table = soup.find('table')

                if table:
                    rows = table.find_all('tr')

                    for row in rows[1:]:  # 跳过表头
                        cols = row.find_all('td')

                        if len(cols) >= 6:
                            # 货币名称
                            currency_name = cols[0].get_text(strip=True)

                            # 检查是否是目标货币
                            if self._is_target_currency(currency_name):
                                # 现汇买入价（索引可能需要调整）
                                try:
                                    # 通常是现汇买入价或中间价
                                    buying_rate = cols[1].get_text(strip=True)

                                    # 转换为浮点数
                                    rate = float(buying_rate)

                                    return rate

                                except (ValueError, IndexError):
                                    continue

                # 如果网页解析失败，使用备用API
                return self._fetch_from_api()

            else:
                return self._fetch_from_api()

        except Exception as e:
            print(f"⚠️ 从中行网站抓取失败: {e}")
            return self._fetch_from_api()

    def _fetch_from_api(self):
        """
        备用方案：从汇率API获取
        可以使用 exchangerate-api.com 或其他免费API
        """
        try:
            # 使用免费的汇率API
            api_url = f"https://api.exchangerate-api.com/v4/latest/{self.base_currency}"

            response = requests.get(api_url, timeout=10)

            if response.status_code == 200:
                data = response.json()

                if self.target_currency in data['rates']:
                    rate = data['rates'][self.target_currency]

                    # 如果基准是CNY，需要取倒数
                    if self.base_currency == "CNY":
                        return 1 / rate
                    else:
                        return rate

            return None

        except Exception as e:
            print(f"⚠️ API抓取失败: {e}")
            return None

    def _is_target_currency(self, currency_name):
        """检查是否是目标货币"""
        # 移除空格和特殊字符
        currency_name = currency_name.strip()

        # 检查货币映射
        for cn_name, code in self.CURRENCY_MAP.items():
            if cn_name in currency_name and code == self.target_currency:
                return True

        return False

    def get_history(self, hours=24):
        """
        获取历史数据

        Args:
            hours: 获取最近几小时的数据

        Returns:
            [{time, rate}, ...]
        """
        if not self.rate_history:
            return []

        # 计算时间范围
        cutoff_time = datetime.now().timestamp() - (hours * 3600)

        # 过滤历史数据
        filtered = [
            item for item in self.rate_history
            if item['timestamp'] >= cutoff_time
        ]

        return filtered

    def get_current_rate(self):
        """获取当前汇率"""
        return self.current_rate

    def clear_history(self):
        """清空历史数据"""
        self.rate_history.clear()
        print("🗑️ 汇率历史已清空")

    def change_currency_pair(self, base, target):
        """
        切换货币对

        Args:
            base: 基准货币
            target: 目标货币
        """
        # 停止当前监控
        self.stop_monitoring()

        # 清空历史（切换货币对时）
        self.clear_history()

        # 开始新的监控
        self.start_monitoring(base, target)

    @staticmethod
    def get_available_currencies():
        """获取可用的货币列表"""
        return list(ExchangeRateFetcher.CURRENCY_MAP.values())

    @staticmethod
    def get_currency_name(code):
        """根据代码获取中文名称"""
        for cn_name, currency_code in ExchangeRateFetcher.CURRENCY_MAP.items():
            if currency_code == code:
                return cn_name
        return code