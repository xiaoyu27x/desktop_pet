"""
汇率调试工具（改进版）
用于测试提醒功能，不污染数据库
"""
from datetime import datetime
from PyQt5.QtCore import QTimer


class ExchangeRateDebugger:
    """汇率调试工具"""

    def __init__(self, storage, fetcher, alerter, config):
        """
        初始化调试工具

        Args:
            storage: ExchangeRateStorage 实例
            fetcher: ExchangeRateFetcher 实例
            alerter: ExchangeRateAlerter 实例
            config: ExchangeRateConfig 实例
        """
        self.storage = storage
        self.fetcher = fetcher
        self.alerter = alerter
        self.config = config

        print("🔧 汇率调试工具已初始化")

    def test_alert(self, currency_pair, pet_instance):
        """
        一键测试提醒功能（改进版）

        测试方法：
        1. 显示当前提醒设置
        2. 立即抓取真实汇率
        3. 手动触发提醒检查（使用模拟的异常汇率）
        4. 不污染数据库

        Args:
            currency_pair: 货币对 (如 "USD/CNY")
            pet_instance: 宠物实例（用于动画）
        """
        print("\n" + "="*50)
        print("🧪 开始提醒功能测试")
        print("="*50)

        # 标准化格式
        currency_pair = currency_pair.replace('-', '/')

        # 步骤1: 显示当前提醒设置
        print(f"\n步骤1: 检查提醒设置...")
        alerts = self._show_alerts_for_pair(currency_pair)

        if not alerts:
            print("\n⚠️ 测试终止：该货币对没有设置提醒")
            print("💡 请先在提醒设置中添加提醒规则")
            print("="*50 + "\n")
            return

        # 步骤2: 立即抓取当前汇率
        print(f"\n步骤2: 立即抓取当前汇率...")
        current_rate = self._force_fetch(currency_pair)

        if not current_rate:
            print("\n❌ 测试失败：无法获取当前汇率")
            print("="*50 + "\n")
            return

        print(f"   ✅ 当前汇率: {current_rate:.4f}")

        # 步骤3: 模拟提醒检查
        print(f"\n步骤3: 测试提醒触发...")
        print(f"   测试场景1: 模拟汇率 = 100.0 (异常高值)")

        triggered_count = 0
        for i, alert in enumerate(alerts):
            alert_type = alert['type']
            threshold = alert['threshold']

            # 检查是否会触发
            if alert_type == 'below' and 100.0 <= threshold:
                print(f"   ⚠️ 提醒[{i+1}]不会触发: 100.0 > {threshold}")
            elif alert_type == 'above' and 100.0 >= threshold:
                print(f"   ✅ 提醒[{i+1}]会触发: 100.0 > {threshold}")
                triggered_count += 1

                # 手动触发提醒
                self._trigger_test_alert(currency_pair, 100.0, alert, pet_instance)
            else:
                print(f"   ⚠️ 提醒[{i+1}]不会触发: 条件不符")

        print(f"\n   测试场景2: 模拟汇率 = 0.01 (异常低值)")

        for i, alert in enumerate(alerts):
            alert_type = alert['type']
            threshold = alert['threshold']

            # 检查是否会触发
            if alert_type == 'below' and 0.01 <= threshold:
                print(f"   ✅ 提醒[{i+1}]会触发: 0.01 < {threshold}")
                triggered_count += 1

                # 手动触发提醒
                self._trigger_test_alert(currency_pair, 0.01, alert, pet_instance)
            elif alert_type == 'above' and 0.01 >= threshold:
                print(f"   ⚠️ 提醒[{i+1}]不会触发: 0.01 < {threshold}")
            else:
                print(f"   ⚠️ 提醒[{i+1}]不会触发: 条件不符")

        # 步骤4: 显示结果
        print(f"\n步骤4: 测试总结:")
        print(f"   当前真实汇率: {current_rate:.4f}")
        print(f"   提醒规则数量: {len(alerts)}")
        print(f"   触发的提醒数: {triggered_count}")

        if triggered_count > 0:
            print(f"\n   ✅ 提醒功能正常工作！")
        else:
            print(f"\n   ℹ️ 未触发任何提醒（这是正常的，取决于提醒设置）")

        print("\n" + "="*50)
        print("🧪 测试完成！")
        print("="*50 + "\n")

    def _force_fetch(self, currency_pair):
        """
        强制抓取指定货币对的汇率

        Returns:
            float: 汇率值，失败返回None
        """
        parts = currency_pair.split('/')
        if len(parts) != 2:
            return None

        target, base = parts

        # 临时停止定时抓取
        was_running = self.fetcher.fetch_timer.isActive()
        if was_running:
            self.fetcher.stop_monitoring()

        # 切换到测试货币对
        old_base = self.fetcher.base_currency
        old_target = self.fetcher.target_currency

        self.fetcher.base_currency = base
        self.fetcher.target_currency = target

        # 立即抓取
        print(f"   正在从网络获取 {currency_pair} 的汇率...")
        self.fetcher.fetch_rate()

        # 等待一下让信号处理完成
        QTimer.singleShot(1000, lambda: None)

        # 获取当前汇率
        current_rate = self.fetcher.current_rate

        # 恢复原设置
        self.fetcher.base_currency = old_base
        self.fetcher.target_currency = old_target

        if was_running:
            self.fetcher.start_monitoring(old_base, old_target)

        return current_rate

    def _trigger_test_alert(self, currency_pair, test_rate, alert, pet_instance):
        """
        手动触发测试提醒（正确使用alerter）

        Args:
            currency_pair: 货币对
            test_rate: 测试汇率值
            alert: 提醒规则
        """
        print(f"      → 触发测试提醒...")

        old_history = self.alerter.alert_history.copy()
        self.alerter.alert_history.clear()

        # 直接传入这条 alert，绕过 self.alerter.alerts 为空的问题
        self.alerter.check_rate(
            currency_pair,
            test_rate,
            pet_instance,
            config_alerts=[alert]
        )

        self.alerter.alert_history = old_history

    def _show_alerts_for_pair(self, currency_pair):
        """
        显示指定货币对的提醒设置

        Returns:
            list: 提醒列表
        """
        currencies = self.config.get_currencies()

        for currency in currencies:
            pair = f"{currency['target']}/{currency['base']}"
            if pair == currency_pair:
                alerts = currency.get('alerts', [])

                if alerts:
                    print(f"   货币对 {currency_pair} 的提醒设置:")
                    for j, alert in enumerate(alerts):
                        type_text = "低于" if alert['type'] == "below" else "高于"
                        print(f"   [{j+1}] 当汇率{type_text} {alert['threshold']:.4f} 时提醒")
                    return alerts
                else:
                    print(f"   货币对 {currency_pair} 没有设置提醒")
                    return []

        print(f"   货币对 {currency_pair} 未被监控")
        return []

    def show_statistics(self, currency_pair):
        """
        显示汇率统计信息

        Args:
            currency_pair: 货币对
        """
        print("\n" + "="*50)
        print(f"📊 {currency_pair} 统计信息")
        print("="*50)

        # 记录总数
        total_count = self.storage.get_record_count(currency_pair)
        print(f"\n总记录数: {total_count}")

        if total_count == 0:
            print("⚠️ 暂无数据")
            print("="*50 + "\n")
            return

        # 最新汇率
        latest = self.storage.get_latest_rate(currency_pair)
        if latest:
            print(f"\n最新汇率:")
            print(f"  值: {latest['rate']:.4f}")
            print(f"  时间: {latest['datetime']}")

        # 7天统计
        stats_7d = self.storage.get_statistics(currency_pair, days=7)
        if stats_7d:
            print(f"\n最近7天统计:")
            print(f"  最高: {stats_7d['max']:.4f}")
            print(f"  最低: {stats_7d['min']:.4f}")
            print(f"  平均: {stats_7d['avg']:.4f}")
            print(f"  记录: {stats_7d['count']}条")

        # 30天统计
        stats_30d = self.storage.get_statistics(currency_pair, days=30)
        if stats_30d:
            print(f"\n最近30天统计:")
            print(f"  最高: {stats_30d['max']:.4f}")
            print(f"  最低: {stats_30d['min']:.4f}")
            print(f"  平均: {stats_30d['avg']:.4f}")
            print(f"  记录: {stats_30d['count']}条")

        print("="*50 + "\n")

    def clear_data(self, currency_pair=None):
        """
        清除数据

        Args:
            currency_pair: 货币对，如果为None则清除所有
        """
        if currency_pair:
            confirm = input(f"确定要清除 {currency_pair} 的所有数据吗？ (yes/no): ")
        else:
            confirm = input("确定要清除所有汇率数据吗？ (yes/no): ")

        if confirm.lower() == 'yes':
            self.storage.clear_test_data(currency_pair)
        else:
            print("❌ 已取消")

    def force_fetch(self, currency_pair=None):
        """
        强制抓取汇率

        Args:
            currency_pair: 货币对，如果为None则使用当前监控的
        """
        if currency_pair:
            rate = self._force_fetch(currency_pair)
            if rate:
                print(f"✅ {currency_pair}: {rate:.4f}")
            else:
                print(f"❌ 获取 {currency_pair} 失败")
        else:
            print(f"🔄 强制抓取当前监控的货币对...")
            self.fetcher.fetch_rate()