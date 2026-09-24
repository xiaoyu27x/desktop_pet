"""
系统托盘管理模块
文件名: tray_manager.py
位置: 项目根目录
"""

from PyQt5.QtWidgets import QSystemTrayIcon, QMenu, QAction
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt
import os


class TrayManager:
    """系统托盘管理器"""

    def __init__(self, parent):
        """
        初始化托盘管理器

        Args:
            parent: 主窗口实例（DesktopPet）
        """
        self.parent = parent
        self.tray_icon = None
        self.is_pet_visible = True  # 宠物是否可见

    def create_tray_icon(self):
        """创建托盘图标"""
        # 创建托盘图标对象
        self.tray_icon = QSystemTrayIcon(self.parent)

        # 加载图标
        icon = self._load_icon()
        self.tray_icon.setIcon(icon)

        # 设置提示文字（鼠标悬停显示）
        self.tray_icon.setToolTip("桌面宠物 v3.2\n双击显示/隐藏")

        # 创建右键菜单
        menu = self._create_menu()
        self.tray_icon.setContextMenu(menu)

        # 连接信号：双击托盘图标
        self.tray_icon.activated.connect(self._on_tray_activated)

        # 显示托盘图标
        self.tray_icon.show()

        print("✅ 系统托盘图标已创建")

    def _load_icon(self):
        """加载托盘图标"""
        # 优先从加密包读取
        try:
            from resource_loader import res
            from PyQt5.QtGui import QPixmap
            icon_keys = [
                "resources/icons/tray_icon.ico",
                "resources/icons/tray_icon.png",
                "resources/pet.png",
            ]
            for key in icon_keys:
                try:
                    pixmap = res.qpixmap(key)
                    if not pixmap.isNull():
                        print(f"📁 使用托盘图标: {key}")
                        return QIcon(pixmap)
                except Exception:
                    continue
        except ImportError:
            pass

        # 回退：文件系统
        icon_paths = [
            "resources/icons/tray_icon.ico",
            "resources/icons/tray_icon.png",
            "pet.png",
        ]
        for path in icon_paths:
            if os.path.exists(path):
                print(f"📁 使用托盘图标（文件系统）: {path}")
                return QIcon(path)

        print("⚠️ 未找到图标文件，使用默认图标")
        return QIcon()

    def _create_menu(self):
        """
        创建托盘右键菜单

        Returns:
            QMenu: 菜单对象
        """
        menu = QMenu()

        # 音乐播放器
        self.music_action = QAction("音乐播放器", self.parent)
        self.music_action.triggered.connect(self.parent.open_music_player)
        menu.addAction(self.music_action)

        menu.addSeparator()

        # === 显示/隐藏 ===
        self.toggle_action = QAction("隐藏宠物", menu)
        self.toggle_action.triggered.connect(self._toggle_visibility)
        menu.addAction(self.toggle_action)

        menu.addSeparator()

        # 重启
        self.restart_action = QAction("重启", self.parent)
        self.restart_action.triggered.connect(self.parent.restart_application)
        menu.addAction(self.restart_action)

        menu.addSeparator()

        # === 退出 ===
        quit_action = QAction("退出程序", menu)
        quit_action.triggered.connect(self._quit_app)
        menu.addAction(quit_action)

        return menu

    def _on_tray_activated(self, reason):
        """
        托盘图标点击事件

        Args:
            reason: 点击类型
                - Trigger: 单击
                - DoubleClick: 双击
                - MiddleClick: 中键点击
        """
        # 双击显示/隐藏宠物
        if reason == QSystemTrayIcon.DoubleClick:
            self._toggle_visibility()

    def _toggle_visibility(self):
        """切换宠物显示/隐藏"""
        if self.is_pet_visible:
            # 隐藏宠物
            self.parent.hide()
            self.is_pet_visible = False
            self.toggle_action.setText("显示宠物")
            print("👻 宠物已隐藏")

            # # 显示气泡提示
            # self.tray_icon.showMessage(
            #     "桌面宠物",
            #     "宠物已隐藏到托盘\n双击托盘图标可重新显示",
            #     QSystemTrayIcon.Information,
            #     2000  # 显示2秒
            # )
        else:
            # 显示宠物
            self.parent.show()
            self.is_pet_visible = True
            self.toggle_action.setText("隐藏宠物")
            print("👀 宠物已显示")

    def _quit_app(self):
        """退出程序"""
        print("👋 退出程序...")

        # 清理托盘图标
        if self.tray_icon:
            self.tray_icon.hide()

        # 退出主程序
        self.parent.close()

        # 强制退出所有线程
        import os
        os._exit(0)

    def show_message(self, title, message, duration=3000):
        """
        显示托盘气泡提示

        Args:
            title: 标题
            message: 消息内容
            duration: 显示时长（毫秒）
        """
        if self.tray_icon:
            self.tray_icon.showMessage(
                title,
                message,
                QSystemTrayIcon.Information,
                duration
            )

    def update_tooltip(self, text):
        """
        更新托盘图标提示文字

        Args:
            text: 新的提示文字
        """
        if self.tray_icon:
            self.tray_icon.setToolTip(text)