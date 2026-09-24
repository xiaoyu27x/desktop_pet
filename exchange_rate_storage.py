"""
汇率数据存储模块 - Excel 和 SQLite 数据库
增强版：修复导出问题，添加调试功能
"""
import os
import sqlite3
import pandas as pd
from datetime import datetime, timedelta
from openpyxl import load_workbook, Workbook
from openpyxl.chart import LineChart, Reference


class ExchangeRateStorage:
    """汇率数据存储管理器"""

    def __init__(self, db_path="exchange_rates.db", excel_path="exchange_rate.xlsx"):
        self.db_path = db_path
        self.excel_path = excel_path

        # 初始化数据库
        self._init_database()

        print("💾 汇率存储管理器已初始化")

    def _init_database(self):
        """初始化SQLite数据库"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # 创建汇率记录表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS exchange_rates (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                currency_pair TEXT NOT NULL,
                base_currency TEXT NOT NULL,
                target_currency TEXT NOT NULL,
                rate REAL NOT NULL,
                timestamp REAL NOT NULL,
                datetime TEXT NOT NULL,
                UNIQUE(currency_pair, timestamp)
            )
        ''')

        # 创建索引
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_currency_pair 
            ON exchange_rates(currency_pair)
        ''')

        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_datetime 
            ON exchange_rates(datetime)
        ''')

        conn.commit()
        conn.close()

        print("✅ 数据库初始化完成")

    def save_rate(self, currency_pair, base, target, rate, dt=None):
        """
        保存汇率数据

        Args:
            currency_pair: 货币对 (如 "USD/CNY")
            base: 基准货币
            target: 目标货币
            rate: 汇率值
            dt: 时间（datetime对象），默认当前时间
        """
        if dt is None:
            dt = datetime.now()

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute('''
                INSERT OR REPLACE INTO exchange_rates 
                (currency_pair, base_currency, target_currency, rate, timestamp, datetime)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                currency_pair,
                base,
                target,
                rate,
                dt.timestamp(),
                dt.strftime('%Y-%m-%d %H:%M:%S')
            ))

            conn.commit()
            print(f"💾 已保存: {currency_pair} = {rate:.4f} ({dt.strftime('%H:%M:%S')})")

        except Exception as e:
            print(f"❌ 保存失败: {e}")
        finally:
            conn.close()

    def get_rates(self, currency_pair, start_date=None, end_date=None):
        """
        查询汇率数据

        Args:
            currency_pair: 货币对
            start_date: 开始日期（datetime）
            end_date: 结束日期（datetime）

        Returns:
            DataFrame
        """
        conn = sqlite3.connect(self.db_path)

        query = "SELECT * FROM exchange_rates WHERE currency_pair = ?"
        params = [currency_pair]

        if start_date:
            query += " AND timestamp >= ?"
            params.append(start_date.timestamp())

        if end_date:
            query += " AND timestamp <= ?"
            params.append(end_date.timestamp())

        query += " ORDER BY timestamp ASC"

        df = pd.read_sql_query(query, conn, params=params)
        conn.close()

        return df

    def export_to_excel(self, currency_pair, period="daily"):
        """
        导出数据到Excel，并生成折线图

        Args:
            currency_pair: 货币对 (如 "USD/CNY" 或 "AUD-CNY")
            period: 时间周期 ("daily", "weekly", "monthly", "all")
        """
        # ⭐ 标准化货币对格式（支持 "/" 和 "-" 两种格式）
        currency_pair = currency_pair.replace('-', '/')

        # 计算时间范围
        now = datetime.now()

        if period == "daily":
            start_date = now - timedelta(days=1)
            sheet_name = f"{currency_pair}_今日"
        elif period == "weekly":
            start_date = now - timedelta(weeks=1)
            sheet_name = f"{currency_pair}_本周"
        elif period == "monthly":
            start_date = now - timedelta(days=30)
            sheet_name = f"{currency_pair}_本月"
        else:
            start_date = None
            sheet_name = f"{currency_pair}_全部"

        # 查询数据
        df = self.get_rates(currency_pair, start_date)

        if df.empty:
            print(f"⚠️ 没有数据可导出: {currency_pair} ({period})")
            print(f"   提示：请检查数据库中的货币对格式是否为 '{currency_pair}'")

            # ⭐ 调试信息：显示数据库中实际有哪些货币对
            self._show_available_pairs()
            return False

        print(f"📊 准备导出 {len(df)} 条记录到 Excel")

        # 处理sheet名称（Excel限制31字符）
        sheet_name = sheet_name.replace('/', '-')[:31]

        # 创建或加载Excel文件
        if os.path.exists(self.excel_path):
            wb = load_workbook(self.excel_path)
        else:
            wb = Workbook()
            # 删除默认的Sheet
            if 'Sheet' in wb.sheetnames:
                wb.remove(wb['Sheet'])

        # 如果sheet已存在，删除
        if sheet_name in wb.sheetnames:
            wb.remove(wb[sheet_name])

        # 创建新sheet
        ws = wb.create_sheet(sheet_name)

        # 写入表头
        ws.append(['时间', '汇率'])

        # 写入数据
        for _, row in df.iterrows():
            ws.append([row['datetime'], row['rate']])

        # 创建折线图
        chart = LineChart()
        chart.title = f"{currency_pair} 汇率走势 ({period})"
        chart.style = 10
        chart.y_axis.title = '汇率'
        chart.x_axis.title = '时间'

        # 数据范围
        data = Reference(ws, min_col=2, min_row=1, max_row=len(df) + 1)
        cats = Reference(ws, min_col=1, min_row=2, max_row=len(df) + 1)

        chart.add_data(data, titles_from_data=True)
        chart.set_categories(cats)

        # 添加图表
        ws.add_chart(chart, "D2")

        # 保存
        wb.save(self.excel_path)
        print(f"✅ 已导出到Excel: {sheet_name} ({len(df)}条记录)")

        return True

    def _show_available_pairs(self):
        """显示数据库中可用的货币对（调试用）"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            SELECT DISTINCT currency_pair, COUNT(*) as count
            FROM exchange_rates
            GROUP BY currency_pair
        ''')

        pairs = cursor.fetchall()
        conn.close()

        if pairs:
            print("   数据库中的货币对:")
            for pair, count in pairs:
                print(f"   - {pair} ({count}条记录)")
        else:
            print("   数据库中暂无任何数据")

    def auto_export_daily(self, currency_pair):
        """每日自动导出"""
        return self.export_to_excel(currency_pair, "daily")

    def auto_export_weekly(self, currency_pair):
        """每周自动导出"""
        return self.export_to_excel(currency_pair, "weekly")

    def auto_export_monthly(self, currency_pair):
        """每月自动导出"""
        return self.export_to_excel(currency_pair, "monthly")

    def get_latest_rate(self, currency_pair):
        """获取最新汇率"""
        # 标准化格式
        currency_pair = currency_pair.replace('-', '/')

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            SELECT rate, datetime FROM exchange_rates
            WHERE currency_pair = ?
            ORDER BY timestamp DESC
            LIMIT 1
        ''', (currency_pair,))

        result = cursor.fetchone()
        conn.close()

        if result:
            return {
                'rate': result[0],
                'datetime': result[1]
            }
        return None

    def get_statistics(self, currency_pair, days=7):
        """
        获取统计信息

        Returns:
            {min, max, avg, current}
        """
        # 标准化格式
        currency_pair = currency_pair.replace('-', '/')

        start_date = datetime.now() - timedelta(days=days)
        df = self.get_rates(currency_pair, start_date)

        if df.empty:
            return None

        return {
            'min': df['rate'].min(),
            'max': df['rate'].max(),
            'avg': df['rate'].mean(),
            'current': df['rate'].iloc[-1] if len(df) > 0 else None,
            'count': len(df)
        }

    # ========== 调试功能 ==========

    def insert_test_rate(self, currency_pair, rate=100.0):
        """
        插入测试汇率数据（用于调试提醒功能）

        Args:
            currency_pair: 货币对 (如 "USD/CNY")
            rate: 测试汇率值（默认100.0）
        """
        # 标准化格式
        currency_pair = currency_pair.replace('-', '/')

        # 提取base和target
        parts = currency_pair.split('/')
        if len(parts) != 2:
            print(f"❌ 无效的货币对格式: {currency_pair}")
            return False

        target, base = parts

        # 插入一个1分钟前的测试数据
        test_time = datetime.now() - timedelta(minutes=1)

        self.save_rate(
            currency_pair=currency_pair,
            base=base,
            target=target,
            rate=rate,
            dt=test_time
        )

        print(f"🧪 已插入测试数据: {currency_pair} = {rate} (时间: {test_time.strftime('%H:%M:%S')})")
        return True

    def clear_test_data(self, currency_pair=None):
        """
        清除测试数据

        Args:
            currency_pair: 货币对，如果为None则清除所有数据
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            if currency_pair:
                currency_pair = currency_pair.replace('-', '/')
                cursor.execute('DELETE FROM exchange_rates WHERE currency_pair = ?', (currency_pair,))
                print(f"🗑️ 已清除 {currency_pair} 的所有数据")
            else:
                cursor.execute('DELETE FROM exchange_rates')
                print(f"🗑️ 已清除所有数据")

            conn.commit()
            deleted = cursor.rowcount
            print(f"   删除了 {deleted} 条记录")

        except Exception as e:
            print(f"❌ 清除数据失败: {e}")
        finally:
            conn.close()

    def get_record_count(self, currency_pair=None):
        """
        获取记录数量

        Args:
            currency_pair: 货币对，如果为None则返回总数

        Returns:
            int: 记录数量
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            if currency_pair:
                currency_pair = currency_pair.replace('-', '/')
                cursor.execute('SELECT COUNT(*) FROM exchange_rates WHERE currency_pair = ?', (currency_pair,))
            else:
                cursor.execute('SELECT COUNT(*) FROM exchange_rates')

            count = cursor.fetchone()[0]
            return count

        except Exception as e:
            print(f"❌ 查询记录数失败: {e}")
            return 0
        finally:
            conn.close()

    def export_summary_sheet(self, currency_pairs):
        """
        导出所有历史数据总表（每个货币对一列，时间轴对齐）

        Args:
            currency_pairs: 货币对列表，支持 "/" 或 "-" 格式
        """
        # 标准化格式
        pairs = [p.replace('-', '/') for p in currency_pairs]

        # 创建或加载 Excel
        if os.path.exists(self.excel_path):
            wb = load_workbook(self.excel_path)
        else:
            wb = Workbook()
            if 'Sheet' in wb.sheetnames:
                wb.remove(wb['Sheet'])

        sheet_name = "总表_全部数据"
        if sheet_name in wb.sheetnames:
            wb.remove(wb[sheet_name])

        ws = wb.create_sheet(sheet_name, 0)  # 放在第一个位置

        # 查询每个货币对的全量数据
        all_data = {}
        all_times = set()

        for pair in pairs:
            df = self.get_rates(pair)
            if not df.empty:
                # 过滤掉测试数据（rate=100.0）
                df = df[df['rate'] != 100.0]
            if not df.empty:
                pair_data = {}
                for _, row in df.iterrows():
                    pair_data[row['datetime']] = row['rate']
                    all_times.add(row['datetime'])
                all_data[pair] = pair_data

        if not all_data:
            print("⚠️ 总表：没有任何历史数据可导出")
            wb.save(self.excel_path)
            return False

        # 按时间排序
        sorted_times = sorted(all_times)

        # 写表头：时间 + 每个货币对一列
        headers = ['时间'] + list(all_data.keys())
        ws.append(headers)

        # 写数据行
        for t in sorted_times:
            row = [t]
            for pair in all_data:
                row.append(all_data[pair].get(t, None))
            ws.append(row)

        # 生成折线图（所有货币对）
        if len(sorted_times) > 1:
            chart = LineChart()
            chart.title = "所有货币对历史走势"
            chart.style = 10
            chart.y_axis.title = '汇率'
            chart.x_axis.title = '时间'

            for col_idx, pair in enumerate(all_data.keys(), start=2):
                data = Reference(ws, min_col=col_idx, min_row=1,
                                 max_row=len(sorted_times) + 1)
                chart.add_data(data, titles_from_data=True)

            cats = Reference(ws, min_col=1, min_row=2,
                             max_row=len(sorted_times) + 1)
            chart.set_categories(cats)
            ws.add_chart(chart, "B{}".format(len(sorted_times) + 4))

        wb.save(self.excel_path)
        total = len(sorted_times)
        print(f"✅ 总表已导出: {len(all_data)} 个货币对，{total} 条时间点")
        return True

    def open_excel(self):
        """打开Excel文件"""
        if os.path.exists(self.excel_path):
            try:
                os.startfile(self.excel_path)
                print(f"📊 已打开: {self.excel_path}")
                return True
            except Exception as e:
                print(f"❌ 打开Excel失败: {e}")
                return False
        else:
            print(f"⚠️ Excel文件不存在: {self.excel_path}")
            return False