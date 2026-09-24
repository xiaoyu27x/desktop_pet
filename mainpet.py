import sys
import subprocess
import random
import os
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QMenu, QAction,
    QFileDialog, QDialog, QMessageBox
)
from PyQt5.QtCore import QTimer, Qt, QTime
from PyQt5.QtGui import QPixmap, QFont, QCursor

# 导入模块
from pet_movement import MovementManager
from pet_animation import AnimationManager
from pet_interaction import InteractionHandler
from pet_window_detector import WindowDetector
from task_managers import TaskHistoryManager, ShortcutManager
from shortcut_ui import ShortcutDialog
from settings_manager import SettingsManager
from task_scheduler import TaskScheduler
from task_ui import TaskSetupDialog, TaskListDialog
from tray_manager import TrayManager
from pomodoro_timer import PomodoroTimer
from pomodoro_ui import PomodoroSetupDialog, PomodoroDisplay
from music_player import MusicPlayer
from music_ui import MusicPlayerDialog
from exchange_rate_config import ExchangeRateConfig
from exchange_rate_display import ExchangeRateDisplay
from exchange_rate_settings import CurrencySettingsDialog, AlertSettingsDialog
from time_display import TimeDisplay
from exchange_rate_fetcher import ExchangeRateFetcher
from exchange_rate_storage import ExchangeRateStorage
from exchange_rate_alerter import ExchangeRateAlerter
from create_tray_icon import create_tray_icon
from exchange_rate_debugger import ExchangeRateDebugger

# 导入全局快捷键库
try:
    import keyboard

    HAS_KEYBOARD = True
except ImportError:
    HAS_KEYBOARD = False
    print("⚠️ 未安装 keyboard 库，快捷键召唤功能将不可用")
    print("安装方法: pip install keyboard")


class DesktopPet(QWidget):
    def __init__(self):
        super().__init__()

        # 窗口设置
        self.setWindowFlags(
            Qt.FramelessWindowHint |
            Qt.WindowStaysOnTopHint |
            Qt.Tool |
            Qt.X11BypassWindowManagerHint
        )
        self.setAttribute(Qt.WA_TranslucentBackground)

        # 基础属性
        self.pet_width = 190
        self.pet_height = 190
        self.x = 0
        self.y = 0
        self.resize(self.pet_width, self.pet_height)

        # 初始化位置
        screen_geometry = QApplication.primaryScreen().geometry()
        self.x = random.randint(0, screen_geometry.width() - self.pet_width)
        self.y = random.randint(0, screen_geometry.height() - self.pet_height)
        self.move(self.x, self.y)

        # 创建标签并加载图片
        self.pet_label = QLabel(self)
        self.pet_label.setGeometry(0, 25, self.pet_width-50, self.pet_height-50)
        self.pet_label.setAlignment(Qt.AlignCenter)
        self.load_pet_image()

        # 报时标签 - 常驻显示，米白色底，深棕色字
        self.time_label = QLabel(self)
        self.time_label.setGeometry(25, 0, self.pet_width-50, 30)
        self.time_label.setAlignment(Qt.AlignCenter)
        self.time_label.setStyleSheet("""
            background-color: #F5F5DC;
            color: #5D4037;
            border: 1px solid #D2B48C;
            border-radius: 5px;
            padding: 2px;
            font-weight: bold;
        """)
        self.time_label.setFont(QFont("Arial", 12))
        self.time_label.show()

        # ⭐ 新增：配置管理器
        self.exchange_config = ExchangeRateConfig()

        # ⭐ 新增：报时组件包装器（在 time_label 创建之后）
        # 注意：time_label 必须已经创建（第 69-81 行）
        self.time_display = TimeDisplay(self, self.exchange_config)

        # # ⭐ 新增：汇率系统
        # self.exchange_fetcher = ExchangeRateFetcher()
        # self.exchange_storage = ExchangeRateStorage()
        # self.exchange_alerter = ExchangeRateAlerter()
        # self.exchange_display = ExchangeRateDisplay(self)
        #
        # # 连接汇率信号
        # self.exchange_fetcher.rate_updated.connect(self.on_exchange_rate_updated)
        # self.exchange_alerter.alert_triggered.connect(self.on_exchange_alert)
        # 创建管理器
        self.movement = MovementManager(self)
        self.animation = AnimationManager(self)
        self.interaction = InteractionHandler(self)
        self.window_detector = WindowDetector(self)

        # ⭐ 汇率监控系统
        self.exchange_config = ExchangeRateConfig()
        self.exchange_display = ExchangeRateDisplay(self)  # ✅ 注意：新版本不需要传 config
        self.exchange_fetcher = ExchangeRateFetcher()
        self.exchange_storage = ExchangeRateStorage()
        self.exchange_alerter = ExchangeRateAlerter()

        # 连接信号
        self.exchange_display.currency_clicked.connect(self.open_currency_settings)
        self.exchange_display.alert_clicked.connect(self.open_alert_settings)
        self.exchange_display.excel_clicked.connect(self.export_exchange_excel)
        self.exchange_fetcher.rate_updated.connect(self.on_exchange_rate_updated)
        self.exchange_alerter.alert_triggered.connect(self.on_exchange_alert)

        # ⭐ 新增：统一配置管理器
        self.settings_manager = SettingsManager()


        # 关键：新增管理器
        self.history_manager = TaskHistoryManager()
        self.shortcut_manager = ShortcutManager()

        # ⭐ 新增：任务调度器
        self.task_scheduler = TaskScheduler()

        # 关联窗口检测器
        self.movement.window_detector = self.window_detector

        # ⭐ 加载保存的碰撞边距设置
        saved_margin = self.settings_manager.get_collision_margin()
        self.movement.collision_margin = saved_margin
        print(f"✅ 已加载碰撞边距设置: {saved_margin}px")

        # ⭐ 加载窗口避让开关状态
        window_avoidance_enabled = self.settings_manager.get_window_avoidance()
        if window_avoidance_enabled:
            self.window_detector.update_timer.start(500)
            print(f"✅ 已启用窗口避让功能")
        else:
            self.window_detector.update_timer.stop()
            print(f"ℹ️ 窗口避让功能已关闭")

        # 图片加载后保存原始图片
        QTimer.singleShot(100, self._save_original_image)

        # 汇率监控：不在启动时自动请求，等用户主动打开组件时再启动
        self._exchange_monitoring_started = False

        # 启动移动
        self.movement.start_moving()

        # 启动移动
        self.movement.start_moving()

        # 定时任务相关
        self.last_reported_minute = -1

        self.global_check_timer = QTimer(self)
        self.global_check_timer.timeout.connect(self.check_time_events)
        self.global_check_timer.start(1000)

        # 初始化全局快捷键
        self.current_hotkey = self.shortcut_manager.load_shortcut()
        if HAS_KEYBOARD:
            self.register_global_hotkey()

        self.report_time(QTime.currentTime().toString("HH:mm"))

        # ⭐ 新增：番茄钟功能
        self.pomodoro_timer = PomodoroTimer()
        self.pomodoro_display = PomodoroDisplay(self)

        # 连接番茄钟信号
        self.pomodoro_timer.time_updated.connect(self.on_pomodoro_tick)
        self.pomodoro_timer.timer_completed.connect(self.on_pomodoro_complete)
        self.pomodoro_timer.round_changed.connect(self.on_pomodoro_round_changed)

        # ⭐ 新增：音乐播放器
        self.music_player = MusicPlayer()

        # 汇率系统
        self.exchange_config = ExchangeRateConfig()
        self.exchange_display = ExchangeRateDisplay(self)
        self.exchange_fetcher = ExchangeRateFetcher()
        self.exchange_storage = ExchangeRateStorage()  # 使用新版本
        self.exchange_alerter = ExchangeRateAlerter()

        # ⭐ 初始化调试器
        self.exchange_debugger = ExchangeRateDebugger(
            self.exchange_storage,
            self.exchange_fetcher,
            self.exchange_alerter,
            self.exchange_config
        )

        # 连接信号
        self.exchange_display.currency_clicked.connect(self.open_currency_settings)
        self.exchange_display.alert_clicked.connect(self.open_alert_settings)
        self.exchange_display.excel_clicked.connect(self.export_exchange_excel)
        self.exchange_display.debug_clicked.connect(self.run_debug_test)
        self.exchange_fetcher.rate_updated.connect(self.on_exchange_rate_updated)    # ⭐ 补上
        self.exchange_alerter.alert_triggered.connect(self.on_exchange_alert)        # ⭐ 补上


        # ⭐ 新增：创建系统托盘（放在最后）
        self.tray_manager = TrayManager(self)
        self.tray_manager.create_tray_icon()

    def _save_original_image(self):
        """延迟保存原始图片"""
        if hasattr(self, 'animation'):
            self.animation.save_original_pixmap()

    def load_pet_image(self):
        """加载宠物图片"""
        # 优先从加密包读取，回退到文件系统
        try:
            from resource_loader import res
            image_keys = [
                'resources/pet2.png',
                'resources/pet.png',
                'resources/pet.jpg',
                'resources/pet.gif',
            ]
            for key in image_keys:
                try:
                    pixmap = res.qpixmap(key)
                    if not pixmap.isNull():
                        pixmap = pixmap.scaled(
                            self.pet_width, self.pet_height,
                            Qt.KeepAspectRatio, Qt.SmoothTransformation
                        )
                        self.pet_label.setAlignment(Qt.AlignCenter)
                        self.pet_label.setPixmap(pixmap)
                        print(f"✅ 成功加载图片: {key}")
                        create_tray_icon()
                        return
                except Exception:
                    continue
        except ImportError:
            pass

        # 回退：直接从文件系统加载
        for image_file in [
            'resources/pet2.png', 'resources/pet.png',
            'resources/pet.jpg', 'resources/pet.gif',
            'pet2.png', 'pet.png', 'pet.jpg', 'pet.gif',
        ]:
            if os.path.exists(image_file):
                pixmap = QPixmap(image_file)
                if not pixmap.isNull():
                    pixmap = pixmap.scaled(
                        self.pet_width, self.pet_height,
                        Qt.KeepAspectRatio, Qt.SmoothTransformation
                    )
                    self.pet_label.setAlignment(Qt.AlignCenter)
                    self.pet_label.setPixmap(pixmap)
                    print(f"✅ 成功加载图片（文件系统）: {image_file}")
                    create_tray_icon()
                    return

        print("⚠️ 未找到宠物图片，使用默认占位符")
        self.create_placeholder()

    def create_placeholder(self):
        """创建占位符"""
        from PyQt5.QtGui import QPainter, QBrush, QColor, QPen

        pixmap = QPixmap(self.pet_width, self.pet_height)
        pixmap.fill(Qt.transparent)

        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setBrush(QBrush(QColor(100, 150, 255, 200)))
        painter.setPen(QPen(QColor(50, 100, 200), 2))
        painter.drawEllipse(10, 10, 120, 120)
        painter.end()

        self.pet_label.setAlignment(Qt.AlignCenter)
        self.pet_label.setPixmap(pixmap)

    def _init_exchange_monitoring(self, restart=False):
        """初始化汇率监控（懒加载，只在第一次调用时真正启动）"""
        if self._exchange_monitoring_started and not restart:
            return  # 已经启动过，直接返回

        # 获取启用的币种
        currencies = self.exchange_config.get_enabled_currencies()

        if currencies:
            currency = currencies[0]
            self.exchange_fetcher.start_monitoring(
                currency['base'],
                currency['target']
            )
            self._exchange_monitoring_started = True
            print(f"📊 开始监控: {currency['target']}/{currency['base']}")

            if len(currencies) > 1:
                print(f"⚠️ 注意：当前只能同时监控一个货币对")
                print(f"   其他 {len(currencies) - 1} 个币种将不会自动更新")

            if self.exchange_config.is_widget_visible():
                self.exchange_display.show_widget()
        else:
            print("⚠️ 没有启用的货币对，汇率监控未启动")

    def open_currency_settings(self):
        """打开币种设置对话框"""
        dialog = CurrencySettingsDialog(self.exchange_config, self)
        if dialog.exec_():
            # 设置已保存，重新开始监控（切换新币种）
            self._init_exchange_monitoring(restart=True)

    def open_alert_settings(self):
        """打开提醒设置对话框"""
        dialog = AlertSettingsDialog(self.exchange_config, self)
        dialog.exec_()

    def export_exchange_excel(self):
        """导出Excel"""
        currencies = self.exchange_config.get_enabled_currencies()

        if not currencies:
            QMessageBox.warning(self, "提示", "没有启用的币种")
            return

        # 导出所有币种
        for currency in currencies:
            currency_pair = f"{currency['target']}-{currency['base']}"
            self.exchange_storage.export_to_excel(currency_pair, "daily")

        # 打开Excel
        if self.exchange_storage.open_excel():
            QMessageBox.information(self, "成功", "Excel已导出并打开")
        else:
            QMessageBox.information(self, "成功", "数据已导出到 exchange_rate.xlsx")

    def check_time_events(self):
        """时间事件检查逻辑 - 更新为使用新调度器"""
        now = QTime.currentTime()
        curr_min = now.minute()
        curr_sec = now.second()

        # 每分钟报时
        if curr_min != self.last_reported_minute and curr_sec == 0:
            self.report_time(now.toString("HH:mm"))
            self.last_reported_minute = curr_min

        # ⭐ 使用新的任务调度器检查待执行任务
        if curr_sec == 0:  # 每分钟的第0秒检查
            pending_tasks = self.task_scheduler.get_pending_tasks(now)
            for task_index, task in pending_tasks:
                self.execute_scheduled_task(task, task_index)

    def execute_scheduled_task(self, task, task_index):
        """执行定时任务并记录历史"""
        path = task["path"]
        name = task["name"]

        # 检查路径是否存在
        if not os.path.exists(path):
            print(f"❌ 路径不存在: {path}")
            self.history_manager.record_launch(name, path)
            QMessageBox.warning(self, "启动失败", f"文件不存在:\n{path}")
            return False

        # 尝试启动
        try:
            os.startfile(path)
            print(f"✅ 已启动: {name}")
            self.history_manager.record_launch(name, path)

            # ⭐ 标记任务为已执行
            self.task_scheduler.mark_executed(task_index)
            return True
        except Exception as e:
            print(f"❌ 启动失败: {e}")
            self.history_manager.record_launch(name, path)
            QMessageBox.warning(self, "启动失败", f"无法启动:\n{str(e)}")
            return False

    # def report_time(self, time_str):
    #     """显示报时信息并执行动画 - 常驻显示"""
    #     self.time_label.setText(time_str)
    #
    #     # ⭐ 修改：如果宠物未暂停，才执行报时动画
    #     if hasattr(self, 'animation') and not self.animation.is_playing:
    #         if hasattr(self, 'interaction') and not self.interaction.is_paused:
    #             self.animation.stretch_on_click()

    def report_time(self, time_str):
        """显示报时信息并执行动画"""
        # ⭐ 更新报时组件
        if hasattr(self, 'time_display'):
            self.time_display.update_time(time_str)

        # 执行动画
        if hasattr(self, 'animation') and not self.animation.is_playing:
            if hasattr(self, 'interaction') and not self.interaction.is_paused:
                self.animation.stretch_on_click()

    # ============ 全局快捷键功能 ============

    def register_global_hotkey(self):
        """注册全局快捷键"""
        if not HAS_KEYBOARD:
            return

        try:
            try:
                keyboard.unhook_all_hotkeys()
            except:
                keyboard.unhook_all()

            keyboard.add_hotkey(
                self.current_hotkey,
                self.summon_to_mouse,
                suppress=False,
                trigger_on_release=False
            )
            print(f"✅ 已注册快捷键: {self.current_hotkey}")
        except AttributeError as e:
            print(f"⚠️ keyboard 库版本不兼容，使用备用方法")
            try:
                keyboard.add_hotkey(self.current_hotkey, self.summon_to_mouse)
                print(f"✅ 已注册快捷键（备用方法）: {self.current_hotkey}")
            except Exception as e2:
                print(f"❌ 快捷键注册失败: {e2}")
                print("💡 建议：以管理员身份运行程序")
        except Exception as e:
            print(f"❌ 快捷键注册失败: {e}")
            print("💡 建议：")
            print("   1. 以管理员身份运行")
            print("   2. 或卸载重装 keyboard 库: pip install --upgrade keyboard")

    def summon_to_mouse(self):
        """召唤到鼠标位置并弹跳"""
        cursor_pos = QCursor.pos()

        target_x = cursor_pos.x() - self.pet_width // 2
        target_y = cursor_pos.y() - self.pet_height // 2

        self.update_position(target_x, target_y)

        if hasattr(self, 'animation') and not self.animation.is_playing:
            self.animation.stretch_on_click()

        print(f"🐾 召唤到: ({target_x}, {target_y})")

    def open_shortcut_setting(self):
        """打开快捷键设置对话框"""
        if not HAS_KEYBOARD:
            QMessageBox.warning(
                self,
                "功能不可用",
                "未安装 keyboard 库\n\n安装方法:\npip install keyboard"
            )
            return

        dlg = ShortcutDialog(self.current_hotkey, self)
        if dlg.exec_() == QDialog.Accepted:
            new_key = dlg.current_key
            self.shortcut_manager.save_shortcut(new_key)
            self.current_hotkey = new_key

            self.register_global_hotkey()

            QMessageBox.information(
                self,
                "设置成功",
                f"快捷键已更新为:\n{new_key}\n\n现在可以使用此快捷键召唤宠物了！"
            )

    # ============ 鼠标事件 ============

    # def mousePressEvent(self, event):
    #     if event.button() == Qt.LeftButton:
    #         if hasattr(self, 'interaction'):
    #             self.interaction.handle_mouse_press(event, self)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            # --- 保持原有的交互逻辑 ---
            if hasattr(self, 'interaction'):
                self.interaction.handle_mouse_press(event, self)

            # --- 修复拖动逻辑：记录鼠标点击点与窗口左上角的偏移 ---
            # 统一使用 self.drag_position 避开与 update_position 方法重名
            self.drag_position = event.globalPos() - self.pos()

            event.accept()
            self.setCursor(QCursor(Qt.OpenHandCursor))

    def mouseMoveEvent(self, event):
        """鼠标移动 - 拖动窗口"""
        if event.buttons() == Qt.LeftButton:
            # 移动宠物
            self.move(event.globalPos() - self.drag_position)

            # ⭐ 同步更新所有组件位置
            if hasattr(self, 'pomodoro_display'):
                self.pomodoro_display.update_position()

            if hasattr(self, 'exchange_display'):
                self.exchange_display.update_position()

            event.accept()



    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            if hasattr(self, 'interaction'):
                self.interaction.handle_mouse_release(event, self)

    def mouseDoubleClickEvent(self, event):
        """⭐ 处理双击事件"""
        if event.button() == Qt.LeftButton:
            if hasattr(self, 'interaction'):
                self.interaction.handle_double_click(event, self)

    def update_position(self, x, y):
        """位置更新方法"""
        self.x = x
        self.y = y
        self.move(int(x), int(y))

        # ⭐ 同时更新番茄钟位置
        if hasattr(self, 'pomodoro_display') and self.pomodoro_display.is_visible:
            self.pomodoro_display.update_position()

    def move(self, *args):
        """重写move方法，确保内部坐标同步"""
        super().move(*args)
        if len(args) == 1:
            self.x = args[0].x()
            self.y = args[0].y()
        elif len(args) == 2:
            self.x = args[0]
            self.y = args[1]

        # ⭐ 同时更新番茄钟位置
        if hasattr(self, 'pomodoro_display') and self.pomodoro_display.is_visible:
            self.pomodoro_display.update_position()

        # ⭐ 新增：更新汇率组件位置
        if hasattr(self, 'exchange_display') and self.exchange_display.is_visible:
            self.exchange_display.update_position()


    # ============ 右键菜单 ============

    def contextMenuEvent(self, event):
        """右键菜单"""
        menu = QMenu(self)

        # === 隐藏宠物 ===
        hide_action = QAction("👻 隐藏宠物", self)
        hide_action.triggered.connect(self.hide_to_tray)
        menu.addAction(hide_action)

        menu.addSeparator()

        # === 快捷键召唤 ===
        hotkey_action = QAction("⌨️ 设置召唤快捷键", self)
        hotkey_action.triggered.connect(self.open_shortcut_setting)
        menu.addAction(hotkey_action)

        menu.addSeparator()

        # === 番茄钟 ===
        pomodoro_action = QAction("🍅 番茄钟", self)
        pomodoro_action.triggered.connect(self.start_pomodoro)
        menu.addAction(pomodoro_action)

        menu.addSeparator()

        # === 定时任务 ===
        timer_action = QAction("⏰ 定时开启软件", self)
        timer_action.triggered.connect(self.setup_timer_task)
        menu.addAction(timer_action)

        view_tasks_action = QAction("📋 查看定时任务", self)
        view_tasks_action.triggered.connect(self.view_scheduled_tasks)
        menu.addAction(view_tasks_action)

        history_action = QAction("📜 启动历史记录", self)
        history_action.triggered.connect(self.view_launch_history)
        menu.addAction(history_action)

        menu.addSeparator()

        # ⭐ 音乐播放器
        music_action = QAction("🎵 音乐播放器", self)
        music_action.triggered.connect(self.open_music_player)
        menu.addAction(music_action)

        menu.addSeparator()

        # ⭐ 汇率监控
        # 汇率监控
        if hasattr(self, 'exchange_display'):
            if self.exchange_display.is_visible:
                exchange_action = QAction("❌ 隐藏汇率", self)
                exchange_action.triggered.connect(self.exchange_display.hide_widget)
            else:
                exchange_action = QAction("💱 显示汇率", self)
                exchange_action.triggered.connect(self.show_exchange_widget)
            menu.addAction(exchange_action)

        menu.addSeparator()

        # 报时组件
        if hasattr(self, 'time_display'):
            if self.time_display.is_visible:
                time_action = QAction("❌ 隐藏报时", self)
                time_action.triggered.connect(self.toggle_time_widget)
            else:
                time_action = QAction("🕐 显示报时", self)
                time_action.triggered.connect(self.toggle_time_widget)
            menu.addAction(time_action)

        menu.addSeparator()

        # === 窗口避让 ===
        avoid_window_action = QAction("窗口避让", self)
        avoid_window_action.setCheckable(True)
        if hasattr(self, 'window_detector'):
            avoid_window_action.setChecked(self.window_detector.update_timer.isActive())
        avoid_window_action.triggered.connect(self.toggle_window_avoidance)
        menu.addAction(avoid_window_action)

        # === 碰撞距离 ===
        if hasattr(self, 'movement'):
            collision_menu = menu.addMenu("碰撞距离")
            current_margin = self.movement.collision_margin

            current_action = QAction(f"当前: {current_margin}px", self)
            current_action.setEnabled(False)
            collision_menu.addAction(current_action)
            collision_menu.addSeparator()

            for margin, label in [(10, "很近"), (15, "近"), (20, "默认"), (25, "远"), (30, "很远")]:
                action = QAction(f"{label} ({margin}px)", self)
                action.setCheckable(True)
                if margin == current_margin:
                    action.setChecked(True)
                action.triggered.connect(lambda checked, m=margin: self.set_collision_margin(m))
                collision_menu.addAction(action)

        menu.addSeparator()

        # === 其他 ===
        reload_action = QAction("重新加载图片", self)
        reload_action.triggered.connect(self.load_pet_image)
        menu.addAction(reload_action)

        # ⭐ 重启选项
        menu.addSeparator()
        restart_action = QAction("重启", self)
        restart_action.triggered.connect(self.restart_application)
        menu.addAction(restart_action)

        menu.addSeparator()
        # 退出
        exit_action = QAction("退出", self)
        exit_action.triggered.connect(self.closeEvent)
        menu.addAction(exit_action)

        menu.exec_(event.globalPos())

    # ============ 定时任务功能 - 更新为新版本 ============

    def setup_timer_task(self):
        """设置定时任务 - 使用新UI"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "选择要定时开启的软件",
            "",
            "可执行文件 (*.exe);;所有文件 (*)"
        )
        if not file_path:
            return

        dlg = TaskSetupDialog(file_path, self)
        if dlg.exec_() == QDialog.Accepted:
            task_info = dlg.get_task_info()

            self.task_scheduler.add_task(
                name=task_info["name"],
                path=task_info["path"],
                time_str=task_info["time"],
                task_type=task_info["type"],
                weekday=task_info["weekday"]
            )

            type_names = {
                "once": "一次性",
                "daily": "每天重复",
                "weekly": "每周重复"
            }

            print(f"✅ 已添加{type_names[task_info['type']]}任务: {task_info['time']} 启动 {task_info['name']}")

    def view_scheduled_tasks(self):
        """查看定时任务列表 - 使用新UI"""
        dlg = TaskListDialog(self.task_scheduler, self)
        dlg.exec_()

    def view_launch_history(self):
        """查看启动历史记录"""
        history = self.history_manager.load_history()

        from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QListWidget, QListWidgetItem, QPushButton

        dlg = QDialog(self)
        dlg.setWindowTitle("📜 启动历史记录")
        dlg.setMinimumSize(600, 400)

        layout = QVBoxLayout()

        title_label = QLabel(f"共 {len(history)} 条记录")
        title_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        layout.addWidget(title_label)

        history_list = QListWidget()

        if not history:
            item = QListWidgetItem("🔭 暂无历史记录")
            item.setFlags(Qt.NoItemFlags)
            history_list.addItem(item)
        else:
            for record in reversed(history):
                time_str = record.get("时间", "未知")
                name = record.get("任务名", "未知")
                status = record.get("执行状态", "未知")

                icon = "✅" if status == "成功" else "❌"
                text = f"{icon} {time_str} | {name} | {status}"

                item = QListWidgetItem(text)
                history_list.addItem(item)

        layout.addWidget(history_list)

        btn_layout = QHBoxLayout()
        btn_clear = QPushButton("🗑️ 清空历史")
        btn_clear.clicked.connect(lambda: self.clear_history(dlg))
        btn_close = QPushButton("关闭")
        btn_close.clicked.connect(dlg.close)

        btn_layout.addWidget(btn_clear)
        btn_layout.addWidget(btn_close)

        layout.addLayout(btn_layout)
        dlg.setLayout(layout)
        dlg.exec_()

    def clear_history(self, dialog):
        """清空历史记录"""
        reply = QMessageBox.question(
            self,
            "确认清空",
            "确定要清空所有历史记录吗？",
            QMessageBox.Yes | QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            if os.path.exists("task_history.json"):
                os.remove("task_history.json")
            print("🗑️ 已清空历史记录")
            dialog.close()
            self.view_launch_history()
    #
    # # ============ 汇率监控功能 ============
    #
    # def toggle_exchange_widget(self):
    #     """切换汇率组件显示/隐藏"""
    #     if hasattr(self, 'exchange_display'):
    #         self.exchange_display.toggle_widget()
    #
    # def toggle_time_widget(self):
    #     """切换报时组件显示/隐藏"""
    #     if hasattr(self, 'time_display'):
    #         self.time_display.toggle_widget()
    #
    # def show_theme_settings(self):
    #     """显示主题和汇率设置"""
    #     dlg = ThemeSettingsDialog(self.exchange_config, self)
    #
    #     if dlg.exec_() == QDialog.Accepted:
    #         # 重新加载主题
    #         self._reload_theme()
    #
    #         # 重启汇率监控
    #         self.exchange_fetcher.stop_monitoring()
    #         self._init_exchange_monitoring()
    #
    #         QMessageBox.information(self, "提示", "设置已保存！\n主题更改需要重启生效。")
    #
    # def _reload_theme(self):
    #     """重新加载主题"""
    #     if hasattr(self, 'exchange_display'):
    #         self.exchange_display.apply_theme()
    #
    #     if hasattr(self, 'time_display'):
    #         self.time_display.apply_theme()
    #
    # def on_exchange_rate_updated(self, rate_data):
    #     """汇率更新回调"""
    #     # 更新显示
    #     if hasattr(self, 'exchange_display'):
    #         self.exchange_display.update_rate(
    #             rate_data['currency_pair'],
    #             rate_data['rate'],
    #             rate_data['time'],
    #             rate_data.get('base'),
    #             rate_data.get('target')
    #         )
    #
    #     # 保存到数据库
    #     if hasattr(self, 'exchange_storage'):
    #         self.exchange_storage.save_rate(
    #             rate_data['currency_pair'],
    #             rate_data['base'],
    #             rate_data['target'],
    #             rate_data['rate'],
    #             rate_data['time']
    #         )
    #
    #     # 检查提醒
    #     if hasattr(self, 'exchange_alerter'):
    #         self.exchange_alerter.check_rate(
    #             rate_data['currency_pair'],
    #             rate_data['rate'],
    #             self
    #         )
    #
    #     # 每小时自动导出Excel
    #     if rate_data['time'].minute == 0:
    #         self.exchange_storage.auto_export_daily(rate_data['currency_pair'])
    #
    # def on_exchange_alert(self, alert_data):
    #     """汇率提醒触发"""
    #     QMessageBox.warning(
    #         self,
    #         "🔔 汇率提醒",
    #         alert_data['message']
    #     )
    #
    # def open_exchange_excel(self):
    #     """打开汇率Excel文件"""
    #     if hasattr(self, 'exchange_storage'):
    #         self.exchange_storage.open_excel()

    # ============ 其他功能 ============

    def set_collision_margin(self, margin):
        """设置碰撞边距 - ⭐ 现在会自动保存"""
        if hasattr(self, 'movement'):
            self.movement.collision_margin = margin
            # ⭐ 保存设置
            self.settings_manager.set_collision_margin(margin)
            print(f"碰撞边距已设置为: {margin}px（已保存）")

    def toggle_window_avoidance(self):
        """开关窗口避让功能 - ⭐ 现在会自动保存状态"""
        if hasattr(self, 'window_detector'):
            if self.window_detector.update_timer.isActive():
                # 关闭窗口避让
                self.window_detector.update_timer.stop()
                self.window_detector.active_window_rect = None
                self.settings_manager.set_window_avoidance(False)
                print("ℹ️ 窗口避让已关闭（已保存）")
            else:
                # 开启窗口避让
                self.window_detector.update_timer.start(500)
                self.settings_manager.set_window_avoidance(True)
                print("✅ 窗口避让已开启（已保存）")

    def hide_to_tray(self):
        """隐藏到托盘（从右键菜单调用）"""
        if hasattr(self, 'tray_manager'):
            self.hide()
            self.tray_manager.is_pet_visible = False
            self.tray_manager.toggle_action.setText("显示宠物")

            print("👻 宠物已隐藏到托盘")

    # ============ 番茄钟功能 ============

    def start_pomodoro(self):
        """启动番茄钟"""
        # 如果已经在运行，先停止
        if self.pomodoro_timer.is_running:
            reply = QMessageBox.question(
                self,
                "番茄钟运行中",
                "当前番茄钟正在运行，是否停止并重新设置？",
                QMessageBox.Yes | QMessageBox.No
            )
            if reply == QMessageBox.Yes:
                self.pomodoro_timer.stop_timer()
                self.pomodoro_display.hide()
            else:
                return

        # 打开设置对话框
        dlg = PomodoroSetupDialog(self)
        if dlg.exec_() == QDialog.Accepted:
            settings = dlg.get_settings()

            # 显示番茄钟界面
            self.pomodoro_display.show_timer(
                settings["work_minutes"],
                settings["break_minutes"],
                settings["rounds"]
            )

            # 启动计时器
            self.pomodoro_timer.start_timer(
                settings["work_minutes"],
                settings["break_minutes"],
                settings["rounds"],
                settings["is_repeat"]
            )

            print(f"🍅 番茄钟已启动: {settings}")

    def on_pomodoro_tick(self, remaining_seconds, is_break):
        """
        番茄钟每秒回调

        Args:
            remaining_seconds: 剩余秒数
            is_break: 是否休息中
        """
        self.pomodoro_display.update_countdown(
            remaining_seconds,
            is_break,
            self.pomodoro_timer.current_round
        )

    def on_pomodoro_round_changed(self, current_round, total_rounds):
        """
        轮数变化回调

        Args:
            current_round: 当前轮数
            total_rounds: 总轮数
        """
        print(f"🍅 番茄钟：第 {current_round}/{total_rounds} 轮")

    def on_pomodoro_complete(self):
        """番茄钟完成回调"""
        print("🎉 番茄钟工作时段完成！")

        # 显示完成消息
        self.pomodoro_display.show_completion()

        # 弹跳动画
        if hasattr(self, 'animation') and not self.animation.is_playing:
            self.animation.stretch_on_click()

        # 3秒后隐藏番茄钟显示（如果不是重复模式）
        if not self.pomodoro_timer.is_running:
            QTimer.singleShot(3000, self.pomodoro_display.hide)


    def open_music_player(self):
        """打开音乐播放器"""
        if hasattr(self, 'music_player'):
            dlg = MusicPlayerDialog(self.music_player, self)
            dlg.exec_()
        else:
            QMessageBox.warning(self, "错误", "音乐播放器未初始化")

    # ============ 汇率监控功能 ============

    # def toggle_exchange_widget(self):
    #     """切换汇率组件"""
    #     if hasattr(self, 'exchange_display'):
    #         self.exchange_display.toggle_widget()
    #
    # def toggle_time_widget(self):
    #     """切换报时组件"""
    #     if hasattr(self, 'time_display'):
    #         self.time_display.toggle_widget()
    #
    # def show_theme_settings(self):
    #     """显示主题设置"""
    #     dlg = ThemeSettingsDialog(self.exchange_config, self)
    #
    #     if dlg.exec_() == QDialog.Accepted:
    #         self._reload_theme()
    #         self.exchange_fetcher.stop_monitoring()
    #         self._init_exchange_monitoring()
    #         QMessageBox.information(self, "提示", "设置已保存！")
    #
    # def _reload_theme(self):
    #     """重新加载主题"""
    #     if hasattr(self, 'exchange_display'):
    #         self.exchange_display.apply_theme()
    #     if hasattr(self, 'time_display'):
    #         self.time_display.apply_theme()
    #
    # def on_exchange_rate_updated(self, rate_data):
    #     """汇率更新回调"""
    #     if hasattr(self, 'exchange_display'):
    #         self.exchange_display.update_rate(
    #             rate_data['currency_pair'],
    #             rate_data['rate'],
    #             rate_data['time']
    #         )
    #     if hasattr(self, 'exchange_storage'):
    #         self.exchange_storage.save_rate(
    #             rate_data['currency_pair'],
    #             rate_data['base'],
    #             rate_data['target'],
    #             rate_data['rate'],
    #             rate_data['time']
    #         )
    #     if hasattr(self, 'exchange_alerter'):
    #         self.exchange_alerter.check_rate(
    #             rate_data['currency_pair'],
    #             rate_data['rate'],
    #             self
    #         )
    #
    # def on_exchange_alert(self, alert_data):
    #     """汇率提醒"""
    #     QMessageBox.warning(self, "🔔 汇率提醒", alert_data['message'])

    def toggle_exchange_widget(self):
        """切换汇率显示"""
        if self.exchange_display.is_visible:
            self.exchange_display.hide_widget()
            self.exchange_config.set_widget_visible(False)
        else:
            self.exchange_display.show_widget()
            self.exchange_config.set_widget_visible(True)
            self._init_exchange_monitoring()

    def on_exchange_rate_updated(self, rate_data):
        """汇率更新回调"""
        # 更新显示
        self.exchange_display.update_rate(
            rate_data['currency_pair'],
            rate_data['rate'],
            rate_data['time'],
            rate_data.get('base'),
            rate_data.get('target')
        )

        # 保存到数据库
        self.exchange_storage.save_rate(
            rate_data['currency_pair'],
            rate_data['base'],
            rate_data['target'],
            rate_data['rate'],
            rate_data['time']
        )

        # 检查提醒
        self.exchange_alerter.check_rate(
            rate_data['currency_pair'],
            rate_data['rate'],
            self
        )

    def on_exchange_alert(self, alert_data):
        """汇率提醒触发"""
        # 显示提醒消息
        QMessageBox.information(
            self,
            "汇率提醒",
            alert_data['message']
        )

    # 添加对应方法
    def show_exchange_widget(self):
        """显示汇率组件并开始监控"""
        self.exchange_display.show_widget()
        self.exchange_config.set_widget_visible(True)
        self._init_exchange_monitoring()

    def run_debug_test(self):
        """运行调试测试"""
        # 获取当前监控的货币对
        currencies = self.exchange_config.get_enabled_currencies()

        if not currencies:
            QMessageBox.warning(self, "提示", "请先添加要监控的币种")
            return

        # 使用第一个币种进行测试
        currency = currencies[0]
        currency_pair = f"{currency['target']}/{currency['base']}"

        # 显示测试对话框
        reply = QMessageBox.question(
            self,
            "🧪 调试测试",
            f"即将测试 {currency_pair} 的提醒功能：\n\n"
            f"1. 插入异常汇率值（100.0）\n"
            f"2. 立即抓取当前真实汇率\n"
            f"3. 检查提醒是否触发\n\n"
            f"确定要继续吗？",
            QMessageBox.Yes | QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            self.exchange_debugger.test_alert(currency_pair, self)

            # 无声提示（用普通 QDialog 代替 QMessageBox.information）
            from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton
            dlg = QDialog(self)
            dlg.setWindowTitle("测试完成")
            dlg.setMinimumSize(320, 180)
            layout = QVBoxLayout(dlg)
            layout.setContentsMargins(15, 15, 15, 15)
            layout.setSpacing(10)
            lbl = QLabel(
                "测试已完成！\n\n"
                "请检查：\n"
                "1. 是否有提醒弹窗\n"
                "2. 宠物是否有跳动动画\n"
                "3. 是否有 alert.mp3 提示音\n\n"
                "详细信息请查看终端输出。"
            )
            lbl.setWordWrap(True)
            layout.addWidget(lbl)
            btn = QPushButton("确定")
            btn.setFixedHeight(32)
            btn.clicked.connect(dlg.accept)
            layout.addWidget(btn)
            dlg.exec_()

    # ========== 报时组件控制 ==========

    def toggle_time_widget(self):
        """切换报时组件显示/隐藏"""
        if hasattr(self, 'time_display'):
            self.time_display.toggle_widget()

    def show_time_widget(self):
        """显示报时组件"""
        if hasattr(self, 'time_display'):
            self.time_display.show_widget()

    def hide_time_widget(self):
        """隐藏报时组件"""
        if hasattr(self, 'time_display'):
            self.time_display.hide_widget()

    # ============ 重启功能 ============

    def restart_application(self):
        """重启应用程序"""
        reply = QMessageBox.question(
            self,
            "确认重启",
            "确定要重启桌面宠物吗？\n\n当前播放的音乐会停止。",
            QMessageBox.Yes | QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            print("🔄 正在重启应用...")

            # 停止音乐播放
            if hasattr(self, 'music_player'):
                self.music_player.stop()

            # 清理资源
            try:
                if HAS_KEYBOARD:
                    import keyboard
                    keyboard.unhook_all()
            except:
                pass

            # 重启
            QApplication.quit()
            python = sys.executable
            os.execl(python, python, *sys.argv)

    def closeEvent(self, event):
        """彻底杀掉进程，解决终端无响应"""
        print("程序关闭中...")
        try:
            if HAS_KEYBOARD:
                import keyboard
                keyboard.unhook_all()
        except:
            pass
        # 强制退出所有线程
        import os
        os._exit(0)

def main():
    app = QApplication(sys.argv)
    pet = DesktopPet()
    pet.show()

    exit_code = app.exec_()

    if HAS_KEYBOARD:
        try:
            keyboard.unhook_all()
            print("✅ 已清理全局快捷键")
        except:
            pass

    sys.exit(exit_code)


if __name__ == "__main__":
    main()